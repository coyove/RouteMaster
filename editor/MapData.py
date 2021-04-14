from PyQt5 import QtCore
from PyQt5.QtCore import QPoint
import PyQt5.QtSvg as QtSvg
from PyQt5.QtWidgets import QWidget

class MapData:
    class Element:
        id: str
        svgData: bytes

        def __init__(self, id = None, d = None) -> None:
            self.svgData = d
            self.id = id

    data1 = [] # Q1, include +x, include +y
    data2 = [] # Q2, exclude +y, include -x
    data3 = [] # Q3, exclude -x, include -y
    data4 = [] # Q4, exclude -y, exclude -x
    
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

    def put(self, x: int, y: int, d):
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

class MapCell(QtSvg.QSvgWidget):
    Base = 32

    class Positioning:
        Center = 1
        Left = 2
        LeftTop = 3
        LeftBottom = 4
        Top = 5
        Right = 6
        RightTop = 7
        RightBottom = 8
        Bottom = 9

    positioning: Positioning = Positioning.Center

    def __init__(self, parent) -> None:
        super().__init__(parent)
        # self.setStyleSheet("border: 1px solid blue")
        return 
        
    def deleteFrom(self, parent: QWidget):
        parent.children().remove(self)
        self.deleteLater()
        
    def loadResizeMove(self, data: MapData.Element, scale: float, x: int, y: int):
        self.current = data

        super().load(data.svgData)
        svgSize = self.sizeHint()
        w, h = int(svgSize.width() * scale), int(svgSize.height() * scale)
        
        self.posx, self.posy = x, y

        x = int(x - (w - MapCell.Base * scale) / 2)
        y = int(y - (h - MapCell.Base * scale) / 2)

        # super().move(x, y)
        # super().setFixedSize(w, h)
        super().setGeometry(x, y, w, h)

    def pos(self) -> QtCore.QPoint:
        return QtCore.QPoint(self.posx, self.posy)
