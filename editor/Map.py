import json
import math
import random
import sys
import typing
from json.decoder import JSONDecodeError

import PyQt5.QtGui as QtGui
from PyQt5 import QtCore
from PyQt5.QtWidgets import (QApplication, QInputDialog, QLineEdit,
                             QMainWindow, QMessageBox, QWidget, qApp)

from Common import BS, TR
from Controller import DragController, HoverController, Selection
from MapData import MapCell, MapData, MapDataElement
from Parser import parseBS
from Svg import SvgSource


def mod(x, y):
    return x - int(x/y) * y

class Map(QWidget):
    import functools

    @functools.cache
    def BigFont():
        return QtGui.QFont(QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.SystemFont.FixedFont).family(), 16)

    def __init__(self, parent, sources):
        super().__init__(parent)
        
        self.data = MapData(self)
        self.scale = 2

        sources = sources or []
        for i in range(0, 10):
            sources.append(SvgSource("id" + str(i), """
                <svg height="48" width="48">
                    <text x="8" y="24" fill="red">{}</text>
                    <rect x="8" y="8" width="32" height="32" fill="transparent" stroke="#000"></rect>
                </svg>""".format(i).encode('utf-8')))
            sources[i].overrideSize(32, 32)
            
        for i in range(0, 0):
            l = int(random.random() * 15 + 10)
            d = random.random() * math.pi * 2
            x, y = int(l * math.cos(d)), int(l * math.sin(d))
            el = MapDataElement(sources[random.randrange(0, len(sources))])
            if random.random() > 0.9:
                el.cascades.append(sources[random.randrange(0, len(sources))])
            if random.random() > 0.8:
                el.text = "lazy\nfox jumps"
            self.data._put(x, y, el)

        self.selector = Selection(self)
        self.dragger = DragController(self)
        self.hover = HoverController(self)
        self.svgBoxes = []
        self.svgBoxesRecycle = []
        self.currentData: MapDataElement = None
        self.viewOrigin = [0, 0]
        self.pan(0, 0) # fill svgBoxes
        self.setMouseTracking(True)
        self.pressPos = None
        self.pressPosPath = []
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
                cell and cell.paint(p)
        self.selector.paint(p)
        self.dragger.paint(p)
        self.hover.paint(p)
        for i in range(0, len(self.pressPosPath)):
            s, e = self.pressPosPath[i], self.pressPosPath[i < len(self.pressPosPath) - 1 and i + 1 or 0]
            p.drawLine(s[0], s[1], e[0], e[1])

        vis = []
        QApplication.queryKeyboardModifiers() & QtCore.Qt.KeyboardModifier.ControlModifier and vis.append('\u2318' if sys.platform == 'darwin' else 'Ctrl')
        QApplication.queryKeyboardModifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier and vis.append("Shift")
        QApplication.mouseButtons() & QtCore.Qt.MouseButton.LeftButton and vis.append("^L")
        QApplication.mouseButtons() & QtCore.Qt.MouseButton.MidButton and vis.append("^M")
        QApplication.mouseButtons() & QtCore.Qt.MouseButton.RightButton and vis.append("^R")
        if vis:
            p.setFont(Map.BigFont())
            p.drawText(0, Map.BigFont().pointSize(), '-'.join(vis))

        p.end()
        return super().paintEvent(a0)
    
    def deltaxy(self): 
        blockSize = int(BS * self.scale)
        sx = mod(self.viewOrigin[0], blockSize)
        sy = mod(self.viewOrigin[1], blockSize)
        return sx, sy
    
    def pan(self, dx, dy):
        blockSize = BS * self.scale
        offsetX = self.viewOrigin[0] = self.viewOrigin[0] + dx
        offsetY = self.viewOrigin[1] = self.viewOrigin[1] + dy

        rows = int(self.height() / blockSize) + 3
        cols = int(self.width() / blockSize) + 3
        for r in self.svgBoxes:
            while len(r) < cols:
                r.append(None)
        while len(self.svgBoxes) < rows:
            self.svgBoxes.append([None for x in range(cols)])
            
        for i in range(rows, len(self.svgBoxes)):
            for cell in self.svgBoxes[i]:
                cell and self.cacheSvgBoxLocked(cell)
        self.svgBoxes = self.svgBoxes[:rows]

        for r in self.svgBoxes:
            for i in range(cols, len(r)):
                r[i] and self.cacheSvgBoxLocked(r[i])
            r[cols:] = []
            
        sx, sy = self.deltaxy()

        for y in range(len(self.svgBoxes)):
            for x in range(len(self.svgBoxes[y])):
                tmp = self.data.get(x - int(offsetX / blockSize) - 1, y - int(offsetY / blockSize) - 1)
                cell: MapCell = self.svgBoxes[y][x]
                if (tmp == None or not tmp.valid()) and cell:
                    self.svgBoxes[y][x] = None
                    self.cacheSvgBoxLocked(cell)

        for y in range(len(self.svgBoxes)):
            for x in range(len(self.svgBoxes[y])):
                tmp = self.data.get(x - int(offsetX / blockSize) - 1, y - int(offsetY / blockSize) - 1)
                cell: MapCell = self.svgBoxes[y][x]
                if tmp and tmp.valid():
                    cell = cell or self._newSvg()
                    self.svgBoxes[y][x] = cell
                    cell.loadResizeMove(tmp, self.scale, x * int(blockSize) + sx - blockSize, y * int(blockSize) + sy - blockSize)
                
        self.findMainWin().barPosition.setText('x:{}({}) y:{}({})'.format(-offsetX, -int(offsetX / blockSize), offsetY, int(offsetY / blockSize)))
        self.findMainWin().barZoom.setText('{}%'.format(int(self.scale * 100)))
        
        self.selectionEvent()
        self.repaint()
        
    def findCellUnder(self, a0: QtGui.QMouseEvent, c: QtCore.QPoint = None):
        c = a0 and a0.pos() or c
        bs = self._blocksize()
        sx, sy = self.deltaxy()
        rr = math.floor
        ix = math.ceil((c.x() - sx) / bs) # xy of cell
        iy = math.ceil((c.y() - sy) / bs)
        pt = QtCore.QPoint(int((c.x() - sx) / bs) * bs + sx, int((c.y() - sy) / bs) * bs + sy)
        x_ = (c.x() - self.viewOrigin[0]) / bs # xy of data
        y_ = (c.y() - self.viewOrigin[1]) / bs
        x, y = rr(x_), rr(y_)
        if x_ == x or y_ == y: # special case: cursor on edge, no cell found
            return None, None, pt
        d = self.data.get(x, y) or MapDataElement(x = x, y = y)
        if iy >= len(self.svgBoxes) or ix >= len(self.svgBoxes[iy]):
            return None, None, pt
        cell = self.svgBoxes[iy][ix]
        return d, cell, pt
    
    def findMainWin(self):
        p = self.parent()
        while not isinstance(p, QMainWindow):
            p = p.parent()
        return p
    
    def selectionEvent(self, action=None, d=None):
        # print(d)
        self.findMainWin().barSelection.setText(self.selector.status())

    def keyReleaseEvent(self, a0: QtGui.QKeyEvent) -> None:
        self.repaint()
        return super().keyReleaseEvent(a0)
        
    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        if a0.key() == QtCore.Qt.Key.Key_Delete:
            self.actDelete()
            
        ctrl = QtGui.QGuiApplication.keyboardModifiers() & QtCore.Qt.KeyboardModifier.ControlModifier 
          
        if ctrl and a0.key() == QtCore.Qt.Key.Key_C:
            self.actCopy()

        if ctrl and a0.key() == QtCore.Qt.Key.Key_X:
            self.actCut()
            
        if ctrl and a0.key() == QtCore.Qt.Key.Key_V:
            self.actPaste() 
                
        if ctrl and (a0.key() == QtCore.Qt.Key.Key_Z or a0.key() == QtCore.Qt.Key.Key_Y):
            self.actUndoRedo(a0.key() == QtCore.Qt.Key.Key_Y)
            
        if ctrl and a0.key() == QtCore.Qt.Key.Key_A:
            self.actSelectAll()
            
        if a0.key() == QtCore.Qt.Key.Key_Escape:
            self.selector.clear()
            self.hover.clear()
            self.dragger.reset()
            self.pressHoldSel = False
            self.pressPos = None
            self.pressPosPath.clear()
            self.pan(0, 0)
            self.findMainWin().searchResults.clearSelection()
            QApplication.restoreOverrideCursor()
            
        if a0.key() == QtCore.Qt.Key.Key_Home or a0.key() == QtCore.Qt.Key.Key_H:
            self.center()
            
        if a0.key() == QtCore.Qt.Key.Key_Space:
            edit: QLineEdit = self.findMainWin().searchBox
            edit.setFocus()
            edit.selectAll()
            
        if a0.key() == QtCore.Qt.Key.Key_Q or a0.key() == QtCore.Qt.Key.Key_1:
            q = a0.key() == QtCore.Qt.Key.Key_Q 
            c = a0.key() == QtCore.Qt.Key.Key_1
            for l in self.hover.labels:
                l: MapDataElement
                r = SvgSource.tryRotate(l.src.svgId, q=q, c1234=c)
                if r:
                    l.src = SvgSource.getcreate(r, SvgSource.Search.path + "/" + r, BS, BS)

        self.repaint() 
        return super().keyPressEvent(a0)
    
    def actDelete(self):
        self.data.begin()
        for l in self.selector.labels:
            self.data.delete(l.data.x, l.data.y)
        self.selector.clear()
        self.pan(0, 0)
    
    def actSelectAll(self):
        self.selector.clear()
        for k in self.data.data:
            self.selector.addSelection(self.data.data[k], propertyPanel=False)
        self.findMainWin().propertyPanel.update()
        self.repaint()
        
    def actCopy(self):
        s = []
        for l in self.selector.labels:
            s.append(l.data.todict())
        QtGui.QGuiApplication.clipboard().setText(json.dumps(s))
        
    def actCut(self):
        self.actCopy()
        self.actDelete()
        
    def actPaste(self):
        c = []
        text = QtGui.QGuiApplication.clipboard().text()
        bad = False

        try:
            for s in json.loads(text):
                d: MapDataElement = MapDataElement.fromdict(s)
                if d and d.src and d.src.svgId:
                    c.append(d)
                else:
                    bad = True
        except JSONDecodeError:
            rows = parseBS(text)
            for y in range(len(rows)):
                x = 0
                while x < len(rows[y]):
                    d = rows[y][x]
                    if not d:
                        x = x + 1
                        continue
                    el = MapDataElement.createFromIdsAt(self, x, y, d)
                    if el:
                        c.append(el)
                    elif x == 0:
                        d = str(d)
                        for xx in range(1, len(rows[y])):
                            el = MapDataElement.createFromIdsAt(self, x, y, rows[y][xx])
                            if el:
                                el.text, el.textAlign, el.textPlacement = d, 'r', 'l'
                                c.append(el)
                                rows[y][0:xx] = []
                                break
                            else:
                                d = d + str(rows[y][xx])
                    elif c:
                        el: MapDataElement = c[-1]
                        el.text, el.textAlign, el.textPlacement = str(d), 'l', 'r'
                    x = x + 1

        if bad or len(c) == 0:
            QMessageBox(QMessageBox.Icon.Warning, TR("Paste"),
                        c and TR("__paste_filter_invalid_blocks__").format(len(c)) or TR("__paste_no_valid_blocks__")).exec_()

        if len(c):
            self.ghostHold(c)

    def actUndoRedo(self, redo=False):
        if redo:
            self.data.forward()
        else:
            self.data.rewind()
        self.selector.clear()
        self.pan(0, 0)
        
    def actSelectByText(self):
        x, ok = QInputDialog.getText(self, TR('Select by Text'), TR('Text:'))
        if not ok or not x:
            return 
        self.selector.clear()
        for k in self.data.data:
            d = self.data.data[k]
            if d.text.lower().count(x.lower()) > 0:
                self.selector.addSelection(d, propertyPanel=False)
        self.findMainWin().propertyPanel.update()
    
    def ghostHold(self, c: typing.List[MapDataElement]):
        self.data.begin()
        self.selector.clear()
        self.hover.hold(c)
        self.dragger.start(0, 0, QtCore.QPoint(0, 0))
        self.dragger.visible = False
        self.pressHoldSel = True
        
    def center(self, selected=False, resetzoom=False):
        if resetzoom:
            self.scale = 1
        if len(self.data.data) == 0:
            self.viewOrigin = [0, 0]
            self.pan(0, 0)
            return
        if selected and len(self.selector.labels):
            cx, cy = self.selector.labels[0].datax, self.selector.labels[0].datay
        else:
            r = self.data.bbox()
            cx, cy = r.x() + r.width() // 2, r.y() + r.height() // 2
        x, y = cx * self._blocksize(), cy * self._blocksize()
        x = -x + self.width() // 2
        y = -y + self.height() // 2
        self.viewOrigin = [x, y]
        self.pan(0, 0)
    
    def _toggleSvgBoxesMoving(self, v):
        for row in self.svgBoxes:
            for c in row:
                if c:
                    c.moving = v
        for c in self.svgBoxesRecycle:
            c.moving = v

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        d, _, pt = self.findCellUnder(a0)
        self.currentData = d
        if a0.buttons() & QtCore.Qt.MouseButton.MidButton:
            self.pressPos = a0.pos()
            QApplication.setOverrideCursor(QtCore.Qt.CursorShape.DragMoveCursor)
            if len(self.svgBoxes) * len(self.svgBoxes[0]) > 1600 and len(self.data.data) > 900:
                self._toggleSvgBoxesMoving(True)
        elif len(self.hover.labels) > 0:
            old = self.hover.labels
            self.hover.end(a0.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier)
            self.pressHoldSel = False
            self.dragger.reset()
            self.pan(0, 0)
            if a0.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier:
                self.ghostHold([x.dup() for x in old]) # continue holding
            else:
                self.findMainWin().searchResults.clearSelection()
        else:
            self.pressPos = None
            self.pressHoldSel = True
            if d:
                if a0.buttons() & QtCore.Qt.MouseButton.RightButton:
                    self.selector.addSelection(d)
                    self.dragger.start(a0.x(), a0.y(), pt)
                else:
                    if a0.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier:
                        if not self.selector.addSelection(d):
                            self.pressPos = a0.pos()
                            self.pressPosPath.append((a0.x(), a0.y()))
                    elif a0.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier:
                        self.selector.delSelection(d)
                    else:
                        self.selector.clear()
                        self.selector.addSelection(d)
            self.repaint()
        return super().mousePressEvent(a0)
    
    def _blocksize(self):
        return int(self.scale * BS)
    
    def _appendPressPath(self):
        x, y = self.pressPos.x(), self.pressPos.y()
        if self.pressPosPath:
            if abs(x - self.pressPosPath[-1][0]) < 4 and abs(y - self.pressPosPath[-1][1]) < 4:
                return
        self.pressPosPath.append((x, y))

    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:
        d, cell, pt = self.findCellUnder(a0)
        if d:
            self.findMainWin().barCursor.setText("{}-{}".format(d.x, d.y))
        if a0.buttons() & QtCore.Qt.MouseButton.MidButton:
        # if isinstance(self.pressPos, QtCore.QPoint):
            diff: QtCore.QPoint = a0.pos() - self.pressPos
            self.pressPos = a0.pos()
            self.pan(diff.x(), diff.y())
        elif a0.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier and self.pressPosPath:
            self._appendPressPath()
            self.pressPos = a0.pos()
            self.repaint()
        elif self.pressHoldSel:
            if d:
                if self.dragger.started:
                    self.dragger.drag(a0.x(), a0.y(), pt)
                else:
                    if a0.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier:
                        self.selector.addSelection(d)
                    elif a0.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier:
                        self.selector.delSelection(d)
            self.repaint()
        return super().mouseMoveEvent(a0)
    
    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.pressPos = None
        
        if self.pressPosPath:
            poly = QtGui.QPolygon()
            for x, y in self.pressPosPath:
                poly.append(QtCore.QPoint(x, y))
            for row in self.svgBoxes:
                for cell in row:
                    if cell and cell.current:
                        p = QtCore.QPoint(cell.posx + self._blocksize() // 2, cell.posy + self._blocksize() // 2)
                        if poly.containsPoint(p, QtCore.Qt.FillRule.OddEvenFill):
                            # print(cell.current.src.svgId)
                            self.selector.addSelection(cell.current, propertyPanel=False)
            self.findMainWin().propertyPanel.update()
            self.pressPosPath.clear()
        
        if self.hover.labels:
            pass # hover depends on dragger, so we don't end it
        else:
            self.pressHoldSel = False
            dx, dy = self.dragger.end()
            if dx != 0 or dy != 0:
                self.selector.move(dx, dy)

        QApplication.restoreOverrideCursor()
        self._toggleSvgBoxesMoving(False)

        self.pan(0, 0)
        return super().mouseReleaseEvent(a0)
    
    def wheelEvent(self, a0: QtGui.QWheelEvent) -> None:
        if self.selector.labels and self.pressHoldSel:
            return super().wheelEvent(a0)
            
        lastScale = self.scale
        if a0.angleDelta().y() > 0:
            self.scale = min(self.scale < 1 and self.scale + 0.125 or self.scale + 1, 32)
        else:   
            self.scale = max(self.scale <= 1 and self.scale - 0.125 or self.scale - 1, 0.25)
            
        c = a0.pos()
        self.viewOrigin[0] = int((self.viewOrigin[0] - c.x()) * self.scale / lastScale + c.x())
        self.viewOrigin[1] = int((self.viewOrigin[1] - c.y()) * self.scale / lastScale + c.y())
        self.pan(0, 0)
        return super().wheelEvent(a0)
    
    def _newSvg(self):
        if self.svgBoxesRecycle:
            return self.svgBoxesRecycle.pop()
        return MapCell(self)
