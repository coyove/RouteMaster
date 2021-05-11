import argparse
import collections
import functools
from genericpath import exists
import os
import sys
import time

from PyQt5.QtCore import QLocale
from PyQt5.QtWidgets import QDialog, QVBoxLayout

class VDialog(QDialog):
    def __init__(self, parent) -> None:
        super().__init__(parent=parent)
        self.setWindowTitle(APP_NAME)
        self.setFixedWidth(WIN_WIDTH)
        self.box = QVBoxLayout(self)

APP_NAME = 'RouteMaster'

APP_VERSION = '0.1.0a'

BLOCK_DIR = os.path.join(os.path.expanduser("~"), APP_NAME + "_blocks")
os.makedirs(BLOCK_DIR, exist_ok=True)

WIN_WIDTH = 400

BS = 32

LOGS = collections.deque(maxlen=1000)

START_TIME = time.time()

NEW_LINE = bytes([0xA])

AP = argparse.ArgumentParser()

FLAGS = {}

# these svg files cannot be rendered properly by Qt
def ispngployfill(fn: str):
    return os.path.exists(os.path.join(BLOCK_DIR, fn.removesuffix(".svg") + ".png"))

from i18n import en, zh_CN # Installer compatible

LANG = QLocale.system().name()

TEST = os.environ.get('RM_TEST') == '1'

def setLang(l):
    global LANG
    LANG = l

def TR(text):
    g = globals()
    x = g[LANG if LANG in g else 'en'].dict
    if text in x:
        return x[text]
    
    if TEST:
        print('"{}": "", # not translated'.format(text))
    return text

@functools.cache
def InkscapePath():
    if FLAGS.get('inkscape'):
        return FLAGS['inkscape']
    if sys.platform == "win32":
        return 'C:/Progra~1/Inkscape/bin/inkscape.exe'
    out = os.popen('which inkscape').read().strip()
    if 'not found' in out.lower():
        return ""
    return out

def startNew():
    import subprocess
    args = sys.argv[:]
    args.insert(0, sys.executable)
    if sys.platform == 'win32':
        args = ['"%s"' % arg for arg in args]
    os.chdir(os.getcwd())
    subprocess.Popen(args)

def maybeName(s):
    import re
    if re.search(r"^[a-zA-Z1-4\~\-\@\+\.\(\)]+$", s):
        if re.search(r"[a-zA-Z]+", s):
            return True
    return False