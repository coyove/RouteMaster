from PyQt5.QtGui import QColor, QIcon, QPixmap, QWindow
from Common import APP_NAME
import time
import os
import zipfile
from PyQt5 import QtCore

from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QProgressBar, QVBoxLayout, QWidget

class Loader(QMainWindow):
    def __init__(self, path):
        super().__init__(flags=QtCore.Qt.WindowType.WindowCloseButtonHint|QtCore.Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowTitle(APP_NAME)
        self.show()

        w = QWidget(self)
        box = QVBoxLayout()
        w.setLayout(box)

        self.bar = QProgressBar(w)
        self.bar.show()
        box.addWidget(QLabel("Loading blocks, you can close to skip and resume next time"), 1)
        box.addWidget(self.bar, 1)

        self.setCentralWidget(w) 

        self.closed = False
        self.loading = LoaderTask(self, self.bar, path)
        self.loading.start()
        self.loading.taskFinished.connect(lambda: self.close())

        r = QApplication.desktop().screenGeometry()
        self.move((r.width() - self.width()) // 2, (r.height() - self.height()) // 2)

        self.installEventFilter(self)

    def closeEvent(self, a0):
        self.closed = True
        return super().closeEvent(a0)

    def eventFilter(self, a0, a1: QtCore.QEvent) -> bool:
        if int(a1.type()) == 9731:
            self.bar.setValue(a1.progress)
        return super().eventFilter(a0, a1)

class LoaderProgress(QtCore.QEvent):
    def __init__(self, p):
        super().__init__(QtCore.QEvent.Type(9731))
        self.progress = p

class LoaderTask(QtCore.QThread):
    taskFinished = QtCore.pyqtSignal()

    def __init__(self, parent, bar, path):
        super().__init__(parent=parent)
        self.path = path
        self.bar = bar

    def run(self):
        zf = zipfile.ZipFile(self.path)
        self.bar.setRange(0, sum((file.file_size for file in zf.infolist())))
        extracted_size = 0
        for file in zf.infolist():
            if self.parent().closed:
                break
            extracted_size += file.file_size
            fn = os.path.basename(file.filename)
            if fn.endswith(".svg") or fn.endswith(".png") or fn.endswith(".json"):
                r = zf.open(file) 
                with open(os.path.join('block', fn), 'wb+') as w:
                    while True:
                        buf = r.read(1024)
                        if not buf:
                            break
                        w.write(buf)
            QtCore.QCoreApplication.postEvent(self.parent(), LoaderProgress(extracted_size))
            # self.bar.setValue(extracted_size)
        zf.close()
        if not self.parent().closed:
            f = open("block/finished", 'w+')
            f.write(str(int(time.time())))
            f.close()
        self.taskFinished.emit()

def load_package(path):
    os.makedirs('block', exist_ok=True)
    if os.path.isfile('block/finished'):
        return

    w = Loader(path)
    w.show()