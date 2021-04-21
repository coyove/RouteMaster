import copy
import json
import sys
import typing

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QRect, QRectF, qDebug
from PyQt5.QtGui import QColor, QFont, QFontMetrics, QPainter, QPen

from Common import BS
from Svg import SvgSource


class MapData:
    class Element:
        def createFromIdsAt(parent, x, y, id, ids):
            id, fn = SvgSource.Search.guess(id)
            if id:
                el = MapData.Element(SvgSource.getcreate(id, fn, BS, BS), x, y)
                for id in ids:
                    id, fn = SvgSource.Search.guess(id)
                    if id:
                        el.cascades.append(SvgSource.getcreate(id, fn, BS, BS))
                return el
            return None

        def __init__(self, d: SvgSource = None, x = 0, y = 0) -> None:
            self.src = d
            self.cascades: typing.List[SvgSource] = []
            self.x, self.y = x, y
            self.text = ''
            self.textSize = 12
            self.textPlacement = 't'
            self.textAlign = 'c'
            self.textFont = 'Times New Roman'
            self.textX = self.textY = 0
            
        def valid(self):
            return self and self.src
        
        def __str__(self) -> str:
            return self.src and "({})".format(self.src.svgId) or "(empty)"
        
        def get(self, t):
            return getattr(self, t)
        
        def set(self, k, v):
            return setattr(self, k, v)
        
        def dup(self):
            tmp = self.src
            self.src = None
            obj = copy.deepcopy(self)
            self.src = tmp
            obj.src = tmp
            return obj
        
        def todict(self):
            if self.src and not self.src.svgId:
                qDebug('strange: empty svg source')
            return {
                "x": self.x,
                "y": self.y,
                "svgId": self.src and self.src.svgId or "",
                "cascadeSvgIds": list(map(lambda x: x.svgId, self.cascades)),
                "text": self.text,
                "textSize": self.textSize,
                "textPlacement": self.textPlacement,
                "textAlign": self.textAlign,
                "textFont": self.textFont,
                "textX": self.textX,
                "textY": self.textY,
            }

        def fromdict(x):
            el = MapData.Element(SvgSource.get(x["svgId"]), x["x"], x["y"])
            el.cascades = list(filter(lambda x: x, list(map(lambda x: SvgSource.Manager.get(x), x["cascadeSvgIds"]))))
            el.text = x["text"]
            el.textPlacement = x["textPlacement"]
            el.textAlign = x["textAlign"]
            el.textSize = x["textSize"]
            el.textX = x["textX"]
            el.textY = x["textY"]
            el.textFont = x["textFont"]
            return el
        
        def pack(self):
            return json.dumps(self.todict())
        
        def unpack(data):
            try:
                return MapData.Element.fromdict(json.loads(data))
            except Exception as e:
                qDebug('unpack:' + str(e))
                return None
            
    def __init__(self, parent) -> None:
        self.parent = parent
        self.data: typing.Dict[typing.Tuple(int, int), MapData.Element] = {}
        self.clearHistory()
        
    def clearHistory(self):
        self.history = []
        self.historyCap = 0
    
    def put(self, x: int, y: int, d: Element):
        self._appendHistory(self._put(x, y, d), d, x, y)

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
        self._appendHistory(self._delete(x, y), None, x, y)

    def _delete(self, x: int, y: int) -> Element:
        old = (x, y) in self.data and self.data[(x, y)] or None
        if (x, y) in self.data:
            del self.data[(x, y)]
        return old
    
    def _appendHistory(self, h: Element, rev: Element, delx = 0, dely = 0):
        hs = h is None and 'delete:{}:{}'.format(delx, dely) or h.pack() # rewind
        revs = rev is None and 'delete:{}:{}'.format(delx, dely) or rev.pack() # forward
        self.history = self.history[:self.historyCap]
        self.history.append((hs, revs))
        self.historyCap = self.historyCap + 1
    
    def begin(self):
        if len(self.history) and self.history[-1] == "null": # no conjucated Nones
            return
        self.history = self.history[:self.historyCap]
        self.history.append("null")
        self.historyCap = self.historyCap + 1
        
    def forward(self):
        metNull = False
        while self.historyCap < len(self.history):
            h = self.history[self.historyCap]
            if h == 'null':
                if metNull:
                    break
                metNull = True
            self.historyCap = self.historyCap + 1
            if h != 'null':
                self._play(h[1])
        self.parent.findMainWin().propertyPanel.update()
        
    def rewind(self):
        while self.historyCap > 0:
            h = self.history[self.historyCap - 1]
            self.historyCap = self.historyCap - 1
            if h == 'null':
                break
            self._play(h[0])
        self.parent.findMainWin().propertyPanel.update()
        
    def _play(self, h: str):
        print(h)
        if h.startswith('delete:'):
            xy = h[7:].split(':')
            self._delete(int(xy[0]), int(xy[1]))
        else:
            d = MapData.Element.unpack(h)
            self._put(d.x, d.y, d)

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
            self.current.src.paint(self.x, self.y, self.w, self.h, p)
            for s in self.current.cascades:
                s.paint(self.x, self.y, self.w, self.h, p)
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
                option = QtGui.QTextOption(QtCore.Qt.AlignmentFlag.AlignCenter)
                bb = int(1000 * self.currentScale)
                if self.current.textAlign == 'c':
                    r = QRectF(x - bb, y - bb, blockSize + bb * 2, blockSize + bb * 2) 
                elif self.current.textAlign == 'l':
                    r = QRectF(x, y - bb, blockSize + bb, blockSize + bb * 2) 
                    option = QtGui.QTextOption(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
                elif self.current.textAlign == 'r':
                    r = QRectF(x - bb, y - bb, blockSize + bb, blockSize + bb * 2) 
                    option = QtGui.QTextOption(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
                elif self.current.textAlign == 't':
                    r = QRectF(x - bb, y, blockSize + bb * 2, blockSize + bb) 
                    option = QtGui.QTextOption(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignTop)
                elif self.current.textAlign == 'b':
                    r = QRectF(x - bb, y - bb, blockSize + bb * 2, blockSize + bb) 
                    option = QtGui.QTextOption(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignBottom)
                r.setX(r.x() + int(self.current.textX * self.currentScale))
                r.setY(r.y() + int(self.current.textY * self.currentScale))
                p.drawText(r, text, option=option)
                p.restore()
        
    def loadResizeMove(self, data: MapData.Element, scale: float, x: int, y: int):
        self.current = data
        self.currentScale = scale
        # super().load(data.svgData)
        # svgSize = self.sizeHint()
        # w, h = int(svgSize.width() * scale), int(svgSize.height() * scale)
        self.w, self.h = int(data.src.width() * scale), int(data.src.height() * scale)
        
        self.posx, self.posy = x, y
        self.x = int(x - (self.w - BS * scale) / 2)
        self.y = int(y - (self.h - BS * scale) / 2)
