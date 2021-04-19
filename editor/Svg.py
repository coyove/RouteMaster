from PyQt5 import QtSvg
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
        
    def width(self):
        return self._w or self._renderer.sizeHint().width() 
    
    def height(self):
        return self._h or self._renderer.sizeHint().height()
    
    def paint(self, x: int, y: int, w: int, h: int, p: QPainter):
        self._renderer.setFixedSize(w, h)
        p.translate(x, y)
        self._renderer.render(p, flags=QWidget.RenderFlag.DrawChildren)
        p.translate(-x, -y)
        
class SvgTextSource(SvgSource):
    class Align:
        Left = 1
        Center = 2
        Right = 3

    def __init__(self, parent, text: str, alignment: Align = Align.Center) -> None:
        id = 'text-' + str(hash(text))
        self.text = text
        self.alignment: SvgTextSource.Align = alignment
        super().__init__(parent, id, ''.encode('utf-8'))
    
    def height(self):
        return 32
    
    def width(self):
        font = QFont("monospace", 8)
        m = QFontMetrics(font)
        return m.horizontalAdvance(self.text)
        
    def paint(self, x: int, y: int, w: int, h: int, p: QPainter):
        fh = h // 4
        p.setFont(QFont("monospace", fh))
        # p.fillRect(x, y, w, h, QColor(0,0,0,100))
        p.drawText(x, y + h - (h - fh) // 2, self.text)

class SvgList(QTableWidget):
    def __init__(self, parent, root) -> None:
        super().__init__(parent=parent)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        item = QTableWidgetItem('zzz')
        self.setRowCount(10)
        self.setColumnCount(10)
        self.setItem(1,1,item)
