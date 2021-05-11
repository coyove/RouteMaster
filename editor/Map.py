import json
import math
import random
import sys
import typing
import re
from json.decoder import JSONDecodeError

import PyQt5.QtGui as QtGui
from PyQt5 import QtCore
from PyQt5.QtWidgets import (QApplication, QComboBox, QInputDialog, QLineEdit,
                             QMainWindow, QMessageBox, QWidget, qApp)

from Common import BS, FLAGS, TR
from Controller import Dragger, Hover, Ruler, Selector
from MapData import MapDataRenderer, MapData, MapDataElement
from Parser import filterBS, parseBS
from Svg import SvgSource


def mod(x, y):
    return x - int(x/y) * y

class Map(QWidget):
    Background = QtGui.QColor(255, 255, 255)

    import functools

    @functools.cache
    def BigFont():
        return QtGui.QFont(QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.SystemFont.FixedFont).family(), 16)

    def __init__(self, parent):
        super().__init__(parent)
        
        self.data = MapData(self)
        self.scale = 2

        if FLAGS["DEBUG_fill"]:
            sources = []
            for i in range(0, 10):
                sources.append(SvgSource("id" + str(i), """
                    <svg height="48" width="48">
                        <text x="8" y="24" fill="red">{}</text>
                        <rect x="8" y="8" width="32" height="32" fill="transparent" stroke="#000"></rect>
                    </svg>""".format(i).encode('utf-8'), BS, BS))
            n = FLAGS["DEBUG_fill"]
            s = math.sqrt(n)
            for i in range(0, n):
                l = int(random.random() * s + 1)
                d = random.random() * math.pi * 2
                x, y = int(l * math.cos(d)), int(l * math.sin(d))
                el = MapDataElement(sources[random.randrange(0, len(sources))])
                if random.random() > 0.9:
                    el.cascades.append(sources[random.randrange(0, len(sources))])
                if random.random() > 0.8:
                    el.text = "lazy\nfox jumps"
                self.data._put(x, y, el)

        self.selector = Selector(self)
        self.dragger = Dragger(self)
        self.hover = Hover(self)
        self.ruler = Ruler(self)
        self.boxRows = self.boxCols = 0
        self.viewOrigin = [0, 0]
        self.pan(0, 0) # fill svgBoxes
        self.setMouseTracking(True)
        self.pressPos = None
        self.pressPosPath = []
        self.pressHoldSel = False
        self.showRuler = True
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)
        
    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        self.pan(0, 0)
        return super().resizeEvent(a0)

    def _getVirtualCell(self, x, y):
        bs = self._blocksize()
        return self.data.get(x - int(self.viewOrigin[0] / bs) - 1, y - int(self.viewOrigin[1] / bs) - 1)
    
    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.RenderHint.HighQualityAntialiasing)
        p.fillRect(0, 0, self.width(), self.height(), Map.Background)

        bs = self._blocksize()
        sx, sy = self.deltaxy()

        if self.boxRows * self.boxCols > len(self.data.data):
            for v in self.data.data.values():
                MapDataRenderer.paint(v, v in self.selector, self.scale, v.x * int(bs) + self.viewOrigin[0], v.y * int(bs) + self.viewOrigin[1], p)
        else:
            for y in range(self.boxRows):
                for x in range(self.boxCols):
                    tmp = self._getVirtualCell(x, y)
                    if tmp and tmp.valid():
                        MapDataRenderer.paint(tmp, tmp in self.selector, self.scale, x * int(bs) + sx - bs, y * int(bs) + sy - bs, p)

        self.selector.paint(p)
        self.dragger.paint(p)
        self.hover.paint(p)
        for i in range(0, len(self.pressPosPath)):
            s, e = self.pressPosPath[i], self.pressPosPath[i < len(self.pressPosPath) - 1 and i + 1 or 0]
            p.drawLine(s[0], s[1], e[0], e[1])

        w = 0
        if self.showRuler:
            w = Ruler.Width
            self.ruler.paint(p)

        if FLAGS.get('show_keys', False):
            vis = []
            QApplication.queryKeyboardModifiers() & QtCore.Qt.KeyboardModifier.ControlModifier and vis.append('\u2318' if sys.platform == 'darwin' else 'Ctrl')
            QApplication.queryKeyboardModifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier and vis.append("Shift")
            if vis:
                p.setFont(Map.BigFont())
                p.drawText(w + 2, w + Map.BigFont().pointSize(), '-'.join(vis))

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

        self.boxRows = int(self.height() / blockSize) + 3
        self.boxCols = int(self.width() / blockSize) + 3

        self.findMainWin().barPosition.setText('x:{}({}) y:{}({})'.format(offsetX, int(offsetX / blockSize), offsetY, int(offsetY / blockSize)))
        self.findMainWin().barZoom.setText('{}%'.format(int(self.scale * 100)))
        
        self.selectionEvent()
        self.repaint()
        
    def findCellUnder(self, a0: QtGui.QMouseEvent, c: QtCore.QPoint = None):
        c = a0 and a0.pos() or c
        bs = self._blocksize()
        sx, sy = self.deltaxy()
        rr = math.floor
        pt = QtCore.QPoint(int((c.x() - sx) / bs) * bs + sx, int((c.y() - sy) / bs) * bs + sy)
        x_ = (c.x() - self.viewOrigin[0]) / bs # xy of data
        y_ = (c.y() - self.viewOrigin[1]) / bs
        x, y = rr(x_), rr(y_)
        if x_ == x or y_ == y: # special case: cursor on edge, no cell found
            return None, pt
        d = self.data.get(x, y) or MapDataElement(x = x, y = y)
        return d, pt
    
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
            
        if a0.key() == QtCore.Qt.Key.Key_Q:
            for l in self.hover.labels:
                l: MapDataElement
                r = SvgSource.tryRotate(l.src.svgId, q=True)
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
            l = json.loads(text)
            if not isinstance(l, list):
                c = filterBS(parseBS(text))
            else:
                for s in l:
                    d = MapDataElement.fromdict(s)
                    if d and d.src and d.src.svgId:
                        c.append(d)
                    else:
                        bad = True
        except JSONDecodeError:
            c = filterBS(parseBS(text))

        if bad or len(c) == 0:
            QMessageBox(QMessageBox.Icon.Warning, TR("Paste"),
                        c and TR("__paste_filter_invalid_blocks__").format(len(c)) or TR("__paste_no_valid_blocks__")).exec_()
        len(c) and self.ghostHold(c)

    def actUndoRedo(self, redo=False):
        self.selector.clear()
        if redo:
            self.data.forward()
        else:
            self.data.rewind()
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
    
    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        if FLAGS["DEBUG_crash"]:
            print(1 // 0)
        if self.showRuler and self.ruler.mousePress(a0):
            self.repaint()
            return super().mousePressEvent(a0)
        d, pt = self.findCellUnder(a0)
        if a0.buttons() & QtCore.Qt.MouseButton.MidButton: # pan start
            self.pressPos = a0.pos()
            QApplication.setOverrideCursor(QtCore.Qt.CursorShape.DragMoveCursor)
        elif len(self.hover.labels) > 0: # ghost hold, place them
            if a0.buttons() & QtCore.Qt.MouseButton.RightButton:
                self.hover.clear()
                self.pressHoldSel = False
                self.dragger.reset()
                return super().mousePressEvent(a0)

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
                if a0.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier: # select
                    if not self.selector.addSelection(d): # begin circle select
                        self.pressPos = a0.pos()
                        self.pressPosPath.append((a0.x(), a0.y()))
                elif a0.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier: # un-select
                    self.selector.delSelection(d)
                elif d.src: # select-n-drag
                    if len(self.selector.labels) == 1:
                        self.selector.clear()
                    self.selector.addSelection(d)
                    self.dragger.start(a0.x(), a0.y(), pt)
                else: # clear selections
                    self.selector.clear()
                    # let's take the slow way, find something visually selectable and select it for user
                    bs = self._blocksize()
                    d, _ = self.findCellUnder(None, QtCore.QPoint(a0.x() - bs, a0.y()))
                    if d and d.src and d.calcActualWidthX(bs, bs) > bs:
                        # double width block consists of 2 std blocks (a, b), user clicked "b", we select "a"
                        self.selector.addSelection(d)
                    else:
                        # block with text, user clicked "text", we select the block
                        sx, sy = self.deltaxy()
                        for y in range(self.boxRows):
                            for x in range(self.boxCols):
                                cell = self._getVirtualCell(x, y)
                                if cell and cell.valid() and cell.text:
                                    posx, posy = x * bs + sx - bs, y * bs + sy - bs
                                    r = cell.textbbox(self.scale, posx, posy, measure=True)
                                    if r.contains(a0.pos()):
                                        self.selector.addSelection(cell)
            self.repaint()
        return super().mousePressEvent(a0)
    
    def _blocksize(self):
        return int(self.scale * BS)
    
    def _appendPressPath(self):
        x, y = self.pressPos.x(), self.pressPos.y()
        if abs(x - self.pressPosPath[-1][0]) < 4 and abs(y - self.pressPosPath[-1][1]) < 4:
            return
        self.pressPosPath.append((x, y))

    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:
        d, pt = self.findCellUnder(a0)
        changed = False
        if d: # update ruler
            xy = (d.x, d.y)
            changed = self.ruler.currentXY != xy and self.showRuler
            self.ruler.currentXY = xy

        if a0.buttons() & QtCore.Qt.MouseButton.MidButton: # pan
            diff: QtCore.QPoint = a0.pos() - self.pressPos
            self.pressPos = a0.pos()
            self.pan(diff.x(), diff.y())
        elif a0.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier and self.pressPosPath: # circle select
            self._appendPressPath()
            self.pressPos = a0.pos()
            self.repaint()
        elif self.pressHoldSel:
            if d:
                if self.dragger.started: # drag, show drag pointer
                    self.dragger.drag(a0.x(), a0.y(), pt)
                else:
                    if a0.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier: # select
                        self.selector.addSelection(d)
                    elif a0.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier: # un-select
                        self.selector.delSelection(d)
            self.repaint()
        elif changed:
            self.repaint()
        return super().mouseMoveEvent(a0)
    
    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.pressPos = None
        
        if self.pressPosPath: # circle select, calc how many blocks have been circled
            sx, sy = self.deltaxy()
            bs = self._blocksize()
            poly = QtGui.QPolygon()
            for x, y in self.pressPosPath:
                poly.append(QtCore.QPoint(x, y))
            for y in range(self.boxRows):
                for x in range(self.boxCols):
                    cell = self._getVirtualCell(x, y)
                    if cell and cell.valid():
                        posx, posy = x * bs + sx - bs, y * bs + sy - bs
                        p = QtCore.QPoint(posx + bs // 2, posy + bs // 2)
                        if poly.containsPoint(p, QtCore.Qt.FillRule.OddEvenFill):
                            self.selector.addSelection(cell, propertyPanel=False)
            self.findMainWin().propertyPanel.update()
            self.pressPosPath.clear()
        
        if self.hover.labels:
            pass # ghost hold depends on dragger, don't end() it here, call end() in mousePressEvent
        else:
            self.pressHoldSel = False
            dx, dy = self.dragger.end()
            if dx != 0 or dy != 0:
                self.selector.moveEnd(dx, dy)

        self.pan(0, 0)
        QApplication.restoreOverrideCursor()
        return super().mouseReleaseEvent(a0)
    
    def wheelEvent(self, a0: QtGui.QWheelEvent) -> None:
        if self.selector.labels and self.pressHoldSel:
            return super().wheelEvent(a0)
        
        if a0.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier:
            c = self.hover.cats()
            if len(c) == 1:
                v = a0.angleDelta().y() or a0.angleDelta().x()
                self.hover.incr() if v > 0 else self.hover.decr()
                self.repaint()
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
    