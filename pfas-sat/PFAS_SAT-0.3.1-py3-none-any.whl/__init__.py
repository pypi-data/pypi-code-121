# -*- coding: utf-8 -*-
"""
@author: msardar2

PFAS_SAT
"""
try:
    from .GUI.PFAS_SAT_run import MyQtApp
    from PySide2 import QtWidgets
except ImportError:
    print("GUI is not imported")
import sys

# Import Main
from PFAS_SAT.Project import Project
from PFAS_SAT.MCResults import MCResults


__all__ = ['MyQtApp',
           'PFAS_SAT',
           'Project',
           'MCResults']

__version__ = '0.3.1'


class PFAS_SAT():
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.qt_app = MyQtApp()
        availableGeometry = self.app.desktop().availableGeometry(self.qt_app)
        self.qt_app.resize(availableGeometry.width() * 2 / 3, availableGeometry.height() * 2.85 / 3)
        self.qt_app.show()
        self.app.exec_()
