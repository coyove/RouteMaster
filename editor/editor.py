from typing import ValuesView
from SvgList import SvgList
import math
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QStatusBar, QLabel, QSplitter, qDrawBorderPixmap
import PyQt5.QtSvg as QtSvg
import PyQt5.QtGui as QtGui
from PyQt5 import QtCore
import random
from MapData import MapData, MapCell, SvgSource
from Selection import DragController, HoverController, Selection

def mod(x, y):
    return x - int(x/y) * y

class Map(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.data = MapData()
        self.scale = 2

        sources = []
        for i in range(0, 10):
            sources.append(SvgSource(self, "id" + str(i), """
                <svg height="48" width="48">
                    <text x="8" y="24" fill="red">{}</text>
                    <rect x="8" y="8" width="32" height="32" fill="transparent" stroke="#000"></rect>
                </svg>""".format(i).encode('utf-8')))
            
        for i in range(0, 1000):
            l = int(random.random() * 15 + 10)
            d = random.random() * math.pi * 2
            x, y = int(l * math.cos(d)), int(l * math.sin(d))
            self.data._put(x, y, MapData.Element(sources[random.randrange(0, len(sources))]))

        self.selector = Selection(self)
        self.dragger = DragController(self)
        self.hover = HoverController(self)
        self.svgBoxes = []
        self.svgBoxesRecycle = []
        self.currentData: MapData.Element = None
        self.viewOrigin = [0, 0]
        self.pan(0, 0) # fill svgBoxes
        self.setMouseTracking(True)
        self.pressPos = None
        self.pressHoldSel = False
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)
        
    def cacheSvgBoxLocked(self, cell):
        self.svgBoxesRecycle.append(cell)

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        self.pan(0, 0)
        return super().resizeEvent(a0)
    
    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.RenderHint.HighQualityAntialiasing)
        p.fillRect(0, 0, self.width(), self.height(), QtGui.QColor(255, 255, 255))
        for row in self.svgBoxes:
            for cell in row:
                if cell:
                    cell.paint(p)
        self.selector.paint(p)
        self.dragger.paint(p)
        self.hover.paint(p)
        p.end()
        return super().paintEvent(a0)
    
    def deltaxy(self): 
        blockSize = int(MapCell.Base * self.scale)
        sx = mod(self.viewOrigin[0], blockSize)
        sy = mod(self.viewOrigin[1], blockSize)
        return sx, sy
    
    def pan(self, dx, dy):
        blockSize = MapCell.Base * self.scale
        offsetX = self.viewOrigin[0] = self.viewOrigin[0] + dx
        offsetY = self.viewOrigin[1] = self.viewOrigin[1] + dy

        self.selector.moveIncr(dx, dy, blockSize)

        rows = int(self.height() / blockSize) + 3
        cols = int(self.width() / blockSize) + 3
        for r in self.svgBoxes:
            while len(r) < cols:
                r.append(None)
        while len(self.svgBoxes) < rows:
            self.svgBoxes.append([None for x in range(cols)])
            
        for i in range(rows, len(self.svgBoxes)):
            for cell in self.svgBoxes[i]:
                if cell:
                    self.cacheSvgBoxLocked(cell)
        self.svgBoxes = self.svgBoxes[:rows]

        for r in self.svgBoxes:
            for i in range(cols, len(r)):
                if r[i]:
                    self.cacheSvgBoxLocked(r[i])
            r[cols:] = []
            
        sx, sy = self.deltaxy()

        for y in range(len(self.svgBoxes)):
            for x in range(len(self.svgBoxes[y])):
                tmp = self.data.get(x - int(offsetX / blockSize), y - int(offsetY / blockSize))
                cell: MapCell = self.svgBoxes[y][x]
                if (tmp == None or not tmp.valid()) and cell:
                    self.svgBoxes[y][x] = None
                    self.cacheSvgBoxLocked(cell)

        for y in range(len(self.svgBoxes)):
            for x in range(len(self.svgBoxes[y])):
                tmp = self.data.get(x - int(offsetX / blockSize), y - int(offsetY / blockSize))
                cell: MapCell = self.svgBoxes[y][x]
                if tmp and tmp.valid():
                    cell = cell or self._newSvg()
                    self.svgBoxes[y][x] = cell
                    cell.loadResizeMove(tmp, self.scale, x * int(blockSize) + sx - blockSize, y * int(blockSize) + sy - blockSize)
                
        self.findMainWin().barPosition.setText( 'x:{}({}) y:{}({})'.format(
            -offsetX, -int(offsetX / blockSize), offsetY, int(offsetY / blockSize)))
        
        self.selectionEvent()
        self.repaint()
        
    def findCellUnder(self, a0: QtGui.QMouseEvent, c: QtCore.QPoint = None):
        c = a0 and a0.pos() or c
        blockSize = int(MapCell.Base * self.scale)
        x_ = ((c.x() - self.viewOrigin[0]) / blockSize)
        y_ = ((c.y() - self.viewOrigin[1]) / blockSize)
        x, y = math.ceil(x_), math.ceil(y_)
        if x_ == x or y_ == y:
            return None, None, None

        d = self.data.get(x, y) or MapData.Element(x = x, y = y)

        sx, sy = self.deltaxy()
        ix = math.ceil((c.x() - sx) / blockSize) 
        iy = math.ceil((c.y() - sy) / blockSize)
        x2 = int((c.x() - sx) / blockSize) * blockSize + sx
        y2 = int((c.y() - sy) / blockSize) * blockSize + sy
        if iy >= len(self.svgBoxes) or ix >= len(self.svgBoxes[iy]):
            return None, None, None
        
        cell = self.svgBoxes[iy][ix]
        # print(d.id, x2, y2)
        return d, cell, QtCore.QPoint(x2, y2)
    
    def findMainWin(self):
        p = self.parent()
        while not isinstance(p, QMainWindow):
            p = p.parent()
        return p
    
    def selectionEvent(self, action=None, d=None):
        # print(d)
        self.findMainWin().barSelection.setText(self.selector.status())
        
    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        delete = a0.key() == QtCore.Qt.Key.Key_Delete
        ctrl = QtGui.QGuiApplication.keyboardModifiers() & QtCore.Qt.KeyboardModifier.ControlModifier 
          
        if ctrl and (a0.key() == QtCore.Qt.Key.Key_C or a0.key() == QtCore.Qt.Key.Key_X):
            delete = a0.key() == QtCore.Qt.Key.Key_X
            s = []
            for l in self.selector.labels:
                s.append(l.data.pack())
            QtGui.QGuiApplication.clipboard().setText("{}".join(s))
            
        if delete:
            self.data.begin()
            for l in self.selector.labels:
                self.data.delete(l.data.x, l.data.y)
            self.selector.clear()
            self.pan(0, 0)
            
        if ctrl and a0.key() == QtCore.Qt.Key.Key_V and len(self.selector.labels) == 1:
            l = self.selector.labels[0]
            x, y = l.data.x, l.data.y
            c = []
            for s in QtGui.QGuiApplication.clipboard().text().split('{}'):
                d = MapData.Element.unpack(s)
                if d:
                    c.append(d)
            if len(c):
                self.data.begin()
                leadx, leady = c[0].x, c[0].y
                for el in c:
                    el: MapData.Element
                    self.data.put(el.x - leadx + x, el.y - leady + y, el)
                self.selector.clear()
                self.pan(0, 0)
                
        if ctrl and a0.key() == QtCore.Qt.Key.Key_Z:
            self.data.rewind()
            self.selector.clear()
            self.pan(0, 0)

        return super().keyPressEvent(a0)
    
    def _toggleSvgBoxesMoving(self, v):
        for row in self.svgBoxes:
            for c in row:
                if c:
                    c.moving = v
        for c in self.svgBoxesRecycle:
            c.moving = v
        

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        d, cell, pt = self.findCellUnder(a0)
        cell: MapCell
        if a0.buttons() & QtCore.Qt.MouseButton.MidButton:
            self.pressPos = a0.pos()
            QApplication.setOverrideCursor(QtCore.Qt.CursorShape.DragMoveCursor)
            if len(self.svgBoxes) * len(self.svgBoxes[0]) > 1600:
                self._toggleSvgBoxesMoving(True)
            self.currentData = d
        else:
            self.pressPos = None
            self.pressHoldSel = True
            if d:
                if a0.buttons() & QtCore.Qt.MouseButton.RightButton:
                    self.selector.addSelection(d, pt, int(MapCell.Base * self.scale))
                    self.dragger.start(a0.x(), a0.y(), pt)
                else:
                    if a0.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier:
                        self.selector.addSelection(d, pt, int(MapCell.Base * self.scale))
                    elif a0.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier:
                        self.selector.delSelection(d)
                    else:
                        self.selector.clear()
                        self.selector.addSelection(d, pt, int(MapCell.Base * self.scale))

        self.repaint()
        return super().mousePressEvent(a0)           

    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:
        if isinstance(self.pressPos, QtCore.QPoint):
            diff: QtCore.QPoint = a0.pos() - self.pressPos
            self.pressPos = a0.pos()
            self.pan(diff.x(), diff.y())
        elif self.pressHoldSel:
            d, cell, pt = self.findCellUnder(a0)
            cell: MapCell
            if d:
                if a0.buttons() & QtCore.Qt.MouseButton.RightButton:
                    # self.hover.pt = pt or self.hover.pt
                    # self.hover.size = int(self.scale * MapCell.Base)
                    self.dragger.drag(a0.x(), a0.y(), pt)
                else:
                    if a0.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier:
                        self.selector.addSelection(d, pt, int(MapCell.Base * self.scale))
                    elif a0.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier:
                        self.selector.delSelection(d)
            self.repaint()
        return super().mouseMoveEvent(a0)
    
    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.pressPos = None
        self.pressHoldSel = False
        # self.hover.size = 0
        
        dx, dy = self.dragger.end(int(MapCell.Base * self.scale))
        if dx != 0 or dy != 0:
            self.selector.move(dx, dy)

        QApplication.restoreOverrideCursor()
        self._toggleSvgBoxesMoving(False)

        self.pan(0, 0)
        return super().mouseReleaseEvent(a0)
    
    def wheelEvent(self, a0: QtGui.QWheelEvent) -> None:
        lastScale = self.scale
        if a0.angleDelta().y() > 0:
            self.scale = min(self.scale * 2, 32)
        else:   
            self.scale = max(self.scale / 2, 0.5)
            
        c = a0.pos()
        self.viewOrigin[0] = int((self.viewOrigin[0] - c.x()) * self.scale / lastScale + c.x())
        self.viewOrigin[1] = int((self.viewOrigin[1] - c.y()) * self.scale / lastScale + c.y())
        self.selector.moveZoom(c.x(), c.y(), self.scale / lastScale)
        self.pan(0, 0)
        return super().wheelEvent(a0)
    
    def _newSvg(self):
        if len(self.svgBoxesRecycle) > 0:
            cell: MapCell = self.svgBoxesRecycle[-1]
            self.svgBoxesRecycle = self.svgBoxesRecycle[:-1]
            return cell
        s = MapCell(self)
        return s
    
class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("RouteMaster")
  
        self.setGeometry(0, 0, 500, 500)

        bar = QStatusBar(self)
        self.barPosition = QLabel(bar)
        bar.addWidget(self.barPosition, 1)
        self.barSelection = QLabel(bar)
        bar.addWidget(self.barSelection, 1)
        self.setStatusBar(bar)

        main = QWidget(self)
        vbox = QVBoxLayout()
        main.setLayout(vbox)
        vbox.setContentsMargins(0,0,0,0)
        self.setCentralWidget(main)
        
        splitter = QSplitter(QtCore.Qt.Orientation.Horizontal)
        lv = SvgList(self, "block")
        splitter.addWidget(lv)
        map = Map(main)
        splitter.addWidget(map)
        splitter.setStretchFactor(1, 2)
        splitter.setSizes([100, 100])
        vbox.addWidget(splitter)

        self.show()

app = QApplication([])
win = Window()
app.exec_()
