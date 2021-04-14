from PyQt5.QtWidgets import QListView 
import os

class SvgList(QListView):
    def __init__(self, parent, root) -> None:
        super().__init__(parent=parent)
        blocks = os.listdir(root)
        for b in blocks:
            print(b)
