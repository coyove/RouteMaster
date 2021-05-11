from SvgPackage import Loader, download
import json
import shutil
from json.decoder import JSONDecodeError
import os
import sys
import time
import typing

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import (QAction, QApplication, QDialog, QFileDialog,
                             QHBoxLayout, QInputDialog, QLabel, QLayout, QLineEdit,
                             QListWidget, QMainWindow, QMenu, QMessageBox,
                             QPushButton, QSplitter, QStatusBar, QTextEdit,
                             QVBoxLayout, QWidget)

from Common import (AP, APP_NAME, APP_VERSION, BLOCK_DIR, FLAGS, InkscapePath,
                    LANG, LOGS, NEW_LINE, START_TIME, TR, WIN_WIDTH, VDialog, setLang, startNew)
from Map import Map
from MapData import MapData, MapDataElement, SvgSource
from MapExport import exportMapDataPng, exportMapDataSvg
from Property import FileProperty, Logger, Property
from Svg import SvgBar, SvgSearch, _quote

AP.add_argument('file', nargs="?")
AP.add_argument('-c', '--convert', help="output PNG/SVG")
AP.add_argument('--png-scale', help="output PNG scale", type=int, default=1)
AP.add_argument('--show-keys', help="show modifier keys", action="store_true")
AP.add_argument('--hide-ruler', help="hide UI ruler", action="store_true")
AP.add_argument('--background', help="canvas background color", type=str, default='#ffffff')
AP.add_argument('--disable-download', help="no wikimedia downloads", action="store_true")
AP.add_argument("--inkscape", type=str, default="")
AP.add_argument('--lang', help="UI language", type=str, default='')
AP.add_argument('--debug-crash', help="DEBUG ONLY", action="store_true")
AP.add_argument('--debug-fill', help="DEBUG ONLY", type=int, default=0)
args = AP.parse_args()
FLAGS['show_keys'] = args.show_keys
FLAGS['hide_ruler'] = args.hide_ruler
FLAGS['disable_download'] = args.disable_download
FLAGS['inkscape'] = args.inkscape
FLAGS['DEBUG_crash'] = args.debug_crash
FLAGS['DEBUG_fill'] = args.debug_fill
Map.Background = QtGui.QColor(args.background)
args.lang and setLang(args.lang)
logfile = open('logs.txt', 'ab+')

class About(VDialog):
    def __init__(self, parent: typing.Optional[QWidget]) -> None:
        super().__init__(parent=parent)
        box = self.box
        box.addWidget(QLabel('{} (v{})'.format(APP_NAME, APP_VERSION)))
        box.addWidget(QLabel(TR('__about__')))

        def _link(url, text=None): 
            l = QLabel(self)
            l.setText("<a href=\"{}\">{}<a>".format(url, text or url));
            l.setTextFormat(QtCore.Qt.TextFormat.RichText)
            l.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextBrowserInteraction);
            l.setOpenExternalLinks(True);
            return l

        box.addWidget(_link("https://commons.wikimedia.org/wiki/BSicon/Guide"))
        box.addWidget(_link("https://github.com/coyove/RouteMaster", "{} on Github".format(APP_NAME)))
        box.addWidget(_link("https://github.com/wisaly/qtbase_zh"))
        box.addWidget(_link("mailto:coyove@hotmail.com", TR("Send Feedbacks")))
        box.addWidget(_link("https://github.com/coyove/RouteMaster/issues", TR("File Issues on Github")))

        btn = QPushButton(TR('OK'), self)
        btn.clicked.connect(lambda: self.close())
        btn.setFixedSize(btn.sizeHint())
        box.addWidget(btn)# alignment=QtCore.Qt.AlignmentFlag.AlignRight)
        self.setFixedSize(self.sizeHint())

class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.searcher = SvgSearch(BLOCK_DIR)
        SvgSource.Search = self.searcher
        SvgSource.Parent = self

        self.loader = Loader()
        # self.loader.addTask("MFADEf")

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
        self.searchBox.setPlaceholderText(TR('Search blocks'))
        self.searchBox.textChanged.connect(self.updateSearches)
        # self.searchBox.returnPressed.connect(self.searchBlocks)
        self.searchResults = SvgBar(self)
        vbox.addWidget(Property._genVBox(self, self.searchBox, self.searchResults, 8))

        main.setLayout(vbox)
        self.setCentralWidget(main)

        splitter = QSplitter(QtCore.Qt.Orientation.Horizontal)
        splitter.addWidget(self.propertyPanel)

        self.mapview = Map(main)
        self._updateCurrentFile('')
        splitter.addWidget(self.mapview)

        splitter.setStretchFactor(1, 2)
        splitter.setSizes([100, 100])
        vbox.addWidget(splitter, 255)
        
        self.topMenus = {}
        self._addMenu(TR('&File'), TR('&New'), 'Ctrl+N', self.doNew)
        self._addMenu(TR('&File'), TR('&New Window'), 'Ctrl+Shift+N', lambda x: startNew())
        self._addMenu(TR('&File'), '-')
        self._addMenu(TR('&File'), TR('&Open'), 'Ctrl+O', self.doOpen)
        self._addMenu(TR('&File'), '-')
        self._addMenu(TR('&File'), TR('&Save'), 'Ctrl+S', self.doSave)
        self._addMenu(TR('&File'), TR('&Save As...'), 'Ctrl+Shift+S', self.doSaveAs)
        self._addMenu(TR('&File'), '-')
        self._addMenu(TR('&File'), TR('&Export PNG...'), '', lambda x: self.doExportPngSvg(png=True))
        self._addMenu(TR('&File'), TR('E&xport SVG...'), '', lambda x: self.doExportPngSvg(png=False))
        self._addMenu(TR('&File'), '-')
        self._addMenu(TR('&File'), TR('&File Properties...'), 'F3', lambda x: FileProperty(self, self.fileMeta).exec_())
        self._addMenu(TR('&File'), '-')
        self._addMenu(TR('&File'), TR('&Open Data Folder'), '', lambda x: QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(BLOCK_DIR)))
        self._addMenu(TR('&File'), TR('&Download SVG Blocks'), '', self.actDownloadBlocks)
        self._addMenu(TR('&File'), '-')
        self._addMenu(TR('&File'), TR('&Quit'), '', lambda x: self._askSave(thenQuit=True))

        self._addMenu(TR('&Edit'), TR('&Undo'), '', lambda x: self.mapview.actUndoRedo())
        self._addMenu(TR('&Edit'), TR('&Redo'), '', lambda x: self.mapview.actUndoRedo(redo=True))
        self._addMenu(TR('&Edit'), '-')
        self._addMenu(TR('&Edit'), TR('&Cut'), '', lambda x: self.mapview.actCut())
        self._addMenu(TR('&Edit'), TR('&Copy'), '', lambda x: self.mapview.actCopy())
        self._addMenu(TR('&Edit'), TR('&Paste'), '', lambda x: self.mapview.actPaste())
        self._addMenu(TR('&Edit'), '-')
        self._addMenu(TR('&Edit'), TR('&Clear History'), 'Ctrl+K', lambda x: self.mapview.data.clearHistory())
        self._addMenu(TR('&Edit'), '-')
        self._addMenu(TR('&Edit'), TR('&Select by Text'), 'Ctrl+F', lambda x: self.mapview.actSelectByText())
        
        self._addMenu(TR('&View'), TR('&Center'), '', lambda x: self.mapview.center())
        self._addMenu(TR('&View'), TR('Center &Selected'), 'Ctrl+Shift+H', lambda x: self.mapview.center(selected=True))
        self._addMenu(TR('&View'), TR('100% &Zoom'), '', lambda x: self.mapview.center(resetzoom=True))
        self._addMenu(TR('&View'), '-')
        self.showRuler = self._addMenu(TR('&View'), TR('&Ruler'), '', self.actShowRuler)
        self.showRuler.setCheckable(True)
        self.mapview.showRuler = not FLAGS["hide_ruler"]
        self.showRuler.setChecked(self.mapview.showRuler)
        self._addMenu(TR('&View'), '-')
        self._addMenu(TR('&View'), TR('&Logs'), '', lambda x: Logger(self, logfile).exec_())

        self._addMenu(TR('&Help'), TR('&About'), '', lambda x: About(self).exec_()).setMenuRole(QAction.MenuRole.AboutRole)

        self.propertyPanel.update()
        self.showMaximized()

        self.fileMeta = {}
        import socket
        self.resetFileMeta = lambda: self.__setattr__("fileMeta", { "author": socket.gethostname(), "desc": APP_NAME })
        self.resetFileMeta()

        self.load(args.file or '')

        if args.convert:
            self.setVisible(False)
            if args.convert.endswith('.svg'):
                exportMapDataSvg(self, args.convert, self.mapview.data)
            else:
                self.mapview.scale = float(args.png_scale)
                exportMapDataPng(self, args.convert, self.mapview.data)
            print('Successfully export to {}'.format(args.convert))
            sys.exit(0)
        
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

    def actDownloadBlocks(self, v):
        ss, _ = QInputDialog.getText(self, APP_NAME, TR('Block Name:'))
        for s in ss.split():
            s = s.strip()
            s and self.loader.addTask(s)
        
    def ghostHoldSvgSource(self, s):
        self.mapview.ghostHold([MapDataElement(s)])

    def actShowRuler(self, v):
        self.mapview.showRuler = v
        self.mapview.repaint()
        
    def _askSave(self, thenQuit=False):
        if self.mapview.data.historyCap:
            ans = QMessageBox.question(self, TR("Save"), TR("Save current file?"),
                                       buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
            if ans == QMessageBox.StandardButton.Cancel:
                return False
            if ans == QMessageBox.StandardButton.Yes:
                self.doSave(True)
        thenQuit and QApplication.quit()
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
        self.resetFileMeta()
       
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
            QMessageBox(QMessageBox.Icon.Warning, TR('Open'), 'Failed to open {}: {}'.format(fn, e)).exec_()
            
    def doSave(self, v):
        if not self.currentFile:
            self.doSaveAs(True)
        else:
            self.save(self.currentFile)
        
    def doSaveAs(self, v):
        d = QFileDialog(self)
        fn, _ = d.getSaveFileName(filter='BSM Files (*.bsm)')
        if not fn:
            return
        try:
            self.save(fn)
        except Exception as e:
            QMessageBox(QMessageBox.Icon.Warning, TR('Save'), 'Failed to save {}: {}'.format(fn, e)).exec_()

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
            QMessageBox.information(self, TR('Export'), TR('__export_success__').format(fn))
        except Exception as e:
            QMessageBox(QMessageBox.Icon.Warning, TR('Export'), TR('__export_fail__').format(fn)).exec_()
            QtCore.qDebug("{}".format(e).encode("utf-8"))
            
    def load(self, fn: str):
        d: MapData = self.mapview.data
        crashfn = fn.removesuffix(".bsm") + ".crash.bsm"
        delcrash = False
        if os.path.exists(crashfn):
            ans = QMessageBox.question(self, TR('Open'), TR('__open_crash__').format(crashfn))
            if ans == QMessageBox.StandardButton.Yes:
                if fn == "":
                    fn = crashfn
                else:
                    filename = os.path.basename(fn)
                    dir = os.path.dirname(fn)
                    shutil.copy2(fn, os.path.join(dir, "." + filename + ".old"))
                    shutil.copy2(crashfn, fn)
                delcrash = True
            else:
                os.remove(crashfn)
        if not os.path.exists(fn):
            return
        with open(fn, 'rb') as f:
            try:
                fd = json.load(f)
            except JSONDecodeError as e:
                QMessageBox(QMessageBox.Icon.Critical, TR('Open'), TR('__open_fail__').format(fn)).exec_()
                QtCore.qDebug("{}".format(e).encode("utf-8"))
                return
            d.clearHistory()
            d.data = {}
            for c in fd['data']:
                el = MapDataElement.fromdict(c)
                if el:
                    d.data[(el.x, el.y)] = el
            # self.mapview.pan(0, 0)
            self.mapview.center()
            self._updateCurrentFile(fn)
            self.fileMeta["author"] = fd.get("author")
            self.fileMeta["desc"] = fd.get("desc")
            self.mapview.ruler.fromdict(fd.get("rulers"))
        if delcrash:
            os.remove(crashfn)
    
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
                "author": self.fileMeta.get("author"),
                "desc": self.fileMeta.get("desc"),
                "ts": int(time.time()),
                "ver": 1,
                "rulers": self.mapview.ruler.todict(),
                "data": z,
            }, f)
            d.clearHistory()
            self._updateCurrentFile(fn)
            self.propertyPanel.update()
            
    def _updateCurrentFile(self, fn):
        self.currentFile = fn
        self.setWindowTitle(APP_NAME + " - " + (self.currentFile or TR('[Untitled]')))
        
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
        return fileOpen
        

# QApplication.setStyle('fusion')

def messagehandle(t: QtCore.QtMsgType, b, c):
    msg: str = str(int(t)) + "; " + ("%.3f" % (time.time() - START_TIME)) + " " + c
    LOGS.append(msg)
    logfile.write(msg.encode('utf-8'))
    logfile.write(NEW_LINE)
    logfile.flush()
QtCore.qInstallMessageHandler(messagehandle)
QtCore.qDebug(time.strftime("[START] %m-%d-%Y %H:%M:%S"))

app = QApplication([])
app.setWindowIcon(QtGui.QIcon("logo.ico"))

if sys.platform == "win32":
    import ctypes
    myappid = u'coyove.route.master' # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

trdir = QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.LibraryLocation.TranslationsPath)
QtCore.qDebug("translation dir: " + trdir)
tr = QtCore.QTranslator()
if not os.path.exists(os.path.join(trdir, "qtbase_zh_CN")):
    shutil.copy2('qtbase_zh_CN.qm', os.path.join(trdir, "qtbase_zh_CN"))
tr.load("qtbase_" + LANG, trdir)
app.installTranslator(tr)

QtCore.qDebug("inkscape: " + (InkscapePath() or "not found, it is needed when rendering complex blocks"))

win = Window()
def excepthook(exc_type, exc_value, exc_tb):
    import traceback
    msg = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    QtCore.qDebug(("exception:\n" + msg).encode('utf-8'))
    print(msg)
    global win
    if win:
        w = win
        win = None # prevent dead loop
        try:
            w.save(w.currentFile.removesuffix(".bsm") + '.crash.bsm' if w.currentFile else '.crash.bsm')
        except Exception as e:
            QtCore.qDebug(("double exception in hook: {}".format(e)).encode('utf-8'))
    app.quit()
sys.excepthook = excepthook

if not os.path.exists(BLOCK_DIR) or len(SvgSource.Search.files) == 0:
    QMessageBox(QMessageBox.Icon.Warning, APP_NAME, TR("__block_dir__").format(BLOCK_DIR)).exec_()

app.exec_()
