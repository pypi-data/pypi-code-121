import sys, re
import argparse

try:
    from PyQt5.QtSvg import QSvgWidget
except ImportError:
    QSvgWidget = None

from pjanice import *
from PyQt5.QtWidgets import QDialog, QApplication, QTabWidget, QTableWidgetItem, QCheckBox
from PyQt5.QtCore import QSettings, QVariant, Qt, QEvent
from PyQt5.Qt import pyqtSlot, pyqtSignal
from stdcomqt5 import *
from stdcomqt5widget import *


class pjaniceGeneric(QWidget):
    """
    Stec Pjanice Widget, but with trees not list.
    """

    MultiverseHostname = None
    MultiversePort = None

    cBridge = None
    currentSub = ""
    data = []
    suspectTable = False
    project = "stec-pjanice"

    liveSubscriptions = {"": []}
    liveSubscriptionsData = {"": []}

    def __init__(self, cBridge: stdcomPyQt = None, project: str = "stec-pjanice", parent = None):
        """
         def __init__(self, cBridge : stdcomPyQt = None):
        :param cBridge: If you are passing a cBridge and it is controlled here, pass it else it will make one
        """

        self.liveSubscriptionsData.clear()
        self.liveSubscriptions.clear()

        self.project = project
        super().__init__(parent)
        self.ui = Ui_pjanice()
        self.ui.setupUi(self)

        self.show()
        self.treeViewTags = stdcomqt5qtreeMorph(self.ui.treeWidgetUI, [self.project], self)

        self.treeViewTags.newTextSignal.connect(self.slotSelected)
        self.MultiverseHostname = self.ui.lineEditIpAddress.text()
        self.MultiversePort = int(self.ui.lineEditServicePort.text())

        if cBridge is not None:
            self.cBridge = cBridge
        else:
            self.cBridge = stdcomPyQt()

        self.cBridge.sigNames.connect(self.slotNames)
        self.cBridge.sigNewData.connect(self.slotNewData)
        self.cBridge.sigNewDesc.connect(self.slotDesc)

        self.LoadConfig()
        self.ui.pushButtonConfigure.clicked.connect(self.SaveConfig)

        self.ui.tableWidgetData.itemChanged.connect(self.on_any_itemChanged)
        self.ui.tableWidgetLiveTags.setHorizontalHeaderLabels(["Name", "Length", "Description", "Resident"])
        self.ui.pushButtonDeleteLiveTag.clicked.connect(self.removeSelected)
        self.ui.pushButtonAddLiveTag.clicked.connect(self.addRow)
        self.ui.pushButtonSaveLiveTag.clicked.connect(self.saveLiveTags)
        self.loadLiveTags()
        self.cleanUpLiveSubscriptions()

    def getStoredData(self, name, nbr: int):
        settings = VSettings(self.project)
        nameData = name + ".Data"
        data = [0.0] * nbr
        data = settings.value(nameData, data)
        for i in range(len(data), nbr):
            data.append(0.0)
        return data

    def saveStoredData(self, name, data):
        settings = VSettings(self.project)
        nameData = name + ".Data"
        settings.setValue( nameData , data)
        settings.sync()

    def cleanUpLiveSubscriptions(self):
        for name in self.liveSubscriptionsData.keys():
            if name not in self.liveSubscriptions:
                if self.currentSub != name:
                    self.cBridge.unsubscribe(name)
                self.liveSubscriptionsData.pop(name, None)

        for name in self.liveSubscriptions.keys():
            if name not in self.liveSubscriptionsData:
                self.cBridge.subscribe(name)
                vals = self.liveSubscriptions.get(name)
                self.cBridge.writeDescription(name, vals[2])
                data = self.getStoredData(name, int(vals[1]))
                self.saveStoredData(name, data)
                self.liveSubscriptionsData.update({name: data})
                self.cBridge.writeValues(name, data)

    def getcBridge(self):
        """
        return the current cBridge, the stdcomPyQt which is the qt version of the stdcom
        """
        return self.cBridge

    def closeEvent(self, event: QEvent = None):
        """
        internal use
        :param event:
        :return:
        """
        if self.cBridge is not None:
            self.cBridge.terminate()
            self.cBridge = None
        event.accept()

    @pyqtSlot(list)
    def slotNames(self, names):
        """
        internal use
        """
        self.treeViewTags.AddNames(names)

    @pyqtSlot(str, str)
    def slotDesc(self, name, desc):
        """
        internal use
        """
        self.treeViewTags.AddDesc(name, desc)
        if name == self.currentSub:
            self.ui.plainTextEditDesc.clear()
            self.ui.plainTextEditDesc.insertPlainText(desc)

    @pyqtSlot(str, str)
    def slotSelected(self, name, desc):
        self.ui.tableWidgetData.clear()
        if self.currentSub != "" and name not in self.liveSubscriptionsData:
            self.cBridge.unsubscribe(self.currentSub)

        self.currentSub = name
        self.cBridge.subscribe(name)

        self.ui.lineEditTag.setText(name)
        self.ui.plainTextEditDesc.clear()
        if desc != "":
            self.ui.plainTextEditDesc.insertPlainText(desc)

        self.cBridge.getPossibleSubscribers()
        values = self.cBridge.readValues(name)
        if values is not None and len(values):
            self.slotNewData(name, values)

    @pyqtSlot(str, list)
    def slotNewData(self, name, data):
        """
        data as it comes in from Multiverse
        :param name:
        :param data:
        :return:
        """
        if name == self.currentSub:
            self.ui.tableWidgetData.clear()
            self.ui.tableWidgetData.setRowCount(len(data))
            self.ui.tableWidgetData.setColumnCount(1)

            self.suspectTable = True
            self.data = data
            for i in range(0, len(data)):
                d = QTableWidgetItem(str(data[i]))
                self.ui.tableWidgetData.setItem(i, 0, d)

            self.suspectTable = False

        if name in self.liveSubscriptionsData:
            self.liveSubscriptionsData.update({name: data})
            self.saveStoredData(name, data)

    @pyqtSlot()
    def SaveConfig(self):

        """
        Saves all setup data
        :return:
        """

        settings = VSettings(self.project)
        self.MultiverseHostname = self.ui.lineEditIpAddress.text()
        self.MultiversePort = int(self.ui.lineEditServicePort.text())

        settings.setValue('MultiverseHostname', self.MultiverseHostname)
        settings.setValue('MultiversePort', self.MultiversePort)

        settings.sync()

        if self.cBridge is not None:
            self.cBridge.terminate()

        self.cBridge.setDestination(self.MultiverseHostname, self.MultiversePort)
        self.treeViewTags.clear()
        self.cBridge.LoadcBridge()

    @pyqtSlot()
    def LoadConfig(self):
        """
        loads all configurations
        :return:
        """
        settings = VSettings(self.project)
        self.MultiverseHostname = str(settings.value("MultiverseHostname", self.MultiverseHostname))
        self.MultiversePort = int(settings.value("MultiversePort", self.MultiversePort))
        self.ui.lineEditIpAddress.setText(self.MultiverseHostname)
        self.ui.lineEditServicePort.setText(str(self.MultiversePort))

        if self.cBridge is not None:
            self.cBridge.terminate()

        self.cBridge.setDestination(self.MultiverseHostname, self.MultiversePort)
        self.cBridge.LoadcBridge()

    @pyqtSlot(QTableWidgetItem)
    def on_any_itemChanged(self, itm: QTableWidgetItem):
        c = itm.column()
        r = itm.row()

        if self.suspectTable is False:
            print("Changed R/C ", r, "/", c, itm.text())
            if r < len(self.data):
                self.data[r] = itm.text()
                self.cBridge.writeValues(self.currentSub, self.data)

    @pyqtSlot()
    def saveLiveTags(self):
        self.liveSubscriptions.clear()
        rows = self.ui.tableWidgetLiveTags.rowCount()
        liveTags = []
        for i in range(0, rows):
            itm = self.ui.tableWidgetLiveTags.item(i, 0)
            if itm is not None:
                name = itm.text()
                itm = self.ui.tableWidgetLiveTags.item(i, 1)
                if itm is not None:
                    nbr = itm.text()
                    itm = self.ui.tableWidgetLiveTags.item(i, 2)
                    if itm is not None:
                        desc = itm.text()
                        self.liveSubscriptions.update({name: [name, nbr, desc]})
                        liveTags.append([name, nbr, desc])

        settings = VSettings(self.project)
        settings.setValue("LiveTags", liveTags)
        self.cleanUpLiveSubscriptions()

    def loadLiveTags(self):
        settings = VSettings(self.project)

        settings = VSettings(self.project)
        liveTags = settings.value("LiveTags", [])

        if liveTags is None:
            liveTags = []

        rows = len(liveTags) + 1
        self.ui.tableWidgetLiveTags.setRowCount(rows)

        for xl in range(0, len(liveTags)):
            xlist = liveTags[xl]
            for i in range(0, len(xlist)):
                val = xlist[i]
                itm = QTableWidgetItem()
                itm.setText(val)
                self.ui.tableWidgetLiveTags.setItem(xl, i, itm)

        self.saveLiveTags()

    @pyqtSlot()
    def removeSelected(self):

        index_list = self.ui.tableWidgetLiveTags.selectedItems()

        if len(index_list) > 0:
            for index in index_list:
                self.ui.tableWidgetLiveTags.removeRow(index.row())
        else:
            rows = self.ui.tableWidgetLiveTags.rowCount()
            if rows:
                self.ui.tableWidgetLiveTags.removeRow(rows - 1)

        rows = self.ui.tableWidgetLiveTags.rowCount()
        if rows < 1:
            self.ui.tableWidgetLiveTags.setRowCount(1)

    @pyqtSlot()
    def addRow(self):
        rows = self.ui.tableWidgetLiveTags.rowCount()
        self.ui.tableWidgetLiveTags.setRowCount(rows + 1)


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
        window = pjaniceGeneric(None,nextProject)
    else:
        window = pjaniceGeneric()

    window.setWindowTitle("Stec PJanice Viewer")

    window.show()  # IMPORTANT!!!!! Windows are hidden by default.

    # Start the event loop.
    app.exec_()
    if window.cBridge != None:
        window.cBridge.terminate()
