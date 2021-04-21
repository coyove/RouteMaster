import json
import time
from Common import APP_NAME, PNG_POLYFILLS
import typing

import PyQt5.QtGui as QtGui
import PyQt5.QtSvg as QtSvg
from PyQt5 import QtCore
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QGraphicsScale, QHBoxLayout, QLabel, QLineEdit,
                             QMainWindow, QMenu, QMessageBox, QPushButton, QSplitter,
                             QStatusBar, QVBoxLayout, QWidget,
                             qDrawBorderPixmap)

from Controller import DragController, HoverController, Selection
from Map import Map
from MapData import MapCell, MapData, SvgSource
from Property import Property
from Svg import SvgBar, SvgSearch

globalSvgSources: typing.List[SvgSource] = None

class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.searcher = SvgSearch('../../block')
        SvgSource.Search = self.searcher
        SvgSource.Parent = self

        self.setWindowTitle(APP_NAME)
        self.setGeometry(0, 0, 800, 500)

        bar = QStatusBar(self)
        self.barPosition = QLabel(bar)
        bar.addWidget(self.barPosition, 1)
        self.barSelection = QLabel(bar)
        bar.addWidget(self.barSelection, 1)
        self.setStatusBar(bar)

        main = QWidget(self)
        vbox = QVBoxLayout()
        vbox.setContentsMargins(0,0,0,0)
        
        self.propertyPanel = Property(main)

        self.searchBox = QLineEdit(self)
        self.searchBox.setPlaceholderText('Search blocks')
        self.searchBox.textChanged.connect(self.updateSearches)
        # self.searchBox.returnPressed.connect(self.searchBlocks)
        self.searchResults = SvgBar(self)
        vbox.addWidget(Property._genVBox(self, self.searchBox, self.searchResults, 8))

        main.setLayout(vbox)
        self.setCentralWidget(main)

        splitter = QSplitter(QtCore.Qt.Orientation.Horizontal)
        splitter.addWidget(self.propertyPanel)

        self.mapview = Map(main, globalSvgSources)
        self.currentFile = ''
        splitter.addWidget(self.mapview)

        splitter.setStretchFactor(1, 2)
        splitter.setSizes([100, 100])
        vbox.addWidget(splitter, 255)
        
        self.topMenus = {}
        self._addMenu('&File', '&Open', 'Ctrl+O', self.doOpen)
        self._addMenu('&File', '-')
        self._addMenu('&File', '&Save', 'Ctrl+S', self.doSave)
        self._addMenu('&File', '&Save As...', 'Ctrl+Shift+S', self.doSaveAs)

        self.propertyPanel.update()
        self.show()
        
    def updateSearches(self):
        results = self.searcher.search(self.searchBox.text())
        if not results:
            return
        self.searchResults.update(results)
        
    def ghostHoldSvgSource(self, s):
        self.mapview.ghostHold([MapData.Element(s)])
        
    def doOpen(self, v):
        d = QFileDialog(self)
        fn , _ = d.getOpenFileName(filter='BSM Files (*.bsm)')
        if not fn:
            return
        try:
            self.load(fn)
        except Exception as e:
            QMessageBox(QMessageBox.Icon.Warning, 'Open', 'Failed to open {}: {}'.format(fn, e)).exec_()
            
    def doSave(self, v):
        if not self.currentFile:
            d = QFileDialog(self)
            self.currentFile, _ = d.getSaveFileName()
            if not self.currentFile:
                return
        self.save(self.currentFile)
        
    def doSaveAs(self, v):
        d = QFileDialog(self)
        fn, _ = d.getSaveFileName(filter='BSM Files (*.bsm)')
        if not fn:
            return
        try:
            self.save(fn)
        except Exception as e:
            QMessageBox(QMessageBox.Icon.Warning, 'Save', 'Failed to save {}: {}'.format(fn, e)).exec_()
            
    def load(self, fn: str):
        d: MapData = self.mapview.data
        with open(fn, 'rb') as f:
            fd = json.load(f)
            d.clearHistory()
            d.data = {}
            for c in fd['data']:
                el = MapData.Element.fromdict(c)
                if el:
                    d.data[(el.x, el.y)] = el
            # self.mapview.pan(0, 0)
            self.mapview.center()
            self.currentFile = fn
            self.setWindowTitle(APP_NAME + " - " + self.currentFile)
    
    def save(self, fn: str):
        d: MapData = self.mapview.data
        with open(fn, 'w+') as f:
            z = []
            for xy in d.data:
                (x, y) = xy
                dd = d.data[xy]
                if dd.x != x or dd.y != y:
                    QtCore.qDebug("shouldn't happen: {}-{} {}-{}", x, y, dd.x, dd.y)
                    continue
                z.append(dd.todict())
            json.dump({
                "author": "test",
                "ts": int(time.time()),
                "data": z,
            }, f)
            d.clearHistory()
            self.currentFile = fn
            self.setWindowTitle(APP_NAME + " - " + self.currentFile)
        
    def _addMenu(self, top, text, shortcut = None, cb = None):
        if top in self.topMenus:
            m = self.topMenus[top]
        else:
            menuBar = self.menuBar()
            m = QMenu(top, self)
            menuBar.addAction(m.menuAction())
            self.topMenus[top] = m
        if text == '-':
            m.addSeparator()
            return
        fileOpen = m.addAction(text)
        if shortcut:
            fileOpen.setShortcut(shortcut)
        fileOpen.triggered.connect(cb)
        
# print(len(PNG_POLYFILLS))

QApplication.setStyle('fusion')
app = QApplication([])
win = Window()
app.exec_()
