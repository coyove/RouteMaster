import argparse
import collections
from genericpath import exists
import os
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

APP_VERSION = '0.1.0'

ICON_PACKAGE = '../../block.zip'

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
PNG_POLYFILLS = set(filter(lambda x: x.strip(), """
BSicon_LKRWl.svg
BSicon_uLKRW%2Br.svg
BSicon_lhvCONTg(l)q.svg
BSicon_uexkLLSTR%2B4.svg
BSicon_LLSTRr%2B1.svg
BSicon_uexLSTR.svg
BSicon_uexhLSTRr.svg
BSicon_uexkLLSTR3.svg
BSicon_exkLLSTRc3.svg
BSicon_uexhkLLSTRc2.svg
BSicon_uhLSTR.svg
BSicon_exLSTR.svg
BSicon_hkLLSTR3%2Bl.svg
BSicon_uexLSTR2%2Br.svg
BSicon_uexhkLLSTRr%2B1.svg
BSicon_uhLSTR%2Br.svg
BSicon_uLKRWg%2Br.svg
BSicon_uexhkLLSTRc3.svg
BSicon_exkLLSTRc2.svg
BSicon_uexkLLSTR2.svg
BSicon_kLLSTRr%2B1.svg
BSicon_exLLSTR3%2B1a.svg
BSicon_exLKRWg%2Br.svg
BSicon_uexkLLSTRl%2B4.svg
BSicon_hLKRW%2Bl.svg
BSicon_uexLSTRl.svg
BSicon_uexLKRW%2Bl.svg
BSicon_exLSTR%2Bl.svg
BSicon_uexhLSTRq.svg
BSicon_kLLSTR3%2Bl.svg
BSicon_LSTR.svg
BSicon_v-LSHI2%2Bl.svg
BSicon_uexhkLLSTRc1.svg
BSicon_gLLSTR2.svg
BSicon_uLLSTR2%2B4a.svg
BSicon_gLSTR%2Br.svg
BSicon_ukLLSTR%2B4.svg
BSicon_uexhkLLSTR3%2Bl.svg
BSicon_hkLLSTRr%2B1.svg
BSicon_gLLSTR3.svg
BSicon_exkLLSTRc1.svg
BSicon_exkLLSTR%2B1.svg
BSicon_%2Bc.svg
BSicon_exhkLLSTR2%2Br.svg
BSicon_uexLKRWg%2Bl.svg
BSicon_LLSTR3%2Bl.svg
BSicon_uexhLSTR%2Bl.svg
BSicon_uexLLSTR3%2B1e.svg
BSicon_fexLKRW%2Br.svg
BSicon_hLKRWr.svg
BSicon_uexLLSTR3%2B1a.svg
BSicon_ukLLSTR3.svg
BSicon_uLSTR3%2Bl.svg
BSicon_fexLSTR.svg
BSicon_exkLLSTRl%2B4.svg
BSicon_uLSTR3.svg
BSicon_uLSTRr.svg
BSicon_uexhkLLSTRc4.svg
BSicon_fLKRWl.svg
BSicon_exLSTR3%2Bl.svg
BSicon_LKRW%2Br.svg
BSicon_ukLLSTR%2B1.svg
BSicon_uhLKRWr.svg
BSicon_uexLSTR2%2B4.svg
BSicon_exLLSTR1%2B4.svg
BSicon_uLLSTR2%2B4e.svg
BSicon_uexLSTR3%2B1.svg
BSicon_exkLLSTRc4.svg
BSicon_exkLLSTR%2B4.svg
BSicon_uLSTR2.svg
BSicon_fLKRW%2Br.svg
BSicon_ukLLSTR2.svg
BSicon_uhkLLSTR3%2Bl.svg
BSicon_uhkLLSTRr%2B1.svg
BSicon_ukLLSTR2%2Br.svg
BSicon_uLSTRq.svg
BSicon_uexkLLSTR%2B1.svg
BSicon_lhvCONTf(l)q.svg
BSicon_exLLSTR3%2B1e.svg
BSicon_%2Bd.svg
BSicon_exv-LSHI2r.svg
BSicon_exLKRWr.svg
BSicon_uexvLSHI2l-.svg
BSicon_exhLSTRq.svg
BSicon_uexhkLLSTR3.svg
BSicon_uexhkLLSTR2.svg
BSicon_LKRWgr.svg
BSicon_exLSTRr%2B1.svg
BSicon_uexhv-LSHI2r.svg
BSicon_LSTRl%2B4.svg
BSicon_lhvCONTf(r).svg
BSicon_uLSTRr%2B1.svg
BSicon_uLKRWgr.svg
BSicon_kLLSTR2.svg
BSicon_uLLSTR3%2B1.svg
BSicon_uLSTR%2Bl.svg
BSicon_exkLLSTR3.svg
BSicon_fexLKRWr.svg
BSicon_uLLSTR2%2B4.svg
BSicon_v-LSHI2r.svg
BSicon_LSTR2.svg
BSicon_LLSTRl%2B4.svg
BSicon_kLLSTRl%2B4.svg
BSicon_%2Bcd.svg
BSicon_uexhLKRWl.svg
BSicon_uLABZl%2Bl.svg
BSicon_ukLLSTRc1.svg
BSicon_uhkLLSTR%2B1.svg
BSicon_LABZqr.svg
BSicon_uhLKRW%2Bl.svg
BSicon_uexkLLSTRr%2B1.svg
BSicon_LSTR3.svg
BSicon_LSTRr.svg
BSicon_gLLSTR2%2Br.svg
BSicon_uexhkLLSTRl%2B4.svg
BSicon_exLLSTR3%2B4.svg
BSicon_exhLKRW%2Bl.svg
BSicon_LKRWg%2Br.svg
BSicon_uexLLSTR%2B1.svg
BSicon_exkLLSTR2.svg
BSicon_uLSTR.svg
BSicon_lhvCONTf(l).svg
BSicon_uexLSTR%2B1.svg
BSicon_exLLSTR2%2B1.svg
BSicon_kLLSTR3.svg
BSicon_uexLSTR%2Br.svg
BSicon_exLLSTR2%2B3.svg
BSicon_exLLSTR2%2Br.svg
BSicon_uexLKRWgl.svg
BSicon_exLKRW%2Br.svg
BSicon_uexkLLSTR3%2Bl.svg
BSicon_uexLLSTR3%2B1.svg
BSicon_uexLLSTR2%2B4.svg
BSicon_ukLLSTRc3.svg
BSicon_ukLLSTRc2.svg
BSicon_LLSTR3%2B1e.svg
BSicon_LSTRq.svg
BSicon_uexLKRWr.svg
BSicon_kLLSTRc4.svg
BSicon_xLABZqr.svg
BSicon_hkLLSTRl%2B4.svg
BSicon_lhvCONTf(r)q.svg
BSicon_uexhLKRW%2Br.svg
BSicon_uLABZqlr.svg
BSicon_lhLSTR.svg
BSicon_gLLSTR3%2B1.svg
BSicon_gLLSTR2%2B4.svg
BSicon_uLABZq%2Blr.svg
BSicon_LSTR%2Bl.svg
BSicon_uv-LSHI2r.svg
BSicon_exkLLSTRr%2B1.svg
BSicon_LLSTR3%2B1a.svg
BSicon_LSTR3%2Bl.svg
BSicon_uLKRWl.svg
BSicon_exhLKRWl.svg
BSicon_kLLSTRc1.svg
BSicon_uhLSTRl.svg
BSicon_uLLSTR2%2Br.svg
BSicon_hLSTR.svg
BSicon_gLSTRr.svg
BSicon_lhvCONTg(r)q.svg
BSicon_uLLSTR2.svg
BSicon_kLLSTRc3.svg
BSicon_exLKRWgl.svg
BSicon_uhkLLSTRl%2B4.svg
BSicon_LLSTR2.svg
BSicon_LSTRr%2B1.svg
BSicon_exkLLSTR3%2Bl.svg
BSicon_uexLLSTR2%2Br.svg
BSicon_uhkLLSTR%2B4.svg
BSicon_uLSTRl%2B4.svg
BSicon_ukLLSTRc4.svg
BSicon_LLSTR3.svg
BSicon_kLLSTRc2.svg
BSicon_exLLSTR3%2B1.svg
BSicon_exLSTRl.svg
BSicon_uLLSTR3.svg
BSicon_fLSTRq.svg
BSicon_gLSTRq.svg
BSicon_exLSTRl%2B4.svg
BSicon_uexLLSTR%2B4.svg
BSicon_uexLSTR%2B4.svg
BSicon_exLLSTR2%2B4.svg
BSicon_uLLSTRr%2B1.svg
BSicon_w.svg
BSicon_uLSTR%2Br.svg
BSicon_uexLLSTR2%2B4a.svg
BSicon_fexLKRWl.svg
BSicon_v-LSHI2l.svg
BSicon_hkLLSTRc1.svg
BSicon_uexkLLSTRc3.svg
BSicon_uexkLLSTRc2.svg
BSicon_uexhLKRWr.svg
BSicon_uLLSTR3%2B1e.svg
BSicon_LSTR%2B4.svg
BSicon_uhLKRW%2Br.svg
BSicon_exkLLSTR2%2Br.svg
BSicon_uexLLSTR3%2Bl.svg
BSicon_LSTRl.svg
BSicon_exhLKRW%2Br.svg
BSicon_LKRWg%2Bl.svg
BSicon_bs.svg
BSicon_c.svg
BSicon_uexLSTR%2Bl.svg
BSicon_uexLKRWgr.svg
BSicon_exLKRW%2Bl.svg
BSicon_exLLSTR2%2B4e.svg
BSicon_uexLLSTRr%2B1.svg
BSicon_kLLSTR%2B4.svg
BSicon_LSTR2%2Br.svg
BSicon_hkLLSTRc2.svg
BSicon_LLSTR1%2B4.svg
BSicon_ukLLSTRl%2B4.svg
BSicon_uexkLLSTRc1.svg
BSicon_hkLLSTRc3.svg
BSicon_uLLSTR%2B1.svg
BSicon_hkLLSTR%2B1.svg
BSicon_exhLSTR.svg
BSicon_uexLKRWl.svg
BSicon_uexhLKRW%2Bl.svg
BSicon_exLLSTR%2B1.svg
BSicon_uLLSTR3%2Bl.svg
BSicon_uLSTR%2B1.svg
BSicon_fexLSTR%2Br.svg
BSicon_b.svg
BSicon_gLLSTRr%2B1.svg
BSicon_exLLSTR3%2Bl.svg
BSicon_kLLSTR%2B1.svg
BSicon_LSTR%2Br.svg
BSicon_uLABZ%2Blr.svg
BSicon_uexkLLSTR2%2Br.svg
BSicon_lhvCONTg(r).svg
BSicon_uLLSTR%2B4.svg
BSicon_hkLLSTR%2B4.svg
BSicon_uLKRWr.svg
BSicon_uexkLLSTRc4.svg
BSicon_exhLKRWr.svg
BSicon_exLLSTR2%2B4a.svg
BSicon_uhLSTRr.svg
BSicon_fLSTR%2Br.svg
BSicon_exLSTRq.svg
BSicon_exLLSTR%2B4.svg
BSicon_uexLSTRl%2B4.svg
BSicon_gLSTRl.svg
BSicon_uLSTR%2B4.svg
BSicon_vLSHI2%2Br-.svg
BSicon_cd.svg
BSicon_vLSHI2r-.svg
BSicon_exLSTR2.svg
BSicon_exLKRWgr.svg
BSicon_exvLSHI2l-.svg
BSicon_exhkLLSTRl%2B4.svg
BSicon_exhkLLSTR3.svg
BSicon_uexv-LSHI2r.svg
BSicon_uLLSTR3%2B1a.svg
BSicon_hkLLSTRc4.svg
BSicon_LSTR3%2B1.svg
BSicon_LSTR2%2B4.svg
BSicon_LSTR%2B1.svg
BSicon_exhkLLSTR2.svg
BSicon_.svg
BSicon_hLSTRq.svg
BSicon_uhLSTRq.svg
BSicon_exLLSTRr%2B1.svg
BSicon_exLSTR3.svg
BSicon_exLSTRr.svg
BSicon_gLLSTR3%2Bl.svg
BSicon_uexLLSTR2%2B4e.svg
BSicon_d.svg
BSicon_s.svg
BSicon_LKRWr.svg
BSicon_uexLSTRq.svg
BSicon_LLSTR2%2B4.svg
BSicon_uLKRW%2Bl.svg
BSicon_LLSTR3%2B1.svg
BSicon_hkLLSTR3.svg
BSicon_uexhLSTRl.svg
BSicon_exhkLLSTR%2B4.svg
BSicon_uhkLLSTRc1.svg
BSicon_ukLLSTR3%2Bl.svg
BSicon_vLSHI2l-.svg
BSicon_exhkLLSTRc1.svg
BSicon_uLLSTRl%2B4.svg
BSicon_LLSTR2%2B4a.svg
BSicon_gLLSTR%2B4.svg
BSicon_hkLLSTR-c1.svg
BSicon_uhLSTR%2Bl.svg
BSicon_uLKRWg%2Bl.svg
BSicon_exLKRWg%2Bl.svg
BSicon_hkLLSTR2.svg
BSicon_exLSTR%2B1.svg
BSicon_uLABZlr.svg
BSicon_hLKRW%2Br.svg
BSicon_uLSTR2%2Br.svg
BSicon_uexLSTR3.svg
BSicon_uexLSTRr.svg
BSicon_uexLLSTRl%2B4.svg
BSicon_uexLKRW%2Br.svg
BSicon_uexLLSTR3.svg
BSicon_LRP2.svg
BSicon_exLSTR%2Br.svg
BSicon_uhkLLSTRc2.svg
BSicon_lhvCONTg(l).svg
BSicon_exhkLLSTRc2.svg
BSicon_hkLLSTR-c3.svg
BSicon_gLSTR%2Bl.svg
BSicon_exLSTR2%2Br.svg
BSicon_gLSTR.svg
BSicon_udLSTR2.svg
BSicon_hkLLSTR-c2.svg
BSicon_fexLSTRq.svg
BSicon_exhkLLSTRc3.svg
BSicon_ukLLSTRr%2B1.svg
BSicon_uhkLLSTRc3.svg
BSicon_LLSTR%2B1.svg
BSicon_uexLKRWg%2Br.svg
BSicon_uexhLSTR%2Br.svg
BSicon_uhkLLSTR2%2Br.svg
BSicon_uexLLSTR2.svg
BSicon_uexhkLLSTR%2B1.svg
BSicon_fexLKRW%2Bl.svg
BSicon_uexLSTR2.svg
BSicon_vLRP2.svg
BSicon_hLKRWl.svg
BSicon_kLLSTR2%2Br.svg
BSicon_eLABZq%2Bl.svg
BSicon_uLSTRl.svg
BSicon_uexhkLLSTR2%2Br.svg
BSicon_fLKRWr.svg
BSicon_fLSTR.svg
BSicon_gLLSTRl%2B4.svg
BSicon_LKRW%2Bl.svg
BSicon_uvLSHI2l-.svg
BSicon_uhLKRWl.svg
BSicon_uhkLLSTR3.svg
BSicon_uhkLLSTR2.svg
BSicon_uexLSTRr%2B1.svg
BSicon_LLSTR%2B4.svg
BSicon_uexhkLLSTR%2B4.svg
BSicon_exhkLLSTR3%2Bl.svg
BSicon_LLSTR2%2B3.svg
BSicon_LLSTR2%2Br.svg
BSicon_LLSTR2%2B1.svg
BSicon_exhkLLSTRr%2B1.svg
BSicon_LLSTR3%2B4.svg
BSicon_LRP4.svg
BSicon_uhkLLSTRc4.svg
BSicon_exhkLLSTR%2B1.svg
BSicon_exhkLLSTRc4.svg
BSicon_hkLLSTR2%2Br.svg
BSicon_exLLSTR3.svg
BSicon_uexLSTR3%2Bl.svg
BSicon_uexhLSTR.svg
BSicon_exLKRWl.svg
BSicon_gLLSTR%2B1.svg
BSicon_uLABZglr.svg
BSicon_exLSTR2%2B4.svg
BSicon_LLSTR2%2B4e.svg
BSicon_LKRWgl.svg
BSicon_exLLSTRl%2B4.svg
BSicon_hkLLSTR-c4.svg
BSicon_exLSTR3%2B1.svg
BSicon_exLABZr%2Br.svg
BSicon_exLLSTR2.svg
BSicon_cdSEP.svg
BSicon_uLABZg%2Blr.svg
BSicon_uLSTR3%2B1.svg
BSicon_uLABZr%2Br.svg
BSicon_exLSTR%2B4.svg
BSicon_uLKRWgl.svg
BSicon_uLSTR2%2B4.svg
""".split('\n')))

from i18n import en, zh_CN

LANG = QLocale.system().name()

TEST = os.environ.get('RM_TEST') == '1'

def TR(text):
    g = globals()
    x = g[LANG if LANG in g else 'en'].dict
    if text in x:
        return x[text]
    
    if TEST:
        print('"{}": "", # not translated'.format(text))
    return text
