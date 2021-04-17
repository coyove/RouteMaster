from math import trunc
import typing
from warnings import simplefilter
from PyQt5 import QtCore
from PyQt5.QtWidgets import QLabel
from MapData import MapCell, MapData
from PyQt5.QtGui import QColor, QMouseEvent, QPainter, QPainterPath, QPen, QPicture

class Selection:
    Add = 1
    Clear = 2
    
    class Block:
        def __init__(self, data: MapData.Element, pos: QtCore.QPoint, size: int) -> None:
            self.x, self.y = pos.x(), pos.y()
            self.size = size
            self.data = data
            
        def oddeven(self):
            return (self.x // self.size + self.y // self.size) % 2

    def __init__(self, parent) -> None:
        self.parent = parent
        self.labels: typing.List[Selection.Block] = []
        self.dedup = {}
        
    def paint(self, p: QPainter):
        d: DragController = self.parent.dragger
        dd = d.dragtonorm - d.startnorm
        x, y = dd.x(), dd.y()
        for l in self.labels:
            p.fillRect(l.x, l.y, l.size, l.size, QColor(255, 255, 0, l.oddeven() and 135 or 90))
            if x or y: # paint select-n-drag blocks if presented
                p.fillRect(l.x + x, l.y + y, l.size, l.size, QColor(255, 255, 0, l.oddeven() and 90 or 45))
        
    def addSelection(self, data: MapData.Element, pos: QtCore.QPoint, size):
        if not data.data:
            return
        if id(data) in self.dedup:
            return

        label = Selection.Block(data, pos, size)
        self.labels.append(label)
        self.dedup[id(data)] = label
        self.parent.selectionEvent(Selection.Add, data)
        
    def delSelection(self, data: MapData.Element):
        if not id(data) in self.dedup:
            return 
        x = self.dedup[id(data)]
        del self.dedup[id(data)]
        self.labels.remove(x)
        
    def moveIncr(self, x, y, size):
        for l in self.labels:
            l.size = size
            l.x, l.y = l.x + x, l.y + y

    def moveZoom(self, cx, cy, deltaScale):
        for l in self.labels:
            l.x = int((l.x - cx) * deltaScale + cx)
            l.y = int((l.y - cy) * deltaScale + cy)
        
    def move(self, dx, dy):
        self.parent.data.begin()
        d: MapData = self.parent.data
        for l in self.labels:
            dd = l.data
            d.delete(dd.x, dd.y)
            d.put(dd.x + dx, dd.y + dy, dd)
        self.clear()
            
    def clear(self):
        self.labels = self.labels[:0]
        self.dedup = {}
        self.parent.selectionEvent(Selection.Clear, None)
        
    def status(self):
        return "{}".format(len(self.labels))

class HoverController:
    def __init__(self, parent) -> None:
        self.parent = parent
        self.labels: typing.List[Selection.Block] = []
        
    def clear(self):
        self.labels = self.labels[:0]
        
    def hold(self, data: typing.List[Selection.Block]):
        self.labels = data
        
    def paint(self, p: QPainter):
        d: DragController = self.parent.dragger
        bs = self.parent._blocksize()
        x, y = d.dragtonorm.x(), d.dragtonorm.y()
        for l in self.labels:
            p.fillRect((l.x - self.labels[0].x ) * bs + x, (l.y - self.labels[0].y) * bs + y, bs, bs, QColor(100, 120, 120, 45))
    
    def end(self):
        if len(self.labels) == 0:
            return
        d: MapData = self.parent.data
        d.begin()

        dd: DragController = self.parent.dragger
        d1, _, _ = dd.parent.findCellUnder(None, QtCore.QPoint(dd.dragtox, dd.dragtoy))

        if d1:
            x, y = self.labels[0].x, self.labels[0].y
            for l in self.labels:
                d.put(l.x - x + d1.x, l.y - y + d1.y, l)

        self.clear()

class DragController:
    Size = 12

    def __init__(self, parent) -> None:
        self.parent = parent
        self.pen = QPen(QColor(100, 120, 120))
        self.pen.setWidth(3)
        self.reset()
        
    def reset(self):
        self.startx = 0
        self.starty = 0
        self.dragtox = 0
        self.dragtoy = 0
        self.dragtonorm = self.startnorm = QtCore.QPoint(0, 0)
        self.started = False
        self.visible = True
    
    def start(self, x: int, y: int, normalized: QtCore.QPoint):
        self.startx = self.dragtox = x
        self.starty = self.dragtoy = y
        self.startnorm = self.dragtonorm = normalized
        self.started = True
        
    def drag(self, x: int, y: int, normalized: QtCore.QPoint):
        self.dragtox = x
        self.dragtoy = y
        self.dragtonorm = normalized 
        
    def end(self):
        if not self.started:
            return 0, 0

        d0, _, _ = self.parent.findCellUnder(None, QtCore.QPoint(self.startx, self.starty))
        d1, _, _ = self.parent.findCellUnder(None, QtCore.QPoint(self.dragtox, self.dragtoy))

        self.reset()
        if d0 and d1:
            return d1.x - d0.x, d1.y - d0.y
        return 0, 0
        
    def paint(self, p: QPainter):
        if not self.started:
            return
        
        if not self.visible:
            return
        
        p.save()
        p.setPen(self.pen)
        p.drawLine(self.startx, self.starty, self.dragtox, self.dragtoy)

        p.setPen(QPen(QColor(0,0,0,0)))
        p.setBrush(QColor(100, 120, 120, 128))
        offset = 4
        size = DragController.Size + offset
        p.drawEllipse(self.startx - size / 2, self.starty - size / 2, size, size)
        p.drawEllipse(self.dragtox - size / 2, self.dragtoy - size / 2, size, size)

        p.setBrush(QColor(100, 120, 120))
        p.drawEllipse(self.startx - DragController.Size / 2, self.starty - DragController.Size / 2, DragController.Size, DragController.Size)
        p.drawEllipse(self.dragtox - DragController.Size / 2, self.dragtoy - DragController.Size / 2, DragController.Size, DragController.Size)

        p.restore()