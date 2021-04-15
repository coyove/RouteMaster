from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtCore import QPoint, QRectF
from PyQt5.QtGui import QColor, QImage, QOpenGLContext, QPaintEvent, QPainter
import PyQt5.QtSvg as QtSvg
from PyQt5.QtWidgets import QWidget

class SvgSource:
    def __init__(self, parent, id, svgData: bytes) -> None:
        self.svgData = svgData
        self.svgId = id
        self._renderer = QtSvg.QSvgWidget(parent)
        self._renderer.load(svgData)
        self._renderer.setVisible(False)

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

    def __init__(self) -> None:
        self.data1 = [] # Q1, include +x, include +y
        self.data2 = [] # Q2, exclude +y, include -x
        self.data3 = [] # Q3, exclude -x, include -y
        self.data4 = [] # Q4, exclude -y, exclude -x
    
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
        d.x, d.y = x, y
        data, x, y = self._which(x, y)
        while len(data) <= y:
            data.append([])
        while len(data[y]) <= x:
            data[y].append(None)
        data[y][x] = d

    def get(self, x: int, y: int) -> Element:
        data, x, y = self._which(x, y)
        if len(data) <= y:
            return None
        if len(data[y]) <= x:
            return None
        return data[y][x]
       
    def delete(self, x: int, y: int):
        data, x, y = self._which(x, y)
        if len(data) <= y:
            return None
        if len(data[y]) <= x:
            return None
        data[y][x] = None

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
