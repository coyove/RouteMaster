import collections
import struct, json
import typing

import PyQt5.QtSvg as QtSvg
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QPoint, QRectF
from PyQt5.QtGui import QColor, QImage, QOpenGLContext, QPainter, QPaintEvent
from PyQt5.QtWidgets import QGraphicsEllipseItem, QWidget


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
        SvgSource.Manager[self.svgId] = self

class MapData:
    class Element:
        def __init__(self, id = None, d: SvgSource = None, x = 0, y = 0) -> None:
            self.id = id
            self.data = d
            self.x = x
            self.y = y
            
        def valid(self):
            return self and self.data
        
        def __str__(self) -> str:
            return self.data and "({}:{})".format(self.id, self.data.svgId) or "(empty)"
        
        def pack(self):
            return json.dumps({
                "cellX": self.x,
                "cellY": self.y,
                "cellId": self.id,
                "svgId": self.data and self.data.svgId or "0",
            })
        
        def unpack(data):
            try:
                x = json.loads(data)
                return MapData.Element(x["cellId"], SvgSource.get(x["svgId"]), x["cellX"], x["cellY"])
            except Exception as e:
                print(e)
            
    class History:
        def __init__(self, x, y, d) -> None:
            self.x = x
            self.y = y
            if d:
                self.id = d.id
                self.svgId = d.data and d.data.svgId or ""
            else:
                self.id = self.svgId = ''

    def __init__(self) -> None:
        self.data1 = [] # Q1, include +x, include +y
        self.data2 = [] # Q2, exclude +y, include -x
        self.data3 = [] # Q3, exclude -x, include -y
        self.data4 = [] # Q4, exclude -y, exclude -x
        self.history = collections.deque(maxlen=5000)
    
    def _which(self, x: int, y: int):
        data = None
        if x >= 0 and y >= 0:
            data = self.data1
        elif x < 0 and y >= 0:
            x = -x
            data = self.data2
        elif x > 0 and y < 0:
            y = -y
            data = self.data4
        else:
            x, y = -x, -y
            data = self.data3
        return data, x, y

    def put(self, x: int, y: int, d: Element):
        self._appendHistory(MapData.History(x, y, self._put(x, y, d)))

    def _put(self, x: int, y: int, d: Element) -> Element:
        d.x, d.y = x, y
        data, x, y = self._which(x, y)
        while len(data) <= y:
            data.append([])
        while len(data[y]) <= x:
            data[y].append(None)
        old = data[y][x]
        data[y][x] = d
        return old

    def get(self, x: int, y: int) -> Element:
        data, x, y = self._which(x, y)
        if len(data) <= y:
            return None
        if len(data[y]) <= x:
            return None
        return data[y][x]
       
    def delete(self, x: int, y: int):
        self._appendHistory(MapData.History(x, y, self._delete(x, y)))

    def _delete(self, x: int, y: int) -> Element:
        data, x, y = self._which(x, y)
        if len(data) <= y:
            return None
        if len(data[y]) <= x:
            return None
        old = data[y][x]
        data[y][x] = None
        return old
    
    def _appendHistory(self, h):
        self.history.append(h)
    
    def begin(self):
        if len(self.history) and self.history[-1] == None: # no conjucated Nones
            return
        self.history.append(None)
        
    def rewind(self):
        while len(self.history):
            h = self.history.pop()
            if not h:
                break
            if h.id:
                self._put(h.x, h.y, MapData.Element(h.id, SvgSource.get(h.svgId)))
            else:
                self._delete(h.x, h.y)

class MapCell:
    Base = 32

    def __init__(self, parent) -> None:
        self.current: MapData.Element = None
        self.currentScale = 1.0
        self.moving = False
        self.parent = parent
        
    def paint(self, p: QPainter): 
        if self.moving and self.parent.currentData != self.current:
            blockSize = int(MapCell.Base * self.currentScale)
            p.drawRect(self.posx, self.posy, blockSize, blockSize)
        elif self.current:
            self.current.data._renderer.setFixedSize(self.w, self.h)
            p.translate(self.x, self.y)
            self.current.data._renderer.render(p, flags=QWidget.RenderFlag.DrawChildren)
            p.translate(-self.x, -self.y)
        
    def loadResizeMove(self, data: MapData.Element, scale: float, x: int, y: int):
        self.current = data
        self.currentScale = scale
        # super().load(data.svgData)
        # svgSize = self.sizeHint()
        # w, h = int(svgSize.width() * scale), int(svgSize.height() * scale)
        self.w = int(data.data._renderer.sizeHint().width() * scale)
        self.h = int(data.data._renderer.sizeHint().height() * scale)
        
        self.posx, self.posy = x, y
        self.x = int(x - (self.w - MapCell.Base * scale) / 2)
        self.y = int(y - (self.h - MapCell.Base * scale) / 2)

    def pos(self) -> QtCore.QPoint:
        return QtCore.QPoint(self.posx, self.posy)
