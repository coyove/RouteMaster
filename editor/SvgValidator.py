from os import read

from PyQt5 import QtGui
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget

from PyQt5 import QtSvg
from PyQt5.QtGui import QColor, QImage, QPainter


if __name__ == '__main__':
    import os
    app = QApplication([])
    win = QMainWindow()
    root = '../../block/'
    svg = QtSvg.QSvgRenderer(win)
    
    log = open('bad.log', 'w+')
    
    c = 0
    for f in os.listdir(root):
        if f.endswith('.svg'):
            # f = "BSicon_STR.svg"
            c = c + 1
            if c % 100 == 0:
                print(c)
                
            svg.load(root + f)
                
            # svg.load(root + f)
            img = QImage(500, 500, QImage.Format.Format_ARGB32)
            p = QPainter(img)
            p.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
            p.fillRect(0, 0, 500, 500, QColor(0, 0, 0, 0))
            svg.render(p)
            p.end()
            
            ok = False
            for x in range(img.width()):
                for y in range(img.height()):
                    tmp = QColor(img.pixel(x, y))
                    r, g, b, _ = tmp.getRgb()
                    if r or g or b:
                        # img.save("1.png")
                        ok = True
                        break
                else:
                    continue
                break
                
            if not ok:
                print(f)
                log.write(f + '\n')
                log.flush()
                
            # raise 1