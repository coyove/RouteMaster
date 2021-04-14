from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QStatusBar, QLabel
import PyQt5.QtSvg as QtSvg
import PyQt5.QtGui as QtGui
from PyQt5 import QtCore
import random
from MapData import MapData, MapCell

def mod(x, y):
    return x - int(x/y) * y

class Map(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.data = MapData()
        self.cellSize = 32

        for i in range(0, 100):
            x = int(random.random() * 20 - 10)
            y = int(random.random() * 20 - 10)
            self.data.put(x, y, """<svg height="32" width="32"> <text x="0" y="15" fill="green">{} {}</text>
                    <rect x="0" y="0" width="32" height="32" fill="transparent" stroke="#000"></rect>
            </svg>""".format(x,y))
            
        self.svgBoxes = []
        self.viewOrigin = [0, 0]
        self.pan(0, 0) # fill svgBoxes
        self.setMouseTracking(True)
        self.pressPos = None
        
    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        self.pan(0, 0)
        return super().resizeEvent(a0)
    
    def pan(self, dx, dy):
        offsetX = self.viewOrigin[0] = self.viewOrigin[0] + dx
        offsetY = self.viewOrigin[1] = self.viewOrigin[1] + dy
        rows = int(self.height() / self.cellSize) + 3
        cols = int(self.width() / self.cellSize) + 3
        for r in self.svgBoxes:
            while len(r) < cols:
                r.append(None)
        while len(self.svgBoxes) < rows:
            self.svgBoxes.append([None for x in range(cols)])
            
        for i in range(rows, len(self.svgBoxes)):
            for cell in self.svgBoxes[i]:
                if cell:
                    cell.deleteFrom(self)
        self.svgBoxes = self.svgBoxes[:rows]

        for r in self.svgBoxes:
            for i in range(cols, len(r)):
                if r[i]:
                    r[i].deleteFrom(self)
            r[cols:] = []
            
        sx = mod(offsetX, self.cellSize)
        sy = mod(offsetY, self.cellSize)
        for y in range(len(self.svgBoxes)):
            for x in range(len(self.svgBoxes[y])):
                tmp = self.data.get(x - int(offsetX / self.cellSize), y - int(offsetY / self.cellSize))
                cell: QtSvg.QSvgWidget = self.svgBoxes[y][x]
                if tmp:
                    if not cell:
                        cell = self._newSvg()
                        self.svgBoxes[y][x] = cell
                    cell.load(str.encode(tmp, 'utf-8'))
                    cell.move(x * self.cellSize + sx - self.cellSize, y * self.cellSize + sy - self.cellSize)
                else:
                    if cell:
                        cell.deleteFrom(self)
                        self.svgBoxes[y][x] = None
                
        self.parent().barPosition.setText(
            'x:{}({}) y:{}({})'.format(-offsetX, -int(offsetX / self.cellSize), offsetY, int(offsetY / self.cellSize)))

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        if a0.buttons() & QtCore.Qt.MouseButton.MidButton:
            self.pressPos = a0.pos()
        else:
            self.pressPos = None
        return super().mouseMoveEvent(a0)           

    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:
        if isinstance(self.pressPos, QtCore.QPoint):
            diff: QtCore.QPoint = a0.pos() - self.pressPos
            self.pressPos = a0.pos()
            self.pan(diff.x(), diff.y())
        return super().mouseMoveEvent(a0)
    
    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.pressPos = None
        return super().mouseReleaseEvent(a0)
    
    def wheelEvent(self, a0: QtGui.QWheelEvent) -> None:
        lastSize = self.cellSize
        if a0.angleDelta().y() > 0:
            self.cellSize = int(self.cellSize * 1.5)
        else:   
            self.cellSize = max(int(self.cellSize / 1.5), 16)
            
        for row in self.svgBoxes:
            for cell in row:
                if cell:
                    cell: QtSvg.QSvgWidget
                    cell.setFixedSize(self.cellSize, self.cellSize)

        c = a0.pos()
        self.viewOrigin[0] = int((self.viewOrigin[0] - c.x()) * self.cellSize / lastSize + c.x())
        self.viewOrigin[1] = int((self.viewOrigin[1] - c.y()) * self.cellSize / lastSize + c.y())
        self.pan(0, 0)
        return super().wheelEvent(a0)
    
    def _newSvg(self):
        # s = QLabel(self)
        # s.setText(str(random.random())[3:5])
        # return s
        s = MapCell(self)
        s.setFixedSize(self.cellSize, self.cellSize)
        s.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        s.show()
        return s

class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Python")
  
        self.setGeometry(0, 0, 500, 500)

        bar = QStatusBar(self)
        self.barPosition = QLabel(bar)
        bar.addWidget(self.barPosition)
        self.setStatusBar(bar)

        test = Map(self)
        self.setCentralWidget(test)     

        # show all the widgets
        self.show()
        
    def updatePosition(self, x, y):
        self.barPosition.setText('x:{} y:{}'.format(-x, y))

app = QApplication([])
win = Window()
app.exec_()
