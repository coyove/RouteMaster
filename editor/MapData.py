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
        def __init__(self, d: SvgSource = None, x = 0, y = 0) -> None:
            self.data = d
            self.x = x
            self.y = y
            
        def valid(self):
            return self and self.data
        
        def __str__(self) -> str:
            return self.data and "({})".format(self.data.svgId) or "(empty)"
        
        def pack(self):
            return json.dumps({
                "cellX": self.x,
                "cellY": self.y,
                "svgId": self.data and self.data.svgId or "0",
            })
        
        def unpack(data):
            try:
                x = json.loads(data)
                return MapData.Element(SvgSource.get(x["svgId"]), x["cellX"], x["cellY"])
            except Exception as e:
                print(e)
            
    class History:
        def __init__(self, x, y, d) -> None:
            self.x = x
            self.y = y
            self.svgId = (d and d.data) and d.data.svgId or ""

    def __init__(self) -> None:
        self.data: typing.Dict[typing.Tuple(int, int), MapData.Element] = {}
        self.history = collections.deque(maxlen=5000)
    
    def put(self, x: int, y: int, d: Element):
        self._appendHistory(MapData.History(x, y, self._put(x, y, d)))

    def _put(self, x: int, y: int, d: Element) -> Element:
        d.x, d.y = x, y
        old = (x, y) in self.data and self.data[(x, y)] or None
        self.data[(x, y)] = d
        return old

    def get(self, x: int, y: int) -> Element:
        return (x, y) in self.data and self.data[(x, y)] or None
       
    def delete(self, x: int, y: int):
        self._appendHistory(MapData.History(x, y, self._delete(x, y)))

    def _delete(self, x: int, y: int) -> Element:
        old = (x, y) in self.data and self.data[(x, y)] or None
        self.data[(x, y)] = None
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
            if h.svgId:
                self._put(h.x, h.y, MapData.Element(SvgSource.get(h.svgId)))
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
            blockSize = self.parent._blocksize()
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
