import sys
import typing

from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QBrush, QClipboard, QColor, QMouseEvent, QPainter, QPen

from MapData import MapCell, MapData, MapDataElement
from PyQt5.QtWidgets import QMenu

from Common import TR


class Selection:
    Add = 1
    Clear = 2
    
    class Block:
        def __init__(self, data: MapDataElement) -> None:
            self.datax, self.datay = data.x, data.y
            self.data = data
            
    def __init__(self, parent) -> None:
        self.parent = parent
        self.labels: typing.List[Selection.Block] = []
        self.dedup = {}
        
    def paint(self, p: QPainter):
        d: DragController = self.parent.dragger
        dd = d.dragtonorm - d.startnorm
        x, y = dd.x(), dd.y()
        bs = self.parent._blocksize()
        for l in self.labels:
            el: MapDataElement = l.data
            posx = l.data.x * bs + self.parent.viewOrigin[0]
            posy = l.data.y * bs + self.parent.viewOrigin[1]
            MapCell._paintRect(el, posx, posy, bs, bs, p)
            if x or y: # paint select-n-drag blocks if presented
                MapCell._paint(el, posx + x, posy + y, bs, bs, p, ghost=True)
        
    def addSelection(self, data: MapDataElement, propertyPanel = True):
        if not data:
            return False
        if not data.src:
            return False
        if id(data) in self.dedup:
            return False
        label = Selection.Block(data)
        self.labels.append(label)
        self.dedup[id(data)] = label
        self.parent.selectionEvent(Selection.Add, data)
        if propertyPanel:
            self.parent.findMainWin().propertyPanel.update()
        return True

    def addRowCol(self, data: MapData, add, x=sys.maxsize, y=sys.maxsize):
        if not add:
            self.clear()
        for dx, dy in data.data:
            if dy == y or dx == x:
                self.addSelection(data.data[(dx, dy)], False)
        self.parent.findMainWin().propertyPanel.update()
        
    def delSelection(self, data: MapDataElement):
        if not id(data) in self.dedup:
            return 
        x = self.dedup[id(data)]
        del self.dedup[id(data)]
        self.labels.remove(x)
        self.parent.findMainWin().propertyPanel.update()
        
    def moveEnd(self, dx, dy):
        self.parent.data.begin()
        d: MapData = self.parent.data
        for l in self.labels:
            d.delete(l.datax, l.datay)
        for l in self.labels:
            d.put(l.datax + dx, l.datay + dy, l.data)
        self.clear()
            
    def clear(self):
        self.labels = self.labels[:0]
        self.dedup = {}
        self.parent.selectionEvent(Selection.Clear, None)
        self.parent.findMainWin().propertyPanel.update()
        
    def status(self):
        return "{}".format(len(self.labels))

class HoverController:
    def __init__(self, parent) -> None:
        self.parent = parent
        self.labels: typing.List[MapDataElement] = []
        
    def clear(self):
        self.labels = self.labels[:0]
        
    def hold(self, data: typing.List[MapDataElement]):
        self.labels = data
        
    def paint(self, p: QPainter):
        d: DragController = self.parent.dragger
        bs = self.parent._blocksize()
        x, y = d.dragtonorm.x(), d.dragtonorm.y()
        for l in self.labels:
            el: MapDataElement = l
            xx, yy = (l.x - self.labels[0].x) * bs + x, (l.y - self.labels[0].y) * bs + y
            MapCell._paint(el, xx, yy, bs, bs, p, ghost=True)
    
    def end(self, cascade):
        if len(self.labels) == 0:
            return
        d: MapData = self.parent.data
        d.begin()

        dd: DragController = self.parent.dragger
        d1, cell, _ = dd.parent.findCellUnder(None, QtCore.QPoint(dd.dragtox, dd.dragtoy))
        cell: MapCell
        
        if cascade and cell and d1 and len(self.labels) == 1:
            old = cell.current.pack()
            cell.current.cascades.append(self.labels[0].src)
            d._appendHistoryPacked(old, cell.current.pack())
        elif d1:
            x, y = self.labels[0].x, self.labels[0].y
            for l in self.labels:
                d.put(l.x - x + d1.x, l.y - y + d1.y, l)

        self.clear()

class DragController:
    Size = 12
    pen = QPen(QColor(100, 120, 120))
    pen.setWidth(3)

    def __init__(self, parent) -> None:
        self.parent = parent
        self.reset()
        
    def reset(self):
        self.startx = 0
        self.starty = 0
        self.dragtox = 0
        self.dragtoy = 0
        self.dragtonorm = self.startnorm = QtCore.QPoint(0, 0)
        self.started = False
        self.visible = True
    
    def start(self, x: int, y: int, normalized: QtCore.QPoint):
        self.startx = self.dragtox = x
        self.starty = self.dragtoy = y
        self.startnorm = self.dragtonorm = normalized
        self.started = True
        
    def drag(self, x: int, y: int, normalized: QtCore.QPoint):
        self.dragtox = x
        self.dragtoy = y
        self.dragtonorm = normalized 
        
    def end(self):
        if not self.started:
            return 0, 0

        d0, _, _ = self.parent.findCellUnder(None, QtCore.QPoint(self.startx, self.starty))
        d1, _, _ = self.parent.findCellUnder(None, QtCore.QPoint(self.dragtox, self.dragtoy))

        self.reset()
        if d0 and d1:
            return d1.x - d0.x, d1.y - d0.y
        return 0, 0
        
    def paint(self, p: QPainter):
        if not self.started:
            return
        if not self.visible:
            return
        if self.dragtonorm == self.startnorm:
            return
        DragController._paint(self.startx, self.starty, self.dragtox, self.dragtoy, p)
        
    def _paint(startx, starty, dragtox, dragtoy, p: QPainter):
        p.save()
        p.setPen(DragController.pen)
        p.drawLine(startx, starty, dragtox, dragtoy)

        p.setPen(QPen(QColor(0,0,0,0)))
        p.setBrush(QColor(100, 120, 120, 128))
        offset = 4
        size = DragController.Size + offset
        p.drawEllipse(startx - size / 2, starty - size / 2, size, size)
        p.drawEllipse(dragtox - size / 2, dragtoy - size / 2, size, size)

        p.setBrush(QColor(100, 120, 120))
        p.drawEllipse(startx - DragController.Size / 2, starty - DragController.Size / 2, DragController.Size, DragController.Size)
        p.drawEllipse(dragtox - DragController.Size / 2, dragtoy - DragController.Size / 2, DragController.Size, DragController.Size)
        p.restore()

class Ruler:
    Width = 20
    Background = QColor(255, 255, 255)
    Cursor = QColor(200, 200, 200)
    Corner = QBrush(QColor(0, 0, 0), QtCore.Qt.BrushStyle.BDiagPattern)
    HVPen = QPen(QColor(190, 190, 190), 1, QtCore.Qt.PenStyle.DashLine)

    def __init__(self, parent) -> None:
        self.parent = parent
        self.currentXY = (sys.maxsize, sys.maxsize)
        self.hlines = set()
        self.vlines = set()

    def mousePress(self, a0: QMouseEvent) -> bool:
        d, _, _ = self.parent.findCellUnder(a0)
        if not d:
            return False
        if a0.buttons() & QtCore.Qt.MouseButton.LeftButton:
            if a0.x() < Ruler.Width: # quick row selection
                self.parent.selector.addRowCol(self.parent.data, a0.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier, y=d.y)
                return True
            if a0.y() < Ruler.Width: # quick column selection
                self.parent.selector.addRowCol(self.parent.data, a0.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier, x=d.x)
                return True
        if a0.buttons() & QtCore.Qt.MouseButton.RightButton:
            if not (a0.x() < Ruler.Width or a0.y() < Ruler.Width):
                return False
            m = QMenu(self.parent)
            if a0.x() < Ruler.Width: # add hline
                if d.y in self.hlines:
                    a = m.addAction(TR('Remove Line'))
                    a.triggered.connect(lambda v: self.hlines.remove(d.y))
                else:
                    a = m.addAction(TR('Add Line'))
                    a.triggered.connect(lambda v: self.hlines.add(d.y))
            else:
                if d.x in self.vlines:
                    a = m.addAction(TR('Remove Line'))
                    a.triggered.connect(lambda v: self.vlines.remove(d.x))
                else:
                    a = m.addAction(TR('Add Line'))
                    a.triggered.connect(lambda v: self.vlines.add(d.x))
            m.popup(self.parent.mapToGlobal(a0.pos()))
            return True
        return False

    def _drawLine(self, x, y, h, p: QPainter):
        p.save()
        p.setPen(Ruler.HVPen)
        if h:
            p.drawLine(x, y, x + self.parent.width(), y)
        else:
            p.drawLine(x, y, x, y + self.parent.height())
        p.restore()

    def paint(self, p: QPainter):
        # hack
        old = self
        self = self.parent

        blockSize = self._blocksize()
        width = Ruler.Width
        xx = int(self.viewOrigin[0] / blockSize) * blockSize
        yy = int(self.viewOrigin[1] / blockSize) * blockSize
        sx, sy = self.deltaxy()
        smallstep = blockSize if blockSize > width * 5 else width * 5 // blockSize * blockSize + blockSize
        optX = QtCore.Qt.AlignmentFlag.AlignVCenter | QtCore.Qt.AlignmentFlag.AlignLeft
        optY = QtCore.Qt.AlignmentFlag.AlignVCenter | QtCore.Qt.AlignmentFlag.AlignRight

        p.save()
        p.setFont(QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.SystemFont.FixedFont))

        p.fillRect(0, 0, width, self.height(), Ruler.Background)
        for y in range(0, self.height() + blockSize, blockSize):
            iy = int((y - yy) / blockSize)
            if iy == old.currentXY[1]:
                p.fillRect(0, y + sy, width, blockSize, Ruler.Cursor)
            if iy in old.hlines:
                old._drawLine(0, y + sy + blockSize / 2, True, p)

            if (y - yy) % smallstep != 0:
                p.drawLine(0, y + sy, width / 4, y + sy)
                continue
            y = y + sy
            p.drawLine(0, y, width, y)
            p.translate(0, y + smallstep)
            p.rotate(-90)
            p.drawText(QtCore.QRect(0, 0, smallstep - 1, width), optY, str(iy))
            p.resetTransform()
        p.drawLine(width, 0, width, self.height())

        p.fillRect(0, 0, self.width(), width, Ruler.Background)
        for x in range(0, self.width() + blockSize, blockSize):
            # x + sx: on-canvas x coord
            if x + sx < width:
                continue
            ix = int((x - xx) / blockSize)
            if ix == old.currentXY[0]:
                p.fillRect(x + sx, 0, blockSize, width, Ruler.Cursor)
            if ix in old.vlines:
                old._drawLine(x + sx + blockSize / 2, 0, False, p)

            if (x - xx) % smallstep != 0:
                p.drawLine(x + sx, 0, x + sx, width / 4)
                continue
            x = x + sx
            p.drawLine(x, 0, x, width)
            p.drawText(QtCore.QRect(x + 1, 0, smallstep, width), optX, str(ix))
        p.drawLine(width, width, self.width(), width)

        p.drawLine(width, 0, width, width)
        p.drawLine(0, width, width, width)
        p.fillRect(0, 0, width, width, Ruler.Corner)

        p.drawRect(0, 0, self.width(), self.height())

        p.restore()

    def todict(self):
        return [list(self.hlines), list(self.vlines)]

    def fromdict(self, d):
        if not isinstance(d, list) or len(d) != 2:
            return
        self.hlines = set(d[0])
        self.vlines = set(d[1])