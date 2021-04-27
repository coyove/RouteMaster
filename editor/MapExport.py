from os import curdir

from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtWidgets import QMessageBox

from MapData import MapCell, MapData


def exportMapDataPng(parent, fn: str, data: MapData):
    # QInputDialog.getInt(parent=parent, title='Block size', label='Pixels', value=32, min=16, max
    bs = parent.mapview._blocksize()

    bounding = data.bbox(includeText=True)
    x0, y0 = bounding.x(), bounding.y()

    img = QImage(bs * bounding.width(), bs * bounding.height(), QImage.Format.Format_ARGB32)
    p = QPainter(img)
    cell = MapCell(parent.mapview)
    for x, y in data.data:
        d = data.data[(x, y)]
        x = x - x0
        y = y - y0
        cell.loadResizeMove(d, parent.mapview.scale, x * bs, y * bs)
        cell.paint(p)
    p.end()
    img.save(fn)

# WIP
def exportMapDataSvg(parent, fn: str, data: MapData):
    bs = parent.mapview._blocksize()
    bounding = data.bbox(includeText=True)
    x0, y0 = bounding.x(), bounding.y()

    import re
    r = re.compile(r"<!.+>")
    buf = ['<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="{}" height="{}">'.format(bounding.width() * bs, bounding.height() * bs)]
    for x, y in data.data:
        d = data.data[(x, y)]
        x = x - x0
        y = y - y0
        buf.append(
            '<svg xmlns="http://www.w3.org/2000/svg" version="1.1" x="{}" y="{}" width="{}" height="{}" viewBox="0 0 500 500">'.format(x * bs, y * bs, bs, bs))
        s = r.sub('', d.src.source())
        buf.append(s.replace('<?', '<!--').replace('?>', '-->'))
        buf.append('</svg>')

    buf.append('</svg>')
    with open(fn, 'wb+') as f:
        f.write(''.join(buf).encode('utf-8'))
