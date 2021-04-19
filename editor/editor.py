from Map import Map
import typing
from Property import Property
from typing import ValuesView
from Svg import SvgList
import math
from PyQt5.QtWidgets import QApplication, QGraphicsScale, QHBoxLayout, QMainWindow, QMessageBox, QVBoxLayout, QWidget, QStatusBar, QLabel, QSplitter, qDrawBorderPixmap
import PyQt5.QtSvg as QtSvg
import PyQt5.QtGui as QtGui
from PyQt5 import QtCore
import random
from MapData import MapData, MapCell, SvgSource
from Controller import DragController, HoverController, Selection
   
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
        # vbox.addWidget(self.propertyPanel, 1)

        main.setLayout(vbox)
        self.setCentralWidget(main)
        
        splitter = QSplitter(QtCore.Qt.Orientation.Horizontal)
        # lv = SvgList(self, "block")
        splitter.addWidget(self.propertyPanel)
        self.mapview = Map(main)
        splitter.addWidget(self.mapview)
        splitter.setStretchFactor(1, 2)
        splitter.setSizes([100, 100])
        vbox.addWidget(splitter, 255)
        
        self.show()
        
app = QApplication([])
win = Window()
app.exec_()
