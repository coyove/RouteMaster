from SvgList import SvgList
import math
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QStatusBar, QLabel, QSplitter
import PyQt5.QtSvg as QtSvg
import PyQt5.QtGui as QtGui
from PyQt5 import QtCore
import random
from MapData import MapData, MapCell
from Selection import Selection

def mod(x, y):
    return x - int(x/y) * y

class Map(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.data = MapData()
        self.scale = 2

        for i in range(0, 200):
            l = int(random.random() * 15 + 10)
            d = random.random() * math.pi * 2
            x, y = int(l * math.cos(d)), int(l * math.sin(d))
            if random.random() > 0.2:
                self.data.put(x, y, MapData.Element("{}-{}".format(x,y), """
                <svg height="48" width="48">
                    <text x="8" y="24" fill="green">{} {}</text>
                    <rect x="8" y="8" width="32" height="32" fill="transparent" stroke="#000"></rect>
                </svg>""".format(x,y).encode('utf-8')))
            else:
                self.data.put(x, y, MapData.Element("{}-{}".format(x,y), """
                <svg height="48" width="96">
                    <text x="8" y="24" fill="red">{} {}</text>
                    <rect x="8" y="8" width="32" height="32" fill="transparent" stroke="#000"></rect>
                </svg>""".format(x,y).encode('utf-8')))

        self.bg = QLabel(self)
        self.bg.setStyleSheet("background: white")
        self.bg.move(0, 0)
        self.selector = Selection(self)
        self.svgBoxes = []
        self.svgBoxesRecycle = []
        self.svgBoxesRecycleLock = QtCore.QMutex()
        t = QtCore.QTimer(self)
        t.timeout.connect(self.svgGc)
        t.start(30000)
        self.viewOrigin = [0, 0]
        self.pan(0, 0) # fill svgBoxes
        self.setMouseTracking(True)
        self.pressPos = None
        self.pressHoldSel = False
        
    def svgGc(self):
        self.svgBoxesRecycleLock.lock()
        for i in range(int(len(self.svgBoxesRecycle) / 2), len(self.svgBoxesRecycle)):
            self.svgBoxesRecycle[i].deleteFrom(self)
        self.svgBoxesRecycle = self.svgBoxesRecycle[:int(len(self.svgBoxesRecycle) / 2)]
        self.svgBoxesRecycleLock.unlock()
    
    def cacheSvgBoxLocked(self, cell):
        self.svgBoxesRecycle.append(cell)
        cell.setVisible(False)

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        self.bg.setFixedSize(self.width(), self.height())
        self.pan(0, 0)
        return super().resizeEvent(a0)
    
    def pan(self, dx, dy, noUpdate = False):
        blockSize = MapCell.Base * self.scale
        offsetX = self.viewOrigin[0] = self.viewOrigin[0] + dx
        offsetY = self.viewOrigin[1] = self.viewOrigin[1] + dy
        if noUpdate:
            return

        self.selector.moveIncr(dx, dy, blockSize)

        rows = int(self.height() / blockSize) + 3
        cols = int(self.width() / blockSize) + 3
        for r in self.svgBoxes:
            while len(r) < cols:
                r.append(None)
        while len(self.svgBoxes) < rows:
            self.svgBoxes.append([None for x in range(cols)])
            
        self.svgBoxesRecycleLock.lock()
        for i in range(rows, len(self.svgBoxes)):
            for cell in self.svgBoxes[i]:
                if cell:
                    self.cacheSvgBoxLocked(cell)
        self.svgBoxes = self.svgBoxes[:rows]

        for r in self.svgBoxes:
            for i in range(cols, len(r)):
                if r[i]:
                    self.cacheSvgBoxLocked(r[i])
                    
            r[cols:] = []
            
        sx = mod(offsetX, blockSize)
        sy = mod(offsetY, blockSize)

        for y in range(len(self.svgBoxes)):
            for x in range(len(self.svgBoxes[y])):
                tmp = self.data.get(x - int(offsetX / blockSize), y - int(offsetY / blockSize))
                cell: QtSvg.QSvgWidget = self.svgBoxes[y][x]
                if not tmp and cell:
                    self.svgBoxes[y][x] = None
                    self.cacheSvgBoxLocked(cell)
        self.svgBoxesRecycleLock.unlock()

        for y in range(len(self.svgBoxes)):
            for x in range(len(self.svgBoxes[y])):
                tmp = self.data.get(x - int(offsetX / blockSize), y - int(offsetY / blockSize))
                cell: QtSvg.QSvgWidget = self.svgBoxes[y][x]
                if tmp:
                    cell = cell or self._newSvg()
                    self.svgBoxes[y][x] = cell
                    cell.loadResizeMove(tmp, self.scale, x * int(blockSize) + sx - blockSize, y * int(blockSize) + sy - blockSize)
                
        self.findMainWin().barPosition.setText( 'x:{}({}) y:{}({})'.format(
            -offsetX, -int(offsetX / blockSize), offsetY, int(offsetY / blockSize)))
        
        self.selectionEvent()
        
    def findCellUnder(self, a0: QtGui.QMouseEvent):
        c = a0.pos()
        blockSize = int(MapCell.Base * self.scale)
        x_ = ((c.x() - self.viewOrigin[0]) / blockSize)
        y_ = ((c.y() - self.viewOrigin[1]) / blockSize)
        x, y = math.ceil(x_), math.ceil(y_)
        if x_ == x or y_ == y:
            return None, None, None

        d = self.data.get(x, y) or MapData.Element(id="{}-{}".format(x, y))

        sx = mod(self.viewOrigin[0], blockSize)
        sy = mod(self.viewOrigin[1], blockSize)
        ix = math.ceil((c.x() - sx) / blockSize) 
        iy = math.ceil((c.y() - sy) / blockSize)
        x2 = int((c.x() - sx) / blockSize) * blockSize + sx
        y2 = int((c.y() - sy) / blockSize) * blockSize + sy
        if iy >= len(self.svgBoxes) or ix >= len(self.svgBoxes[iy]):
            return None, None, None
        
        cell = self.svgBoxes[iy][ix]
        # print(d.id, x2, y2)
        return d, cell, QtCore.QPoint(x2, y2)
    
    def findMainWin(self):
        p = self.parent()
        while not isinstance(p, QMainWindow):
            p = p.parent()
        return p
    
    def selectionEvent(self, action=None, d=None):
        self.findMainWin().barSelection.setText(self.selector.status())

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        if a0.buttons() & QtCore.Qt.MouseButton.MidButton:
            self.pressPos = a0.pos()
            QApplication.setOverrideCursor(QtCore.Qt.CursorShape.DragMoveCursor)
        else:
            self.pressPos = None
            d, cell, pt = self.findCellUnder(a0)
            cell: MapCell
            if d and cell:
                self.selector.addSelection(d, cell.pos(), int(MapCell.Base * self.scale))
            elif d and a0.buttons() & QtCore.Qt.MouseButton.RightButton:
                self.selector.addSelection(d, pt, int(MapCell.Base * self.scale))
            else:
                self.selector.clear()
            self.pressHoldSel = True

        return super().mousePressEvent(a0)           

    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:
        if isinstance(self.pressPos, QtCore.QPoint):
            diff: QtCore.QPoint = a0.pos() - self.pressPos
            self.pressPos = a0.pos()
            self.pan(diff.x(), diff.y())
        elif self.pressHoldSel:
            d, cell, pt = self.findCellUnder(a0)
            cell: MapCell
            if d and cell:
                self.selector.addSelection(d, cell.pos(), int(MapCell.Base * self.scale))
            elif d and a0.buttons() & QtCore.Qt.MouseButton.RightButton:
                self.selector.addSelection(d, pt, int(MapCell.Base * self.scale))
            
        return super().mouseMoveEvent(a0)
    
    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.pressPos = None
        self.pressHoldSel = False
        QApplication.restoreOverrideCursor()
        self.pan(0, 0)
        return super().mouseReleaseEvent(a0)
    
    def wheelEvent(self, a0: QtGui.QWheelEvent) -> None:
        lastScale = self.scale
        if a0.angleDelta().y() > 0:
            self.scale = min(self.scale * 2, 32)
        else:   
            self.scale = max(self.scale / 2, 0.5)
            
        c = a0.pos()
        self.viewOrigin[0] = int((self.viewOrigin[0] - c.x()) * self.scale / lastScale + c.x())
        self.viewOrigin[1] = int((self.viewOrigin[1] - c.y()) * self.scale / lastScale + c.y())
        self.selector.moveZoom(c.x(), c.y(), self.scale / lastScale)
        self.pan(0, 0)
        return super().wheelEvent(a0)
    
    def _newSvg(self):
        if len(self.svgBoxesRecycle) > 0:
            self.svgBoxesRecycleLock.lock()
            cell: MapCell = self.svgBoxesRecycle[-1]
            self.svgBoxesRecycle = self.svgBoxesRecycle[:-1]
            cell.setVisible(True)
            self.svgBoxesRecycleLock.unlock()
            return cell
        s = MapCell(self)
        s.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        s.show()
        print(random.random())
        return s
    
class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("RouteMaster")
  
        self.setGeometry(0, 0, 500, 500)

        bar = QStatusBar(self)
        self.barPosition = QLabel(bar)
        bar.addWidget(self.barPosition, 1)
        self.barSelection = QLabel(bar)
        bar.addWidget(self.barSelection, 1)
        self.setStatusBar(bar)

        main = QWidget(self)
        vbox = QVBoxLayout()
        main.setLayout(vbox)
        vbox.setContentsMargins(0,0,0,0)
        self.setCentralWidget(main)
        
        splitter = QSplitter(QtCore.Qt.Orientation.Horizontal)
        lv = SvgList(self, "block")
        splitter.addWidget(lv)
        map = Map(main)
        splitter.addWidget(map)
        splitter.setStretchFactor(1, 2)
        splitter.setSizes([100, 100])
        vbox.addWidget(splitter)

        self.show()

app = QApplication([])
win = Window()
app.exec_()
