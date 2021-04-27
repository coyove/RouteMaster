from Common import WIN_WIDTH
import typing

from PyQt5 import QtCore
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import (QComboBox, QDialog, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QPushButton,
                             QScrollArea, QSizePolicy, QSpinBox, QTextEdit,
                             QVBoxLayout, QWidget)

from MapData import MapData, MapDataElement
from Svg import SvgBar, SvgSearch, SvgSource


class Property(QWidget):
    def _title(self, t):
        l = QLabel(t, self)
        l.setStyleSheet("font-weight: bold")
        return l 

    def __init__(self, parent: typing.Optional['QWidget']):
        super().__init__(parent=parent)
        self.scrollView = QScrollArea(self)
        self.scrollView.setWidgetResizable(True)
        self.scrollView.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.textAttr = QWidget(self)
        self.textAttr.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.textAttrBox = QVBoxLayout()
        self.textAttr.setLayout(self.textAttrBox)
        
        self.cascades = SvgBar(self)
        self.cascades.setVisible(False)
        self.cascades.onDelete = self.deleteCascade
        self.cascades.onDrag = self.resortCascade
        self.textAttrBox.addWidget(self.cascades)
        
        self.svgId = QLabel('N/A', self)
        self.textAttrBox.addWidget(self._title('Type'))
        self.textAttrBox.addWidget(self.svgId)

        self.textAttrBox.addWidget(self._title('Text'))
        self.text = QTextEdit(self)
        self.text.textChanged.connect(self.textChanged)
        self.text.installEventFilter(self)
        self.textAttrBox.addWidget(self.text)
        
        self.textFont = QComboBox(self)
        fontFamilies = QFontDatabase()
        for s in fontFamilies.families():
            self.textFont.addItem(s)
        self.textFont.currentIndexChanged.connect(self.fontChanged)
        self.textFont.setEditable(True)
        
        self.textSize = QComboBox(self)
        for i in range(8, 150, 1):
            if i <= 32:
                self.textSize.addItem(str(i))
            elif i <= 80 and i % 2 == 0:
                self.textSize.addItem(str(i))
            elif i % 10 == 0:
                self.textSize.addItem(str(i))
        self.textSize.currentIndexChanged.connect(self.sizeChanged)
        self.textSize.setEditable(True)
        self._addBiBoxInTextAttrBox(self._title("Font Family"), self.textFont, self._title("Font Size"), self.textSize)
        
        self.textAlign = QComboBox(self)
        self.textPlace = QComboBox(self)
        for c in [self.textAlign, self.textPlace]:
            c.addItem('Center', 'c')
            c.addItem('Top', 't')
            c.addItem('Bottom', 'b')
            c.addItem('Left', 'l')
            c.addItem('Right', 'r')
        self.textAlign.currentIndexChanged.connect(self.alignChanged)
        self.textPlace.currentIndexChanged.connect(self.placeChanged)
        self._addBiBoxInTextAttrBox(self._title("Alignment"), self.textAlign, self._title("Placement"), self.textPlace)
        
        self.textX = QSpinBox(self)
        self.textY = QSpinBox(self)
        for c in [self.textX, self.textY]:
            c.setValue(0)
            c.setMinimum(-1e5)
            c.setMaximum(1e5)
        self.textX.valueChanged.connect(lambda e: self.offsetChanged('x', e))
        self.textY.valueChanged.connect(lambda e: self.offsetChanged('y', e))
        self._addBiBoxInTextAttrBox(self._title("Offset X"), self.textX, self._title("Offset Y"), self.textY)

        # self.setLayout(self.textAttrBox)
        self.scrollView.setWidget(self.textAttr)
        box = QVBoxLayout()
        box.addWidget(self.scrollView)
        box.setContentsMargins(0, 0, 0, 0)
        self.setLayout(box)

        self.show()
        self.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        
        self.updating = False
        
    def _genVBox(p, w1, w2, m=0):
        placeAttr = QWidget(p)
        placeAttrBox = QVBoxLayout()
        placeAttrBox.setContentsMargins(m, m, m, m)
        placeAttr.setLayout(placeAttrBox)
        placeAttrBox.addWidget(w1)
        placeAttrBox.addWidget(w2)
        return placeAttr
    
    def eventFilter(self, a0, a1: QtCore.QEvent) -> bool:
        if a1.type() == QtCore.QEvent.FocusIn and a0 is self.text:
            self.findMainWin().mapview.data.begin()
            self.oldTextStore = []
            for x in self.selection():
                self.oldTextStore.append(x.dup())
        if a1.type() == QtCore.QEvent.FocusOut and a0 is self.text:
            for x in self.selection():
                self._getMapData()._appendHistory(self.oldTextStore.pop(0), x)
            self.oldTextStore.clear()
        return super().eventFilter(a0, a1)

    def _addBiBoxInTextAttrBox(self, t1, w1, t2, w2):
        placeAttr = QWidget(self)
        placeAttrBox = QHBoxLayout()
        placeAttrBox.setContentsMargins(0, 0, 0, 0)
        placeAttr.setLayout(placeAttrBox)
        placeAttrBox.addWidget(Property._genVBox(self, t1, w1))
        placeAttrBox.addWidget(Property._genVBox(self, t2, w2))
        self.textAttrBox.addWidget(placeAttr)
        
    def textChanged(self):
        for x in self.selection():
            x.text = self.text.toPlainText()
        self.findMainWin().mapview.pan(0, 0)

    def _getMapData(self) -> MapData:
        return self.findMainWin().mapview.data
        
    def deleteCascade(self, idx: int):
        self._getMapData().begin()
        item = self.selection()[0]
        old = item.pack()
        if idx == 0:
            item.src = item.cascades[0]
            item.cascades = item.cascades[1:]
        else:
            item.cascades = item.cascades[:idx-1] + item.cascades[idx-1+1:]
        self._getMapData()._appendHistoryPacked(old, item.pack())
        self.findMainWin().mapview.setFocus()
        self.update()

    def resortCascade(self, fr: int, to: int):
        self._getMapData().begin()
        item: MapDataElement = self.selection()[0]
        old = item.pack()
        if to == 0:
            fr = fr - 1
            old = item.src
            item.src = item.cascades[fr]
            item.cascades = [old] + item.cascades[:fr] + item.cascades[fr + 1:]
        elif fr == 0:
            old = item.src
            item.src = item.cascades[0]
            item.cascades = item.cascades[1:to] + [old] + item.cascades[to:]
        else:
            fr, to = fr - 1, to - 1
            fold = item.cascades[fr]
            item.cascades = item.cascades[:fr] + item.cascades[fr + 1:]
            item.cascades = item.cascades[:to] + [fold] + item.cascades[to:]
        self._getMapData()._appendHistoryPacked(old, item.pack())
        self.findMainWin().mapview.setFocus()
        self.update()
        
    def _foreach(self, f):
        mainData = self.findMainWin().mapview.data
        mainData.begin()
        for x in self.selection():
            old = x.dup()
            f(x)
            # print(old.pack(), x.pack())
            mainData._appendHistory(old, x)
        self.findMainWin().mapview.pan(0, 0)
        
    def fontChanged(self, e):
        self._foreach(lambda x: x.set("textFont", self.textFont.itemText(e)))
        
    def offsetChanged(self, t, v):
        self._foreach(lambda x: x.set(t == 'x' and 'textX' or 'textY', v))
        
    def sizeChanged(self, e):
        self._foreach(lambda x: x.set("textSize", int(self.textSize.itemText(e))))
        
    def alignChanged(self, e):
        self._foreach(lambda x: x.set("textAlign", self.textAlign.itemData(e)))
        
    def placeChanged(self, e):
        self._foreach(lambda x: x.set("textPlacement", self.textPlace.itemData(e)))
        
    def findMainWin(self):
        p = self.parent()
        while not isinstance(p, QMainWindow):
            p = p.parent()
        return p
    
    def selection(self):
        if self.updating:
            return []
        return list(map(lambda l: l.data, self.findMainWin().mapview.selector.labels))
    
    def update(self):
        data = self.findMainWin().mapview.data
        self.findMainWin().barHistory.setText('{}@{}'.format(data.historyCap, len(data.history)))
        self.findMainWin().barHistory.setStyleSheet(data.historyCap and "background: #80f0f000" or "")
        
        def toggle(v):
            for k in self.__dict__: # disbale all widgets
                w = self.__dict__[k]
                if isinstance(w, QWidget) and w != self.scrollView:
                    w.setEnabled(v)

        toggle(False)
        self.cascades.setVisible(False)

        items = self.selection()
        if not items:
            self.svgId.setText("N/A")
            return
        toggle(True)

        e = items[-1]
        self.updating = True
        self.svgId.setText(e.src.svgId)
        if e.cascades and len(items) == 1:
            self.cascades.update([(e.src.svgId, SvgSource.Search.fullpath(e.src.svgId))] + list(
                map(lambda x: (x.svgId, SvgSource.Search.fullpath(x.svgId)), e.cascades)))
            self.cascades.setVisible(True)
        self.text.setText(e.text)
        self.textFont.setEditText(e.textFont)
        self.textSize.setEditText(str(e.textSize))
        self._setAP(self.textAlign, e.textAlign)
        self._setAP(self.textPlace, e.textPlacement)
        self.updating = False
        
    def _setAP(self, w: QComboBox, d):
        for i in range(0, w.count()):
            if w.itemData(i) == d:
                w.setCurrentIndex(i)
                break

class FileProperty(QDialog):
    def __init__(self, parent: typing.Optional[QWidget], meta: dict) -> None:
        super().__init__(parent=parent)
        self.meta = meta
        box = QVBoxLayout(self)
        box.addWidget(QLabel('Author'))
        self.author = QLineEdit(self)
        self.author.setText(meta.get("author"))
        box.addWidget(self.author)

        self.desc = QTextEdit(self)
        self.desc.setText(meta.get("desc"))
        box.addWidget(QLabel('Description'))
        box.addWidget(self.desc, 20)

        data: MapData = parent.mapview.data
        missings = []
        for v in data.data.values():
            if not v.src.svgId.lower() in SvgSource.Search.files:
                missings.append(v.src.svgId)
            for s in v.cascades:
                if not s.svgId.lower() in SvgSource.Search.files:
                    missings.append(s.svgId)

        if missings:
            box.addWidget(QLabel('Missing Blocks'))
            self.missing = QTextEdit(self)
            self.missing.setReadOnly(True)
            self.missing.setStyleSheet("background: transparent")
            self.missing.setText('\n'.join(missings))
            box.addWidget(self.missing, 1)

        self.ok = QPushButton("OK", self)
        self.ok.clicked.connect(self.onOK)
        box.addWidget(self.ok)

        self.setFixedWidth(WIN_WIDTH)
    
    def onOK(self, v):
        self.meta["author"] = self.author.text()
        self.meta["desc"] = self.desc.toPlainText()
        self.close()