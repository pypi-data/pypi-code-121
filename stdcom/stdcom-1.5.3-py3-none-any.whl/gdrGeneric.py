import sys, re
import argparse

try:
    from PyQt5.QtSvg import QSvgWidget
except ImportError:
    QSvgWidget = None

from PyQt5.QtWidgets import QDialog, QApplication, QTabWidget, QTableWidgetItem, QCheckBox
from PyQt5.QtCore import QSettings, QVariant, Qt, QEvent
from PyQt5.Qt import pyqtSlot, pyqtSignal
from stdcomqt5 import *
from stdcomqt5widget import *

from gdr import  *
from pjaniceGeneric import  pjaniceGeneric as pj


class gdrGeneric(QDialog):
    """
    Stec Pjanice Widget, but with trees not list.
    this will turn into a postgres tool..

    """

    project = "stec-gdr"


    def __init__(self, cBridge: stdcomPyQt = None, project: str = "stec-gdr"):
        """
         def __init__(self, cBridge : stdcomPyQt = None):
        :param cBridge: If you are passing a cBridge and it is controlled here, pass it else it will make one
        """

        self.project = project
        super().__init__()
        self.ui = Ui_GDR()
        self.ui.setupUi(self)
        self.project = project

        self.treeViewGrade = stdcomqt5qtreeMorph(self.ui.treeWidgetGrades, [self.project],self)

        self.widgetPjanice =  pj( cBridge, self.project, self.ui.tabPjanice)
        self.widgetPjanice.setObjectName("widgetPjanice")
        self.ui.verticalLayout_2.addWidget(self.widgetPjanice)
        self.ui.pushButtonGdrDel.clicked.connect(self.removeSelected)
        self.ui.pushButtonGdrAdd.clicked.connect(self.addRow)
        self.ui.pushButtonGdrSave.clicked.connect(self.saveGdrTags)
        self.loadGdrTags()

        self.ui.pushButtonAddGrade.clicked.connect(self.addGrade)
        self.ui.pushButtonDeleteGrade.clicked.connect(self.deleteGrade)
        self.ui.tableWidgetGrades.itemClicked.connect(self.selectGrade)


    @pyqtSlot()
    def removeSelected(self):
        """
        remote selected
        """

        index_list = self.ui.tableWidgetGdrTemplate.selectedIndexes()

        if len(index_list) > 0:
            for index in index_list:
                row = index.row()
                self.ui.tableWidgetGdrTemplate.removeRow(row)

        rows = self.ui.tableWidgetGdrTemplate.rowCount()

    @pyqtSlot()
    def addRow(self):
        rows = self.ui.tableWidgetGdrTemplate.rowCount()
        rows = rows + 1
        self.ui.tableWidgetGdrTemplate.setRowCount(rows)
        rows = self.ui.tableWidgetGdrTemplate.rowCount()
        print(rows)

    @pyqtSlot()
    def saveGdrTags(self):
        setting = stdTableSave(self.project)
        setting.saveTable("gdr.template", self.ui.tableWidgetGdrTemplate)
        setting.loadTable("gdr.template",self.ui.tableWidgetGrades)


    @pyqtSlot()
    def loadGdrTags(self):
        setting = stdTableSave(self.project)
        setting.loadTable("gdr.template",self.ui.tableWidgetGdrTemplate)
        setting.loadTable("gdr.template", self.ui.tableWidgetGrades)

    @pyqtSlot()
    def addGrade(self):
        text = self.ui.editlineGrade.text()
        if text is not None and text !=  "" :
            self.treeViewGrade.AddName(text)

    @pyqtSlot()
    def deleteGrade(self):
       self.treeViewGrade.DeleteSelected()

    @pyqtSlot(QTableWidgetItem)
    def selectGrade(self,itm):
        print("Selectet", itm.text())


if __name__ == "__main__":
    """
    bumped version
    """

    my_parser = argparse.ArgumentParser( description="Version 1.5.2 Stec Pjanice Python Version")
    # Add the arguments
    my_parser.add_argument('-p','--project', metavar='project', required=False)


    args = my_parser.parse_args()
    nextProject = args.project


    app = QApplication(sys.argv)
    if nextProject is not None :
        window = gdrGeneric(None,nextProject)
    else:
        window = gdrGeneric()

    window.setWindowTitle("Stec PJanice Viewer")

    window.show()  # IMPORTANT!!!!! Windows are hidden by default.

    # Start the event loop.
    app.exec_()
    if window.widgetPjanice.cBridge != None:
        window.widgetPjanice.cBridge.terminate()


