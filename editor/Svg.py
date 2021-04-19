import json

from PyQt5 import QtGui
from PyQt5 import QtCore, QtSvg
from PyQt5.QtGui import QColor, QFont, QFontMetrics, QPainter
from PyQt5.QtWidgets import QListView, QPushButton, QTableWidget, QTableWidgetItem, QToolBar, QWidget 
from urllib.parse import quote
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
        self.setFixedHeight(SvgBar.size)
        self.setContentsMargins(0, 0, 0, 0)
        self.left = QPushButton("<", self)
        self.right = QPushButton(">", self)
        self.svgBoxes = []

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        size = SvgBar.size
        self.left.setFixedSize(size / 2, size)
        self.left.move(0, 0)
        self.right.setFixedSize(size / 2, size)
        self.right.move(self.width() - size / 2, 0)
        return super().resizeEvent(a0)
        
class SvgSearch:
    def __init__(self, path: str) -> None:
        self.path = path.strip("/")
        with open(self.path + '/meta.json') as f:
            data = json.load(f)

        self.data = data
        self.files = set()

        for k in data:
            for n in data[k]:
                self.files.add(n.lower())
        
    def search(self, q: str):
        q = q.lower()
        test = quote(q) + ".svg"
        if test in self.files:
            return [(test, self.path + "/" + test)]

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
            
        uq = quote(q).lower()
        for f in self.files:
            f: str = f
            if f.count(uq) > 0:
                c.append((f, 1e5))
            
        c = sorted(c, key=lambda x: x[1], reverse=True)
        return list(map(lambda x: (x[0], self.path + "/" + x[0]), c))
