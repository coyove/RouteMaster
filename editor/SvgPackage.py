import os
from os.path import join
import re
from urllib import request

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import (QApplication, QFileDialog, QLabel, QMainWindow,
                             QProgressBar, QVBoxLayout, QWidget)

from Common import APP_NAME, BLOCK_DIR, TR, WIN_WIDTH
from Svg import SvgSearch, SvgSource, _quote


class Loader(QMainWindow):
    Single = None

    def __init__(self):
        super().__init__(flags=QtCore.Qt.WindowType.WindowCloseButtonHint|QtCore.Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowTitle(APP_NAME)
        self.setMaximumWidth(WIN_WIDTH * 2)
        self.show()

        w = QWidget(self)
        box = QVBoxLayout()
        w.setLayout(box)

        self.bar = QProgressBar(w)
        self.bar.show()
        self.bar.setRange(0, 0)

        box.addWidget(QLabel(TR("__download_icons__")), 1)
        self.progress = QLabel('0')
        box.addWidget(self.progress)
        box.addWidget(self.bar, 1)

        self.setCentralWidget(w) 
        self.setVisible(False)
        self.tasks = set()
        Loader.Single = self

    def addTask(self, fn: str):
        if fn in self.tasks:
            return
        self.tasks.add(fn)
        loading = LoadTask(self, fn)
        loading.start()
        self.setVisible(True)
        self.updateProgress()
        self.bar.setMaximum(self.bar.maximum() + 1)
        loading.taskFinished.connect(lambda: self.onComplete(fn))

    def updateProgress(self):
        self.progress.setText('({}) -> {}'.format(len(self.tasks), '/'.join(self.tasks)))

    def onComplete(self, fn: str) -> None:
        self.tasks.remove(fn)
        self.updateProgress()
        self.bar.setValue(self.bar.value() + 1)
        if len(self.tasks) == 0:
            self.setVisible(False)
            SvgSource.Search.reload()

class LoadTask(QtCore.QThread):
    taskFinished = QtCore.pyqtSignal()

    def __init__(self, parent, name):
        super().__init__(parent=parent)
        self.name = name

    def run(self):
        download(self.name)
        self.taskFinished.emit()

def download(name):
    fn = "BSicon_" + _quote(name) + ".svg"
    try:
        with request.urlopen("https://en.wikipedia.org/wiki/File:" + fn) as r:
            body = r.read().decode('utf-8')
            m = re.findall(r'<a[^>]+?"(//upload\.wikimedia.+?\.svg)">', body)
            if m:
                with request.urlopen("https:" + m[0]) as r:
                    with open(os.path.join(BLOCK_DIR, fn), "wb+") as f:
                        f.write(r.read())
        QtCore.qDebug("download {} ok".format(name).encode('utf-8'))
        return True
    except Exception as e:
        QtCore.qDebug("download {}: FAIL {}".format(name, e).encode('utf-8'))
        return False

if __name__ == "__main__":
    download("MFADEf")
