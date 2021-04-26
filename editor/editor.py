from MapExport import exportMapDataPng, exportMapDataSvg
from SvgPackage import load_package
import json
import time
import typing
import multiprocessing as mp
from zipfile import ZipInfo

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import (QApplication, QFileDialog, QGraphicsDropShadowEffect, QGraphicsScale,
                             QHBoxLayout, QLabel, QLineEdit, QMainWindow,
                             QMenu, QMessageBox, QPushButton, QSplitter,
                             QStatusBar, QVBoxLayout, QWidget)

from Common import APP_NAME, ICON_PACKAGE, PNG_POLYFILLS
from Map import Map
from MapData import MapData, MapDataElement, SvgSource
from Property import Property
from Svg import SvgBar, SvgSearch

globalSvgSources: typing.List[SvgSource] = None

class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.searcher = SvgSearch('block')
        SvgSource.Search = self.searcher
        SvgSource.Parent = self

        self.setWindowTitle(APP_NAME)
        self.setGeometry(0, 0, 800, 500)

        bar = QStatusBar(self)
        self.barPosition = QLabel(bar)
        bar.addWidget(self.barPosition, 1)
        self.barSelection = QLabel(bar)
        bar.addWidget(self.barSelection, 1)
        self.barZoom = QLabel(bar)
        bar.addWidget(self.barZoom, 1)
        self.barCursor = QLabel(bar)
        bar.addWidget(self.barCursor, 1)
        self.barHistory = QLabel(bar)
        bar.addWidget(self.barHistory, 1)
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
        self._updateCurrentFile('')
        splitter.addWidget(self.mapview)

        splitter.setStretchFactor(1, 2)
        splitter.setSizes([100, 100])
        vbox.addWidget(splitter, 255)
        
        self.topMenus = {}
        self._addMenu('&File', '&New', 'Ctrl+N', self.doNew)
        # self._addMenu('&File', '&New Window', 'Ctrl+Shift+N', lambda x: mpq.put(1))
        self._addMenu('&File', '-')
        self._addMenu('&File', '&Open', 'Ctrl+O', self.doOpen)
        self._addMenu('&File', '-')
        self._addMenu('&File', '&Save', 'Ctrl+S', self.doSave)
        self._addMenu('&File', '&Save As...', 'Ctrl+Shift+S', self.doSaveAs)
        self._addMenu('&File', '-')
        self._addMenu('&File', '&Export PNG...', '', lambda x: self.doExportPngSvg(png=True))
        self._addMenu('&File', 'E&xport SVG...', '', lambda x: self.doExportPngSvg(png=False))
        self._addMenu('&File', '-')
        self._addMenu('&File', '&Refresh Icons Package', '', lambda x: load_package(ICON_PACKAGE, force=True))

        self._addMenu('&Edit', '&Undo', '', lambda x: self.mapview.actUndoRedo())
        self._addMenu('&Edit', '&Redo', '', lambda x: self.mapview.actUndoRedo(redo=True))
        self._addMenu('&Edit', '-')
        self._addMenu('&Edit', '&Cut', '', lambda x: self.mapview.actCut())
        self._addMenu('&Edit', '&Copy', '', lambda x: self.mapview.actCopy())
        self._addMenu('&Edit', '&Paste', '', lambda x: self.mapview.actPaste())
        self._addMenu('&Edit', '-')
        self._addMenu('&Edit', '&Clear History', '', lambda x: self.mapview.data.clearHistory())
        self._addMenu('&Edit', '-')
        self._addMenu('&Edit', '&Select by Text', '', lambda x: self.mapview.actSelectByText())
        
        self._addMenu('&View', '&Center', '', lambda x: self.mapview.center())
        self._addMenu('&View', 'Center &Selected', 'Ctrl+Shift+H', lambda x: self.mapview.center(selected=True))
        self._addMenu('&View', '100% &Zoom', '', lambda x: self.mapview.center(resetzoom=True))

        self.propertyPanel.update()
        self.showMaximized()

        self.load('123.bsm')
        exportMapDataSvg(self, '11.svg', self.mapview.data)
        
    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        if not self._askSave():
            a0.ignore()
            return
        return super().closeEvent(a0)
        
    def updateSearches(self):
        results = self.searcher.search(self.searchBox.text())
        if not results:
            return
        self.searchResults.update(results)
        
    def ghostHoldSvgSource(self, s):
        self.mapview.ghostHold([MapDataElement(s)])
        
    def _askSave(self):
        if self.mapview.data.historyCap:
            ans = QMessageBox.question(self, "Save", "Save current file?",
                                       buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
            if ans == QMessageBox.StandardButton.Cancel:
                return False
            if ans == QMessageBox.StandardButton.Yes:
                self.doSave(True)
        return True
                
    def doNew(self, v):
        if not self._askSave():
            return
        d = self.mapview.data
        d.clearHistory()
        d.data = {}
        self.mapview.scale = 2
        self.mapview.center()
        self._updateCurrentFile('')
       
    def doOpen(self, v):
        if not self._askSave():
            return
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

    def doExportPngSvg(self, v=True, png=True):
        d = QFileDialog(self)
        fn, _ = d.getSaveFileName(filter='PNG File (*.png)' if png else 'SVG File (*.svg)')
        if not fn:
            return
        try:
            if png:
                exportMapDataPng(self, fn, self.mapview.data)
            else:
                exportMapDataSvg(self, fn, self.mapview.data)
            QMessageBox.information(self, 'Export', 'Successfully exported to {}'.format(fn))
        except Exception as e:
            QMessageBox(QMessageBox.Icon.Warning, 'Export', 'Failed to export {}: {}'.format(fn, e)).exec_()
            
    def load(self, fn: str):
        d: MapData = self.mapview.data
        with open(fn, 'rb') as f:
            fd = json.load(f)
            d.clearHistory()
            d.data = {}
            for c in fd['data']:
                el = MapDataElement.fromdict(c)
                if el:
                    d.data[(el.x, el.y)] = el
            # self.mapview.pan(0, 0)
            self.mapview.center()
            self._updateCurrentFile(fn)
    
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
            self._updateCurrentFile(fn)
            self.propertyPanel.update()
            
    def _updateCurrentFile(self, fn):
        self.currentFile = fn
        self.setWindowTitle(APP_NAME + " - " + (self.currentFile or '[Untitled]'))
        
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
        
QApplication.setStyle('fusion')
app = QApplication([])
load_package(ICON_PACKAGE)
win = Window()
app.exec_()
