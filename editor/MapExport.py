from os import curdir
from MapData import MapCell, MapData
from PyQt5.QtWidgets import QInputDialog

from PyQt5.QtGui import QImage, QPainter

def exportMapDataImage(parent, fn: str, data: MapData, cells):
    # QInputDialog.getInt(parent=parent, title='Block size', label='Pixels', value=32, min=16, max
    bs = parent.mapview._blocksize()

    bounding = data.bbox()
    x0, y0 = bounding.x(), bounding.y()

    img = QImage(bs * bounding.width(), bs * bounding.height(), QImage.Format.Format_ARGB32)
    p = QPainter(img)
    drawed = set()
    p.save()
    p.translate(-x0 * bs - parent.mapview.viewOrigin[0], -y0 * bs - parent.mapview.viewOrigin[1])
    for row in cells:
        for cell in row:
            cell: MapCell
            if not cell or not cell.current:
                continue
            drawed.add((cell.current.x, cell.current.y))
            cell.paint(p)
    p.restore()

    for x, y in data.data:
        if (x, y) in drawed:
            continue
        d = data.data[(x, y)]
        x = x - x0
        y = y - y0
        d.src.paint(x * bs, y * bs, bs, bs, p)
        for s in d.cascades:
            s.paint(x * bs, y * bs, bs, bs, p)
    p.end()
    img.save(fn)

def exportMapDataMW(fn: str, data: MapData):
    pass