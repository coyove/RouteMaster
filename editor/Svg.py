import json
import os
from urllib.parse import quote, unquote

from PyQt5 import QtCore, QtGui, QtSvg
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import QMainWindow, QWidget

from Common import BS, PNG_POLYFILLS, TR


def _quote(s: str):
    s = quote(s)
    return s.replace('%40', '@')
 
class SvgSearch:
    def __init__(self, path: str) -> None:
        self.path = path.removesuffix("/")
        self.reload()
    
    def reload(self):
        self.files = {}
        for f in os.listdir(self.path):
            if f.endswith(".svg"):
                self.files[f.lower()] = f
                
    def guess(self, s: str):
        if not s:
            return "", ""
        if s.endswith('.svg'):
            return s, self.fullpath(s)
        p = "bsicon_" + _quote(s).lower() + ".svg"
        if p in self.files:
            return self.files[p], self.fullpath(self.files[p])
        QtCore.qDebug(("guess '" + s + u"' failed").encode('utf-8'))
        return "", ""
                
    def fullpath(self, id: str):
        return self.path + "/" + id
        
    def search(self, q: str):
        q = q.strip().lower()
        c = []

        test = "bsicon_" + _quote(q) + ".svg"
        if test in self.files:
            c.append((self.files[test], 1e8))
            
        uq = _quote(q).lower()
        for f in self.files:
            f: str = f
            if f.count(uq) > 0:
                c.append((self.files[f], 1e3 * (1000 - len(f))))
            
        c = sorted(c, key=lambda x: (x[1], x[0]), reverse=True)
        return list(map(lambda x: (x[0], self.path + "/" + x[0]), c))

class SvgSource:
    Manager = {}
    Search: SvgSearch = None
    Parent: QWidget
    
    def get(id):
        if id in SvgSource.Manager:
            return SvgSource.Manager[id]
        fn, p = SvgSource.Search.guess(id)
        if fn:
            s = SvgSource(fn, p, BS, BS)
            return s
        return None
    
    def getcreate(id, fn, w, h):
        if id in SvgSource.Manager:
            return SvgSource.Manager[id]
        s = SvgSource(id, fn, w, h)
        return s
    
    def tryRotate(id: str, q=False, c1234=False):
        def check(fn):
            # print(fn)
            return fn.lower() in SvgSource.Search.files and fn or None

        id = id.removesuffix('.svg')
        if q:
            if id.endswith('q'):
                return check(id[:-1] + ".svg")
            return check(id + "q.svg")
        return
    
    def __init__(self, id, svgData: bytes, w = 0, h = 0) -> None:
        self.svgData = svgData
        self.svgId = id
        self._ratio = 1
        self.svgValid = True
        if id in PNG_POLYFILLS:
            self._renderer = QPixmap(svgData.removesuffix(".svg") + ".png")
            # print(self._renderer.height(), svgData)
            if not self._renderer.height() or not self._renderer.width():
                QtCore.qDebug("{}/{} not valid".format(id, svgData).encode("utf-8"))
                self.svgValid = False
            else:
                self._ratio = self._renderer.width() / self._renderer.height()
        else:
            self._renderer = QtSvg.QSvgWidget(SvgSource.Parent) # SvgRenderer can't render, don't know why
            self._renderer.load(svgData)
            self._renderer.setVisible(False)
            self.svgValid = self._renderer.renderer().isValid()
            if self.svgValid:
                self._ratio = self._renderer.sizeHint().width() / self._renderer.sizeHint().height()
            else:
                self._ratio = 1
        self._w, self._h = w, h
        SvgSource.Manager[self.svgId] = self

    def cleanSvgId(self):
        return unquote(self.svgId.replace('bsicon_', '').replace('.svg', '').replace('BSicon_', ''))
        
    def overrideSize(self, w, h):
        self._w, self._h = w, h
        
    def width(self):
        return self._w or self._renderer.sizeHint().width() 
    
    def height(self):
        return self._h or self._renderer.sizeHint().height()

    def source(self):
        try:
            with open(self.svgData, 'rb') as f:
                return f.read().decode('utf-8')
        except Exception as e:
            QtCore.qDebug("SvgSource.source: {}".format(e))

    def paint(self, x: int, y: int, w: int, h: int, p: QPainter, ghost=False, xOffsetPercent=0):
        if not self.svgValid:
            p.drawRect(x, y, w, h)
            p.save()
            p.setPen(QPen(QColor(255, 0, 0)))
            p.drawText(QtCore.QRect(x + 2, y + 2, w - 4, h - 4), QtCore.Qt.AlignmentFlag.AlignCenter | QtCore.Qt.TextFlag.TextWrapAnywhere, self.cleanSvgId())
            p.drawLine(x, y, x + w, y + h)
            p.drawLine(x + w, y, x, y + h)
            p.restore()
            return
        # print(xOffsetPercent, xOffsetPercent % 1)
        xOffsetPercent = xOffsetPercent % 1
        x = x + int(xOffsetPercent * w)
        w = int(h * self._ratio)
        if isinstance(self._renderer, QPixmap):
            p.drawPixmap(x, y, w, h, self._renderer)
        else:
            self._renderer.setFixedSize(w, h)
            p.translate(x, y)
            self._renderer.render(p, flags=QWidget.RenderFlag.DrawChildren)
            p.translate(-x, -y)
        if ghost:
            p.fillRect(x, y, w, h, QColor(255, 255, 255, 180))
        
class SvgBar(QWidget):
    size = 64
    dragPen = QPen(QColor(0, 0, 0, 255))
    dragPen.setWidth(3)
    dashPen = QPen(QColor(160, 160, 160), 1, style=QtCore.Qt.PenStyle.DashLine)
    dashBrush = QBrush(QColor(240, 240, 240))

    def __init__(self, parent):
        super().__init__(parent)
        # self.setStyleSheet("background: white")
        self.setFixedHeight(SvgBar.size * 1.5)
        self.sources = []
        self.setMouseTracking(True)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)
        self.onDelete = None
        self.onDrag = None
        self.onCopy = None
        self.update([])
    
    def cells(self):
        return self.width() // SvgBar.size
    
    def findMainWin(self):
        p = self.parent()
        while not isinstance(p, QMainWindow):
            p = p.parent()
        return p
        
    def update(self, files):
        self.files = files
        self.page = 0
        self.currentHover = -1
        self.currentDragFrom = -1
        self.currentDragTo = -1
        self.refresh()
        
    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        self.refresh()
        return super().resizeEvent(a0)

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        p = QPainter(self)
        p.fillRect(0, 0, self.width(), self.height(), QColor(255 ,255, 255))
        p.drawRect(0, 0, self.width() - 1, self.height() - 1)
        for i in range(len(self.sources)):
            x = i * SvgBar.size
            s: SvgSource = self.sources[i]
            m = 8
            sz = SvgBar.size - m*2
            if s._ratio > 1:
                s.paint(x + m, m, sz / 2, sz / 2, p)
                r = QtCore.QRect(x + m, m + sz / 2, sz, sz / 2)
                p.save()
                p.setPen(SvgBar.dashPen)
                p.drawRect(r)
                p.fillRect(r, SvgBar.dashBrush)
                p.restore()
                p.drawText(r, QtCore.Qt.AlignmentFlag.AlignCenter, str(s._ratio))
                p.drawRect(x + m, m, sz, sz / 2)
            else:
                w = sz * s._ratio
                s.paint(x + m, m, sz, sz, p)
                if s._ratio != 1:
                    r = QtCore.QRect(x + m + w, m, sz - w, sz)
                    p.save()
                    p.setPen(SvgBar.dashPen)
                    p.drawRect(r)
                    p.fillRect(r, SvgBar.dashBrush)
                    p.restore()
                    # p.drawText(r, QtCore.Qt.AlignmentFlag.AlignCenter, chr(0xbb + int((1 - s._ratio) / 0.25)))
                p.drawRect(x + m, m, w, sz)
            opt = QtGui.QTextOption(QtCore.Qt.AlignmentFlag.AlignCenter)
            opt.setWrapMode(QtGui.QTextOption.WrapMode.WrapAnywhere)
            p.save()
            if i == self.currentHover:
                p.fillRect(x, 0, SvgBar.size, SvgBar.size * 1.5, QColor(0, 0, 0, 40))
            if i == self.currentDragTo:
                p.save()
                p.setPen(SvgBar.dragPen)
                p.drawLine(x + 1, 0, x + 1, SvgBar.size * 1.5)
                p.restore()
            p.drawText(QtCore.QRectF(x + 4, SvgBar.size, SvgBar.size - 8, SvgBar.size / 2 - 4), s.cleanSvgId(), option=opt)
            p.restore()
        p.end()
        return super().paintEvent(a0)
    
    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        if self.currentHover >= 0:
            idx = self.currentHover + self.page
            if a0.key() == QtCore.Qt.Key.Key_Delete and self.onDelete:
                self.onDelete(idx)
            if a0.key() == QtCore.Qt.Key.Key_C and a0.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier and self.onCopy:
                self.onCopy(self.sources[self.currentHover])
        return super().keyPressEvent(a0)
    
    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.currentHover = a0.x() // SvgBar.size
        self.currentDragFrom = self.currentHover
        if self.currentHover < len(self.sources) and not self.onDelete: # switch to map view and ghost hold
            self.findMainWin().ghostHoldSvgSource(self.sources[self.currentHover])
            self.findMainWin().mapview.setFocus()
        self.repaint()
        return super().mousePressEvent(a0)

    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:
        if self.currentDragFrom != -1 and self.onDrag:
            self.currentDragTo = a0.x() // SvgBar.size
            self.repaint()
        return super().mouseMoveEvent(a0)
    
    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.dragPos = None
        if self.onDrag and self.currentDragFrom != -1 and self.currentDragTo != -1 and self.currentDragTo != self.currentDragFrom:
            df, dt = self.currentDragFrom + self.page, self.currentDragTo + self.page
            self.onDrag(df, dt)
        self.currentDragFrom = self.currentDragTo = -1
        self.repaint()
        return super().mouseReleaseEvent(a0)
    
    def clearSelection(self):
        self.currentHover = -1
        self.repaint()
    
    def wheelEvent(self, a0: QtGui.QWheelEvent) -> None:
        self.currentHover = -1
        if a0.angleDelta().y() <= 0:
            self.page = min(self.page + self.cells() // 3, max(0, len(self.files) - self.cells() // 2))
        else:
            self.page = max(self.page - self.cells() // 3, 0)
        self.refresh()
        return super().wheelEvent(a0)
    
    def refresh(self):
        self.sources = self.sources[:0]
        for i in range(self.page, self.page + self.cells()):
            if i >= len(self.files):
                break
            self.sources.append(SvgSource.getcreate(self.files[i][0], self.files[i][1], BS, BS))
        self.repaint()
       
