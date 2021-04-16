from math import trunc
from PyQt5 import QtCore
from PyQt5.QtWidgets import QLabel
from MapData import MapCell, MapData
from PyQt5.QtGui import QColor, QMouseEvent, QPainter, QPainterPath

class Selection:
    Add = 1
    Clear = 2

    def __init__(self, parent) -> None:
        self.parent = parent
        self.labels = []
        self.dedup = {}
        
    def addSelection(self, data: MapData.Element, pos: QtCore.QPoint, size):
        if data.id in self.dedup:
            return

        label = QLabel(self.parent)
        label.move(pos)
        label.setFixedSize(size, size)
        label.setStyleSheet((int(pos.x() / size) + int(pos.y() / size)) % 2 and
            'background: rgba(255,255,0,135)' or
            'background: rgba(255,255,0,90)')
        label.show()
        l = { "data": data, "w": label}
        self.labels.append(l)
        print(self.dedup.keys())
        self.dedup[data.id] = l
        self.parent.selectionEvent(Selection.Add, data)
        
    def delSelection(self, data: MapData.Element):
        print("del", data.id, self.dedup.keys())
        if not data.id or not data.id in self.dedup:
            return 
        x = self.dedup[data.id]
        del self.dedup[data.id]
        self.parent.children().remove(x["w"])
        self.labels.remove(x)
        x["w"].deleteLater()
        x["w"].setVisible(False)
        
    def moveIncr(self, x, y, size):
        for l in self.labels:
            l: QLabel = l["w"]
            l.move(l.x() + x, l.y() + y)
            l.setFixedSize(size, size)

    def moveZoom(self, cx, cy, deltaScale):
        for l in self.labels:
            l: QLabel = l["w"]
            l.move(int((l.x() - cx) * deltaScale + cx), int((l.y() - cy) * deltaScale + cy))
        
    def move(self, dx, dy):
        d: MapData = self.parent.data
        for l in self.labels:
            dd: MapData.Element = l["data"]
            d.delete(dd.x, dd.y)
            d.put(dd.x + dx, dd.y + dy, dd)
        self.clear()
            
    def clear(self):
        for l in self.labels:
            l: QLabel = l["w"]
            self.parent.children().remove(l)
            l.deleteLater()
        self.labels = self.labels[:0]
        self.dedup = {}
        self.parent.selectionEvent(Selection.Clear, None)
        
    def status(self):
        return "{}".format(len(self.labels))

class HoverController:
    def __init__(self, parent) -> None:
        self.parent = parent
        self.pt = QtCore.QPoint(0, 0)
        self.size = 0
        
    def paint(self, p: QPainter):
        if self.size == 0:
            return
        p.fillRect(self.pt.x(), self.pt.y(), self.size, self.size, QColor(0, 0, 255, 60))
    
class DragController:
    Size = 16

    def __init__(self, parent) -> None:
        self.parent = parent
        self.startx = 0
        self.starty = 0
        self.dragtox = 0
        self.dragtoy = 0
        self.started = False
    
    def start(self, x: int, y: int):
        self.startx = x
        self.starty = y
        self.dragtox = x
        self.dragtoy = y
        self.started = True
        
    def drag(self, x: int, y: int):
        self.dragtox = x
        self.dragtoy = y
        
    def end(self, size):
        if not self.started:
            return 0, 0

        self.started = False
        d0, _, _ = self.parent.findCellUnder(None, QtCore.QPoint(self.startx, self.starty))
        d1, _, _ = self.parent.findCellUnder(None, QtCore.QPoint(self.dragtox, self.dragtoy))
        if d0 and d1:
            return d1.x - d0.x, d1.y - d0.y
        return 0, 0
        
    def paint(self, p: QPainter):
        if not self.started:
            return
        
        p.drawLine(self.startx, self.starty, self.dragtox, self.dragtoy)
        p.setBrush(QColor(0, 255, 255, 128))
        p.drawEllipse(self.startx - DragController.Size / 2, self.starty - DragController.Size / 2, DragController.Size, DragController.Size)
        p.drawEllipse(self.dragtox - DragController.Size / 2, self.dragtoy - DragController.Size / 2, DragController.Size, DragController.Size)