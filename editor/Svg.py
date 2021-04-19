import json
from PyQt5 import QtCore, QtSvg
from PyQt5.QtGui import QColor, QFont, QFontMetrics, QPainter
from PyQt5.QtWidgets import QListView, QTableWidget, QTableWidgetItem, QWidget 
from urllib.parse import quote
import os

class SvgSource:
    Manager = {}
    
    def get(id):
        return id in SvgSource.Manager and SvgSource.Manager[id] or None
    
    def __init__(self, parent, id, svgData: bytes) -> None:
        self.svgData = svgData
        self.svgId = id
        self._renderer = QtSvg.QSvgWidget(parent)
        self._renderer.load(svgData)
        self._renderer.setVisible(False)
        self._w = self._h = 0 # override sizeHint
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
        
class SvgSearch:
    def __init__(self, path: str) -> None:
        self.path = path.strip("/")
        with open(self.path + '/meta.json') as f:
            data = json.load(f)

        self.data = data
        self.files = set()

        for k in data:
            for n in data[k]:
                self.files.add(n)
        
    def search(self, q: str):
        scores = {}
        for p in q.lower().split(' '):
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
            f: str = f.lower()
            if f.count(uq) > 0:
                c.append((f, 1e5))
            
        c = sorted(c, key=lambda x: x[1], reverse=True)
        return list(map(lambda x: (x[0], self.path + "/" + x[0]), c))
