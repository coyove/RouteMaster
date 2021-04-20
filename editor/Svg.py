import json
import math
import typing

from PyQt5 import QtGui
from PyQt5 import QtCore, QtSvg
from PyQt5.QtGui import QColor, QFont, QFontMetrics, QPainter
from PyQt5.QtWidgets import QListView, QMainWindow, QPushButton, QTableWidget, QTableWidgetItem, QToolBar, QWidget 
from urllib.parse import quote, unquote
from Common import BS
import os

class SvgSource:
    Manager = {}
    
    def get(id):
        return id in SvgSource.Manager and SvgSource.Manager[id] or None
    
    def __init__(self, parent, id, svgData: bytes, w = 0, h = 0) -> None:
        self.svgData = svgData
        self.svgId = id
        self._renderer = QtSvg.QSvgWidget(parent)
        self._renderer.load(svgData)
        self._renderer.setVisible(False)
        self._w, self._h = w, h
        SvgSource.Manager[self.svgId] = self
        
    def dupWithSize(self, w, h):
        return SvgSource(self._renderer.parent(), self.svgId, self.svgData, w, h)
        
    def overrideSize(self, w, h):
        self._w, self._h = w, h
        
    def width(self):
        return self._w or self._renderer.sizeHint().width() 
    
    def height(self):
        return self._h or self._renderer.sizeHint().height()
    
    def paint(self, x: int, y: int, w: int, h: int, p: QPainter):
        self._renderer.setFixedSize(w, h)
        p.translate(x, y)
        self._renderer.render(p, flags=QWidget.RenderFlag.DrawChildren)
        p.translate(-x, -y)
        
class SvgBar(QWidget):
    size = 64

    def __init__(self, parent):
        super().__init__(parent)
        # self.setStyleSheet("background: white")
        self.setFixedHeight(SvgBar.size * 1.5)
        self.sources = []
        self.setMouseTracking(True)
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
        self.refresh()
        
    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        self.refresh()
        return super().resizeEvent(a0)

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        p = QPainter(self)
        p.fillRect(0, 0, self.width(), self.height(), QColor(255 ,255, 255))
        for i in range(len(self.sources)):
            x = i * SvgBar.size
            s: SvgSource = self.sources[i]
            m = 8
            s.paint(x + m, m, SvgBar.size - m*2, SvgBar.size - m*2, p)
            p.drawRect(x + m, m, SvgBar.size - m*2, SvgBar.size - m*2)
            opt = QtGui.QTextOption(QtCore.Qt.AlignmentFlag.AlignCenter)
            opt.setWrapMode(QtGui.QTextOption.WrapMode.WrapAnywhere)
            p.save()
            if i == self.currentHover:
                p.fillRect(x, 0, SvgBar.size, SvgBar.size * 1.5, QColor(0, 0, 0, 40))
            p.drawText(QtCore.QRectF(x + 4, SvgBar.size, SvgBar.size - 8, SvgBar.size / 2), unquote(s.svgId.replace('bsicon_', '').replace('.svg', '')), option=opt)
            p.restore()
        p.end()
        return super().paintEvent(a0)
    
    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.currentHover = a0.x() // SvgBar.size
        if self.currentHover < len(self.sources):
            self.findMainWin().ghostHold(self.sources[self.currentHover].dupWithSize(BS, BS))
        self.repaint()
        return super().mousePressEvent(a0)
    
    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
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
            self.sources.append(SvgSource(self, self.files[i][0], self.files[i][1]))
        self.repaint()
        
class SvgSearch:
    def __init__(self, path: str) -> None:
        self.path = path.strip("/")
        with open(self.path + '/meta.json', 'rb') as f:
            data = json.load(f)

        self.data = data
        self.files = set()

        for k in data:
            for n in data[k]:
                self.files.add(n.lower())
        
    def search(self, q: str):
        q = q.lower()

        scores = {}
        for p in q.split(' '):
            if not p in self.data:
                continue
            for c in self.data[p]:
                if c in scores:
                    scores[c] = scores[c] + 1
                else:
                    scores[c] = 1
        c = []
        for k in scores:
            c.append((k, scores[k]))
            
        test = "bsicon_" + quote(q) + ".svg"
        if test in self.files:
            c.append((test, 1e8))
            
        uq = quote(q).lower()
        for f in self.files:
            f: str = f
            if f.count(uq) > 0:
                c.append((f, 1e3 * (1000 - len(f))))
            
        c = sorted(c, key=lambda x: (x[1], x[0]), reverse=True)
        return list(map(lambda x: (x[0], self.path + "/" + x[0]), c))
