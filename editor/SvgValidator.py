import sys
import os

from PyQt5 import QtCore, QtGui, QtSvg, QtWidgets
from PyQt5.QtGui import QColor, QImage, QPainter, qAlpha
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget

from Common import BLOCK_DIR, InkscapePath


def convertpng(svg):
    if os.path.exists(InkscapePath()):
        if sys.platform == 'win32':
            c = InkscapePath() + " --export-type png -h 128 \"" + svg + "\""
        else:
            c = InkscapePath() + " --export-type png -h 128 '" + svg.replace("'", "\\'") + "'"
        os.system(c)
    else:
        QtCore.qDebug("SvgSource convert: inkscape not found")

if __name__ == '__main__':
    import os
    app = QApplication([])
    win = QMainWindow()
    root = BLOCK_DIR
    svg = QtSvg.QSvgWidget(win)

    if True:
        for f in os.listdir(root):
            if f.endswith('.svg'):
                with open(root + "/" + f, 'rb+') as f:
                    b = f.read()
                    idx = b.find('<'.encode('utf-8'))
                    idx2 = b.rfind('>'.encode('utf-8'))
                    if idx != 0 or idx2 != len(b) - 1:
                        b = b[idx:idx2 + 1]
                        f.seek(0)
                        f.write(b)
                        f.truncate(len(b))
                        print(f.name, idx, idx2)
        sys.exit(0)

    log = open('bad.log', 'r+')

    if False:
        for f in os.listdir(root):
            if f.endswith('.png') or not f.startswith("BSicon"):
                os.remove(root + "/" + f)
        i = 0
        for line in log.readlines():
            line = line.strip()
            if not line:
                continue
            os.system("/usr/local/bin/Inkscape --export-type png -h 128 '" + (root + "/" + line).replace("'", "'\\''") + "'")
            i = i + 1
            print(i, line)
        sys.exit(0)
    
    c = 0
    for f in os.listdir(root):
        if f.endswith('.svg'):
            # f = "BSicon_LSTR.svg"
            c = c + 1
            if c % 100 == 0:
                print(c)
                
            svg.load(root + "/" + f)
                
            # svg.load(root + f)
            img = QImage(500, 500, QImage.Format.Format_ARGB32)
            p = QPainter(img)
            p.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
            p.fillRect(0, 0, 500, 500, QColor(0, 0, 0, 0))
            p.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
            svg.setFixedSize( 500, 500)
            svg.render(p, flags=QtSvg.QSvgWidget.RenderFlag.DrawChildren)
            p.end()
            
            ok = False
            # img.save("1.png")
            for x in range(img.width()):
                for y in range(img.height()):
                    tmp = img.pixel(x, y)
                    a = qAlpha(tmp)
                    if a:
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
