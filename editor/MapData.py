import collections
import sys
import json
import copy
import typing

from PyQt5 import QtCore
from PyQt5 import QtGui

from PyQt5.QtGui import QColor, QFont, QFontMetrics, QPainter, QPen
from PyQt5.QtCore import QRect, QRectF, qDebug
from PyQt5.QtWidgets import QMessageBox

from Svg import SvgSource


class MapData:
    class Element:
        def __init__(self, d: SvgSource = None, x = 0, y = 0) -> None:
            self.data = d
            self.x = x
            self.y = y
            self.text = ''
            self.textSize = 12
            self.textPlacement = 't'
            self.textAlign = 'c'
            self.textX = 0
            self.textY = 0
            self.textFont = 'Times New Roman'
            
        def valid(self):
            return self and self.data
        
        def __str__(self) -> str:
            return self.data and "({})".format(self.data.svgId) or "(empty)"
        
        def get(self, t):
            return getattr(self, t)
        
        def set(self, k, v):
            return setattr(self, k, v)
        
        def dup(self):
            tmp = self.data
            self.data = None
            obj = copy.deepcopy(self)
            self.data = tmp
            obj.data = tmp
            return obj
        
        def pack(self):
            return json.dumps({
                "cellX": self.x,
                "cellY": self.y,
                "svgId": self.data and self.data.svgId or "0",
                "text": self.text,
                "textSize": self.textSize,
                "textPlacement": self.textPlacement,
                "textAlign": self.textAlign,
                "textFont": self.textFont,
                "textX": self.textX,
                "textY": self.textY,
            })
        
        def unpack(data):
            try:
                x = json.loads(data)
                el = MapData.Element(SvgSource.get(x["svgId"]), x["cellX"], x["cellY"])
                el.text = x["text"]
                el.textPlacement = x["textPlacement"]
                el.textAlign = x["textAlign"]
                el.textSize = x["textSize"]
                el.textX = x["textX"]
                el.textY = x["textY"]
                el.textFont = x["textFont"]
                return el
            except Exception as e:
                qDebug('unpack:' + data)
                return None
            
    def __init__(self, parent) -> None:
        self.parent = parent
        self.data: typing.Dict[typing.Tuple(int, int), MapData.Element] = {}
        self.history = collections.deque(maxlen=5000)
    
    def put(self, x: int, y: int, d: Element):
        self._appendHistory(self._put(x, y, d), x, y)

    def _put(self, x: int, y: int, d: Element) -> Element:
        d.x, d.y = x, y
        old = (x, y) in self.data and self.data[(x, y)] or None
        self.data[(x, y)] = d
        return old

    def get(self, x: int, y: int) -> Element:
        return (x, y) in self.data and self.data[(x, y)] or None
    
    def bbox(self) -> QRect:
        maxx, maxy = -sys.maxsize, -sys.maxsize
        minx, miny = sys.maxsize, sys.maxsize
        for k in self.data:
            (x, y) = k
            maxx = max(maxx, x)
            maxy = max(maxy, y)
            minx = min(minx, x)
            miny = min(miny, y)
        return QRect(minx, miny, maxx - minx, maxy - miny)
       
    def delete(self, x: int, y: int):
        self._appendHistory(self._delete(x, y), x, y)

    def _delete(self, x: int, y: int) -> Element:
        old = (x, y) in self.data and self.data[(x, y)] or None
        self.data[(x, y)] = None
        return old
    
    def _appendHistory(self, h: Element, delx = 0, dely = 0):
        if h is None:
            self.history.append('delete:{}:{}'.format(delx, dely))
        else:
            self.history.append(h.pack())
    
    def begin(self):
        if len(self.history) and self.history[-1] == "null": # no conjucated Nones
            return
        self.history.append("null")
        
    def rewind(self):
        while len(self.history):
            h: str = self.history.pop()
            if h == 'null':
                break
            if h.startswith('delete:'):
                xy = h[7:].split(':')
                self._delete(int(xy[0]), int(xy[1]))
            else:
                d = MapData.Element.unpack(h)
                self._put(d.x, d.y, d)
        self.parent.findMainWin().propertyPanel.update()

class MapCell:
    Base = 32
    selectedTextPen = QPen(QColor(0, 0, 255, 120)) 
    
    def __init__(self, parent) -> None:
        self.current: MapData.Element = None
        self.currentScale = 1.0
        self.moving = False
        self.parent = parent
        
    def paint(self, p: QPainter): 
        blockSize = self.parent._blocksize()
        if self.moving and self.parent.currentData != self.current:
            p.drawRect(self.posx, self.posy, blockSize, blockSize)
        elif self.current:
            self.current.data.paint(self.x, self.y, self.w, self.h, p)
            if self.current.text:
                font = QFont(self.current.textFont, int(self.current.textSize * self.currentScale))
                p.save()
                p.setFont(font)
                
                x, y = self.posx, self.posy
                if self.current.textPlacement == 'c':
                    pass
                elif self.current.textPlacement == 'l':
                    x = x - blockSize
                elif self.current.textPlacement == 'r':
                    x = x + blockSize
                elif self.current.textPlacement == 't':
                    y = y - blockSize
                elif self.current.textPlacement == 'b':
                    y = y + blockSize
                    
                if self.current == self.parent.currentData:
                    p.setPen(MapCell.selectedTextPen)

                text = self.current.text
                if self.current.textAlign == 'c':
                    r = QRectF(x + self.current.textX - 1000, y + self.current.textY - 1000, blockSize + 2000, blockSize + 2000) 
                    p.drawText(r, text, option=QtGui.QTextOption(QtCore.Qt.AlignmentFlag.AlignCenter))
                elif self.current.textAlign == 'l':
                    r = QRectF(x + self.current.textX, y + self.current.textY - 1000, blockSize + 1000, blockSize + 2000) 
                    p.drawText(r, text, option=QtGui.QTextOption(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter))
                elif self.current.textAlign == 'r':
                    r = QRectF(x + self.current.textX - 1000, y + self.current.textY - 1000, blockSize + 1000, blockSize + 2000) 
                    p.drawText(r, text, option=QtGui.QTextOption(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter))
                elif self.current.textAlign == 't':
                    r = QRectF(x + self.current.textX - 1000, y + self.current.textY, blockSize + 2000, blockSize + 1000) 
                    p.drawText(r, text, option=QtGui.QTextOption(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignTop))
                elif self.current.textAlign == 'b':
                    r = QRectF(x + self.current.textX - 1000, y + self.current.textY - 1000, blockSize + 2000, blockSize + 1000) 
                    p.drawText(r, text, option=QtGui.QTextOption(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignBottom))
                p.restore()
        
    def loadResizeMove(self, data: MapData.Element, scale: float, x: int, y: int):
        self.current = data
        self.currentScale = scale
        # super().load(data.svgData)
        # svgSize = self.sizeHint()
        # w, h = int(svgSize.width() * scale), int(svgSize.height() * scale)
        self.w, self.h = int(data.data.width() * scale), int(data.data.height() * scale)
        
        self.posx, self.posy = x, y
        self.x = int(x - (self.w - MapCell.Base * scale) / 2)
        self.y = int(y - (self.h - MapCell.Base * scale) / 2)
