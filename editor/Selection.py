from PyQt5 import QtCore
from PyQt5.QtWidgets import QLabel
from MapData import MapData

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
        self.labels.append({ "data": data, "w": label})
        self.dedup[data.id] = True
        self.parent.selectionEvent(Selection.Add, data)
        
    def moveIncr(self, x, y, size):
        for l in self.labels:
            l: QLabel = l["w"]
            l.move(l.x() + x, l.y() + y)
            l.setFixedSize(size, size)

    def moveZoom(self, cx, cy, deltaScale):
        for l in self.labels:
            l: QLabel = l["w"]
            l.move(int((l.x() - cx) * deltaScale + cx), int((l.y() - cy) * deltaScale + cy))
            
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