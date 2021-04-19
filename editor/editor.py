import json
import math
import os
import random
from typing import ValuesView
import typing

import PyQt5.QtGui as QtGui
import PyQt5.QtSvg as QtSvg
from PyQt5 import QtCore
from PyQt5.QtWidgets import (QApplication, QGraphicsScale, QHBoxLayout, QLabel,
                             QMainWindow, QMessageBox, QPushButton, QSplitter,
                             QStatusBar, QVBoxLayout, QWidget,
                             qDrawBorderPixmap)

from Controller import DragController, HoverController, Selection
from Map import Map
from MapData import MapCell, MapData, SvgSource
from Property import Property
from Svg import SvgSearch

globalSvgSources: typing.List[SvgSource] = None

class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("RouteMaster")
  
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
        vbox.addWidget(QPushButton(self))

        main.setLayout(vbox)
        self.setCentralWidget(main)
        
        s = SvgSearch('../../block')
        globalSvgSources = []
        for icon in s.search("xSTR"):
            s = SvgSource(main, icon[0], icon[1])
            s.overrideSize(32, 32)
            globalSvgSources.append(s)
        
        splitter = QSplitter(QtCore.Qt.Orientation.Horizontal)
        # lv = SvgList(self, "block")
        splitter.addWidget(self.propertyPanel)
        self.mapview = Map(main, globalSvgSources)
        splitter.addWidget(self.mapview)
        splitter.setStretchFactor(1, 2)
        splitter.setSizes([100, 100])
        vbox.addWidget(splitter, 255)
        
        self.show()

app = QApplication([])
win = Window()
app.exec_()
