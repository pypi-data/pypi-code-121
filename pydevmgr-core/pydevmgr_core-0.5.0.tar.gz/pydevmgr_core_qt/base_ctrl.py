from .base import BaseUiLinker, record_widget_factory

from PyQt5 import uic
from PyQt5.QtWidgets import QFrame, QWidget, QHBoxLayout, QLabel


class BaseCtrl(BaseUiLinker):

    class Widget(QWidget):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            ly =  QHBoxLayout()
            txt = QLabel("Base ctrl device. No Widget defined")
            ly.addWidget(txt)
            self.setLayout(ly)


record_widget_factory("ctrl", "Base", BaseCtrl)

