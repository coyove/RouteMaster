from PyQt5.QtGui import QColor, QIcon, QPixmap
from Common import APP_NAME
import time
import os
import zipfile
from PyQt5 import QtCore

from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QProgressBar, QVBoxLayout, QWidget

class Loader(QMainWindow):
    def __init__(self, path):
        super().__init__(flags=QtCore.Qt.WindowType.WindowCloseButtonHint)
        self.setWindowTitle(APP_NAME)
        self.show()

        w = QWidget(self)
        box = QVBoxLayout()
        w.setLayout(box)

        bar = QProgressBar(w)
        bar.show()
        box.addWidget(QLabel("Loading blocks ... close to skip"), 1)
        box.addWidget(bar, 1)

        self.setCentralWidget(w) 

        self.loading = LoaderTask(bar, path)
        self.loading.start()
        self.loading.taskFinished.connect(lambda: self.close())

        r = QApplication.desktop().screenGeometry()
        self.move((r.width() - self.width()) // 2, (r.height() - self.height()) // 2)

    def closeEvent(self, a0):
        self.loading.terminate()
        return super().closeEvent(a0)

class LoaderTask(QtCore.QThread):
    taskFinished = QtCore.pyqtSignal()

    def __init__(self, bar, path):
        super().__init__()
        self.path = path
        self.bar = bar

    def run(self):
        zf = zipfile.ZipFile(self.path)
        self.bar.setRange(0, sum((file.file_size for file in zf.infolist())))
        extracted_size = 0
        for file in zf.infolist():
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
            self.bar.setValue(extracted_size)
        zf.close()
        f = open("block/finished", 'w+')
        f.write(str(int(time.time())))
        f.close()
        self.taskFinished.emit()

def load_package(path):
    os.makedirs('block', exist_ok=True)
    if os.path.isfile('block/finished'):
        return

    app = QApplication([])
    win = Loader(path)
    app.exec_() 