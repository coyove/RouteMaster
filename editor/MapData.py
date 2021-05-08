import collections
import copy
import json
import math
import random
import sys
import typing

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QRect, QRectF, qDebug
from PyQt5.QtGui import QColor, QFont, QFontMetrics, QPainter, QPainterPath, QPen

from Common import BS
from Svg import SvgSource


class MapDataElement:
    def createWithXY(x, y, id):
        sid, fn = SvgSource.Search.guess(id[0] if isinstance(id, list) else id)
        if not sid and isinstance(id, list):
            for i in range(1, len(id)):
                sid, fn = SvgSource.Search.guess(id[i])
                if sid:
                    id = id[i+1:]
                    break
        if sid:
            el = MapDataElement(SvgSource.getcreate(sid, fn, BS, BS), x, y)
            if isinstance(id, list):
                for id in id[1:]:
                    sid, fn = SvgSource.Search.guess(id)
                    if sid:
                        el.cascades.append(SvgSource.getcreate(sid, fn, BS, BS))
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
        self.startXOffset = 0
        
    def valid(self):
        return self and self.src
    
    def __str__(self) -> str:
        return self.src and "({})".format(self.src.svgId) or "(empty)"
    
    def get(self, t):
        return getattr(self, t)
    
    def set(self, k, v):
        return setattr(self, k, v)
    
    def dup(self):
        tmp, tmpc = self.src, self.cascades
        self.src, self.cascades = None, None
        obj = copy.deepcopy(self)
        self.src, obj.src = tmp, tmp
        self.cascades, obj.cascades = tmpc, tmpc
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
            "startXOffset": self.startXOffset,
        }

    def fromdict(x):
        try:
            el = MapDataElement(SvgSource.get(x["svgId"]), x["x"], x["y"])
            el.cascades = list(filter(lambda x: x, list(map(lambda x: SvgSource.get(x), x["cascadeSvgIds"]))))
            el.text = x["text"]
            el.textPlacement = x["textPlacement"]
            el.textAlign = x["textAlign"]
            el.textSize = x["textSize"]
            el.textX = x["textX"]
            el.textY = x["textY"]
            el.textFont = x["textFont"]
            el.startXOffset = x.get("startXOffset", 0)
            if not el.src:
                qDebug(("fromdict invalid source: " + x["svgId"]).encode('utf-8'))
            return el
        except KeyError:
            qDebug(("fromdict invalid key: " + json.dumps(x)).encode('utf-8'))
            return None
    
    def pack(self):
        return json.dumps(self.todict())
    
    def unpack(data: str):
        try:
            return MapDataElement.fromdict(json.loads(data))
        except Exception as e:
            qDebug(('unpack ' + str(e) + ": " + data).encode("utf-8"))
            return None

    def textbbox(self, scale: float, x = 0, y = 0, measure=False):
        blockSize = BS * scale
        if self.textPlacement == 'c':
            pass
        elif self.textPlacement == 'l':
            x = x - blockSize
        elif self.textPlacement == 'r':
            x = x + blockSize
        elif self.textPlacement == 't':
            y = y - blockSize
        elif self.textPlacement == 'b':
            y = y + blockSize

        option = QtCore.Qt.AlignmentFlag.AlignCenter
        bb = int(1500 * scale)
        dx = int(self.textX * scale)
        dy = int(self.textY * scale)
        if self.textAlign == 'c':
            r = QRect(x - bb, y - bb, blockSize + bb * 2, blockSize + bb * 2) 
        elif self.textAlign == 'l':
            r = QRect(x, y - bb, blockSize + bb, blockSize + bb * 2) 
            option = QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter
        elif self.textAlign == 'r':
            r = QRect(x - bb, y - bb, blockSize + bb, blockSize + bb * 2) 
            option = QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter
        elif self.textAlign == 't':
            r = QRect(x - bb, y, blockSize + bb * 2, blockSize + bb) 
            option = QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignTop
        else: # self.textAlign == 'b':
            r = QRect(x - bb, y - bb, blockSize + bb * 2, blockSize + bb) 
            option = QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignBottom
        r.setX(r.x() + dx)
        r.setY(r.y() + dy)
        r.setWidth(r.width() + dx)
        r.setHeight(r.height() + dy)

        if measure:
            m = QFontMetrics(MapDataRenderer.FontsManager.get(self.textFont, int(self.textSize * scale)))
            r = m.boundingRect(r, option, self.text)
            # print(r)
            return r
        return r, option

    def calcActualWidthX(self, w, h):
        def adv(w, drawWidth, xOffsetPercent):
            xOffsetPercent = xOffsetPercent % 1
            return int(xOffsetPercent * w) + drawWidth
        lastXOffset = self.startXOffset
        right = 0
        right = max(right, adv(w, h * self.src._ratio, lastXOffset))
        lastXOffset = lastXOffset + self.src._ratio
        for s in self.cascades:
            right = max(right, adv(w, h * s._ratio, lastXOffset))
            lastXOffset = lastXOffset + s._ratio
        return right
    
class MapData: 
    def __init__(self, parent) -> None:
        self.parent = parent
        self.data = {}
        self.history = []
        self.historyCap = 0
        
    def clearHistory(self):
        self.history = []
        self.historyCap = 0
        self.parent.findMainWin().propertyPanel.update()
    
    def put(self, x: int, y: int, d: MapDataElement):
        self._appendHistory(self._put(x, y, d), d, x, y)

    def _put(self, x: int, y: int, d: MapDataElement) -> MapDataElement:
        d.x, d.y = x, y
        old = (x, y) in self.data and self.data[(x, y)] or None
        self.data[(x, y)] = d
        return old

    def get(self, x: int, y: int) -> MapDataElement:
        return (x, y) in self.data and self.data[(x, y)] or None
    
    def bbox(self, includeText=False) -> QRect:
        if not self.data:
            return QRect()
        maxx, maxy = -sys.maxsize, -sys.maxsize
        minx, miny = sys.maxsize, sys.maxsize
        def merge(x, y):
            nonlocal maxx, maxy, minx, miny
            maxx = max(maxx, x)
            maxy = max(maxy, y)
            minx = min(minx, x)
            miny = min(miny, y)
        for k in self.data:
            (x, y) = k
            merge(x, y)
            if includeText and self.data[k].text:
                r = self.data[k].textbbox(scale=1, measure=True)
                merge(math.ceil(r.x() / BS) - 1 + x, math.ceil(r.y() / BS) - 1 + y)
                merge(math.ceil((r.x() + r.width()) / BS) + 1 + x, math.ceil((r.y() + r.height()) / BS) + 1 + y)
        return QRect(minx, miny, maxx - minx + 1, maxy - miny + 1)
       
    def delete(self, x: int, y: int):
        self._appendHistory(self._delete(x, y), None, x, y)

    def _delete(self, x: int, y: int) -> MapDataElement:
        old = (x, y) in self.data and self.data[(x, y)] or None
        if (x, y) in self.data:
            del self.data[(x, y)]
        return old
    
    def _appendHistory(self, h, rev, delx = 0, dely = 0):
        hs = h is None and 'delete:{}:{}'.format(delx, dely) or h.pack() # rewind
        revs = rev is None and 'delete:{}:{}'.format(delx, dely) or rev.pack() # forward
        self._appendHistoryPacked(hs, revs)
        
    def _appendHistoryPacked(self, h: str, rev: str):
        self.history = self.history[:self.historyCap]
        self.history.append((h, rev))
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
        # print(h)
        if h.startswith('delete:'):
            xy = h[7:].split(':')
            self._delete(int(xy[0]), int(xy[1]))
        else:
            d = MapDataElement.unpack(h)
            self._put(d.x, d.y, d)

class MapDataRenderer:
    _selectedTextPen = QPen(QColor(0, 0, 255, 120)) 

    class FontsManager:
        cache = {}
        @classmethod
        def get(cls, name, size):
            key = hash(name) << 10 | size
            if key in cls.cache:
                return cls.cache[key]
            font = QFont(name, size)
            cls.cache[key] = font
            if len(cls.cache) > 100: # simple
                cls.cache.clear()
            return font
    
    def __init__(self, parent) -> None:
        self.current: MapDataElement = None
        self.parent = parent

    def _paint(s: MapDataElement, x, y, w, h, p: QPainter, ghost=False):
        lastXOffset = s.startXOffset
        s.src.paint(x, y, w, h, p, ghost=ghost and len(s.cascades) == 0, xOffsetPercent=lastXOffset)
        lastXOffset = lastXOffset + s.src._ratio
        for sc in s.cascades:
            # ghost: last one is the top most, so draw ghost overlay
            sc.paint(x, y, w, h, p, ghost=ghost and sc == s.cascades[-1], xOffsetPercent=lastXOffset)
            lastXOffset = lastXOffset + sc._ratio

    def _paintRect(s: MapDataElement, x, y, w, h, p: QPainter):
        w = s.calcActualWidthX(w, h)
        p.drawRect(x, y, w, h)
        p.fillRect(x, y, w, h, QColor(255, 255, 0, 90))
       
    def paint(data: MapDataElement, selected: bool, scale: float, x: int, y: int, p: QPainter):
        posx = x
        posy = y
        w, h = int(data.src.width() * scale), int(data.src.height() * scale)
        x = int(x - (w - BS * scale) / 2)
        y = int(y - (h - BS * scale) / 2)
        w, h = data.src.width() * scale, data.src.height() * scale
        MapDataRenderer._paint(data, x, y, w, h, p)
        if not data.text:
            return
        font = MapDataRenderer.FontsManager.get(data.textFont, int(data.textSize * scale))
        p.save()
        p.setFont(font)
        selected and p.setPen(MapDataRenderer._selectedTextPen)
        r, option = data.textbbox(scale, posx, posy)
        p.drawText(QRectF(r.x(), r.y(), r.width(), r.height()), data.text, option=QtGui.QTextOption(option))
        p.restore()