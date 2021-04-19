from PyQt5 import QtCore, QtSvg
from PyQt5.QtGui import QColor, QFont, QFontMetrics, QPainter
from PyQt5.QtWidgets import QListView, QTableWidget, QTableWidgetItem, QWidget 
import os

class SvgSource:
    Manager = {}
    
    def get(id):
        return id in SvgSource.Manager and SvgSource.Manager[id] or None
    
    def __init__(self, parent, id, svgData: bytes) -> None:
        self.svgData = svgData
        self.svgId = id
        self._renderer = QtSvg.QSvgWidget(parent)
        self._renderer.load(svgData)
        self._renderer.setVisible(False)
        self._w = self._h = 0 # override sizeHint
        SvgSource.Manager[self.svgId] = self
        
    def overrideWidthHeight(self, w, h):
        self._w, self._h = w, h
        
    def width(self):
        return self._w or self._renderer.sizeHint().width() 
    
    def height(self):
        return self._h or self._renderer.sizeHint().height()
    
    def paint(self, x: int, y: int, w: int, h: int, p: QPainter):
        self._renderer.setFixedSize(w, h)
        p.translate(x, y)
        self._renderer.render(p, flags=QWidget.RenderFlag.DrawChildren)
        p.translate(-x, -y)
        
class SvgList(QTableWidget):
    def __init__(self, parent, root) -> None:
        super().__init__(parent=parent)
        # self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        item = QTableWidgetItem('zzz')
        item.setFlags(item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
        self.setRowCount(10)
        self.setColumnCount(2)
        self.setItem(1,1,item)
