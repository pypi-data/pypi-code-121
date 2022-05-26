from PyQt5.QtCore import QTimer, QObject, pyqtSignal, pyqtSlot, QSettings, QDataStream, QByteArray, QVariant, QIODevice, Qt
from PyQt5.QtWidgets import  QTabWidget, QTableWidgetItem

from stdcom import *

"""
    This is where Stec QObject are kept, this are not QWidgets
"""
class VSettings(QSettings):
    """
    Used to save setup data
    """
    def __init__(self, project : str = "stec-opcua"):
        """
        :param project:   default is "stec-opc" Should be the Project you or instance of the Project
        """
        super().__init__( project, QSettings.IniFormat)


class stdTableSave( ) :
    project = None
    def __init__(self, project: str = "stec-opcua"):
        self.project = project

    def saveTable(self, tableName: str = None, table: QTabWidget = None):

        ba = QByteArray();

        r = table.rowCount()
        c = table.columnCount()

        stream = QDataStream(ba,QIODevice.WriteOnly)
        stream.writeInt(c)
        stream.writeInt(r)

        for row in range(r):
            for col in range(c):
                itm = table.item(row, col)
                if itm is not None:
                    text = itm.text()

                    try:
                        data = itm.data()

                    except :
                        data = []
                        data.append(QVariant(""))

                    cc = int(col)
                    rr = int(row)
                    stream.writeInt(cc)
                    stream.writeInt(rr)
                    stream.writeQString(text)
                    stream.writeQVariant(data)

        settings = VSettings(self.project)
        settings.setValue(tableName, ba)

    def loadTable(self, tableName: str = None, table: QTabWidget = None):

        ba = QByteArray();
        settings = VSettings(self.project)
        ba = settings.value(tableName, ba)

        if ba is None :
            return

        stream = QDataStream(ba,QIODevice.ReadOnly)
        c = int(0)
        r = int(0)

        if stream.atEnd() :
            return
        c = stream.readInt()

        if stream.atEnd() :
            return
        r = stream.readInt()

        table.setRowCount(int(r))
        table.setColumnCount(int(c))

        while not stream.atEnd():

            cc = stream.readInt()
            rr = stream.readInt()
            itm = table.item(rr, cc)

            if itm is None:
                itm = QTableWidgetItem()

            text = stream.readQString()
            itm.setText(text)

            try:
                data = QVariant(stream.readQVariant())
                type = data.type()

                if data.isValid() or type == QVariant.List:
                    itm.setData(Qt.UserRole, data)
                    table.setItem(rr, cc, itm)
                else:
                    print("Unknown Type")

            except:
                print("Goofy Col ", cc, " : Row ", rr)




class stdcomPyQt(QObject):
    """
    The stdcomPyQt class is a PyQt5 version that sits on top of stdcom, can has signals, slots, and auto restart capabilities build into it.
        :uiparent: QObject = None default, or the parent QObject
    """


    sigNewData = pyqtSignal(str, list)
    sigNewDesc = pyqtSignal(str, str)

    sigNames = pyqtSignal(list)
    sigConnect = pyqtSignal()
    sigNoConnect = pyqtSignal()
    sigBalanceTable = pyqtSignal()

    cBridge = None
    Parent = None
    liveSubnames = []


    watchDogSeconds = 5

    # this is a duplicate, but it allows us to stay running if the Links to Multiverse is down..
    liveData = {}
    liveDesc = {}
    liveOurDesc = {}

    timer = None
    MultiverseHostname = "192.168.199.245"
    MultiversePort = 4897

    def __init__(self, uiparent: QObject = None):
        """
        :param uiparent: QObject of the parent or None
        """
        if uiparent is not None:
            super().__init__(uiparent)
        else:
            super().__init__()

        self.Parent = uiparent
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.RestartAttmepts)
        self.timer.setInterval(self.watchDogSeconds * 1000)

    def setWatchDogIntervalSec(self, seconds: int = 5):
        """
        Sets the watchdog timer in seconds. This can be adjusted if the Multiverse in on the internet and thousands of miles away.
            :seconds: Default is 5 seconds, make this longer if huge internet delay
        """

        self.watchDogSeconds = seconds
        self.timer.setInterval(self.watchDogSeconds * 1000)

    def readValues(self, Name: str):
        """
        Reads values cached for a single subscription name that is given and has been subscribed to.
            :Name: Name of the subscription
            :return: list of data for a given subscrition, or None if not available
        """
        if Name in self.liveData.keys():
            return self.liveData.get(Name)
        return None

    def writeValues(self, Name: str, Data: list):
        """
        WritesValues to multiverse if subcription is made, or local data is ~/ is the prefix
            :Name: The name of the subscription, if ~/ is the prefix, then data is local.
            :Data: Is a list[] of data

        """
        if Name in self.liveData.keys():
            self.liveData.update({Name: Data})
            if self.cBridge is not None and Data is not None:
                Data = list(Data)
                if len(Data):
                    self.cBridge.UpdateRaw(Name, Data, 0)

            # allow the system to operate without Multiverse
            else:
                self.sigNewData.emit(Name, Data)

    def writeDescription(self,name, desc : str):
        if desc is not None :
            if self.cBridge is not None :
                self.cBridge.UpdateDescription(name,desc)
            self.liveDesc.update({name: desc})
            self.liveOurDesc.update({name: desc})
            self.sigNewDesc.emit(name, desc)


    def subscribe(self, Name: str):
        """
        Subscribe to a give Name
            :Name: The subscription name

        """
        if Name not in self.liveData.keys():
            self.liveData.update({Name: []})
            if self.cBridge is not None:
                self.cBridge.AddSubscriptions([Name])

    def getPossibleSubscribers(self):
        """
        All the possible subscription names possible
           :return: list of names of all possible subscritions
        """

        return self.liveSubnames

    def getSubscribers(self):
        """
        All the stuff subscribed to
            :return: A list of all the subscription names we have subscribed to
        """
        return list(self.liveData.keys())

    def unsubscribe(self, Name):
        """
        UnSubscribe to something previously subscribed to.
            :Name: The name of the Subscription to delete
        """
        if Name in self.liveData.keys():
            del self.liveData[Name]
            if self.cBridge is not None:
                self.cBridge.RemoveSub(Name)

    def AddValues(self, sub):


        """
        Internal use, updates makes and notfies by signal data has changed for a subcription
            :sigNewData.emit: Name, Data
        """
        self.liveData.update({sub.Name(): sub.Data()})
        self.sigNewData.emit(sub.Name(), sub.Data())

    def AddDesc(self, sub):
        """
        Internal use, updates makes and notfies by signal data has changed for a subcription
            :sigNewData.emit: Name, Data
        """


        d = sub.Data()

        if len(d) >= 1  :
            desc = str (d[0])
            self.liveDesc.update({sub.Name() : desc})
            self.sigNewDesc.emit(sub.Name(), desc)


    def AddNames(self, values):
        """
        Internal use tell when a new name is found, with emit
            : sigNames.emit: list[str] of new names entering the picture that can be subscribed to
        """

        self.sigNames.emit(values)

    def ConnectSocket(self, v):
        """
        Socket connection call back, for internal use
            :sigConnect.emit: emits the signal if connection happens
        """
        self.sigConnect.emit()
        print(v)

    def ConnectionError(self):
        """
         Socket error connection call back, for internal use
            :sigNoConnect.emit: emits the signal if connection error or close happens
        """
        self.sigNoConnect.emit()
        print("Connection Error")

    def setDestination(self, dest, port):
        """
        Sets a new Destination and port, the user must terminate amd loadbridge again after changing is connected.
        """
        self.MultiverseHostname = dest
        self.MultiversePort = port

    def LoadcBridge(self):
        """
        User calls this to start the ball rolling to the connection to multiverse providing the destination and port are set correctly.
        """

        if self.cBridge is not None:
            self.liveSubnames = []
            self.cBridge.terminate()
            self.sigNames.disconnect(self.NewLiveTags)

        try:

            self.cBridge = stdcom(self.MultiverseHostname, self.MultiversePort, self.ConnectSocket, None, None,
                                  self.ConnectionError)

            self.cBridge.SetCallbacks(self.AddValues, self.AddNames, self.AddDesc)
            self.cBridge.NamesOn()  # tell the communication class to tu
            self.sigNames.connect(self.NewLiveTags)
            self.sigConnect.emit()

            subs = list(self.liveData.keys())

            if subs is not None and len(subs) > 0:
                self.cBridge.AddSubscriptions(subs)
                for each in subs :
                    if each in self.liveOurDesc :
                        desc = self.liveOurDesc.get(each)
                        self.cBridge.UpdateDescription(each, desc)


            else:
                print("No Subscriptions to Add")



            self.timer.start()

        except  ConnectionError as e:
            print("Need To Set Correct IP and Port")
            self.cBridge = None
            self.sigNoConnect.emit()

    # ----- from threads
    def terminate(self):
        """
        Cridical the user called this function when leaving .. I closes down the thread connected to multiverse
        """
        if self.cBridge is not None:
            self.timer.stop()
            self.cBridge.terminate()
            self.cBridge = None
            self.sigNoConnect.emit()

    @pyqtSlot(str, list)
    def slotUpdateData(self, Name, Data):
        self.writeValues(Name, Data)

    @pyqtSlot(list)
    def NewLiveTags(self, names):
        self.liveSubnames = self.liveSubnames + names

    @pyqtSlot()
    def RestartAttmepts(self): # todo needs better logic, this works but logic is weak and needs something besides order and 1 default
        if self.cBridge is None or self.cBridge.isConnected() is False:
            self.LoadcBridge()
        elif self.cBridge != None:
            acks = self.cBridge.GetAcks()
            print("ACKS: ", acks)
            if acks == 0:
                self.LoadcBridge()
            else:
                self.cBridge.Ping()


if __name__ == "__main__":


    class stdcomClientPyQt(QObject):

        cBridge = None

        def __init__(self, cBridge : stdcomPyQt = None,  uiparent: QObject = None):

            self.cBridge = cBridge
            """
               :param uiparent: QObject of the parent or None
            """
            if uiparent is not None:
                super().__init__(uiparent)
            else:
                super().__init__()

            self.cBridge.sigNames.connect(self.slotNames)
            self.cBridge.sigNewData.connect(self.slotNewData)
            self.cBridge.sigNewDesc.connect(self.slotNewDesc)

            print("Connected")

        @pyqtSlot(str, list )
        def slotNewData(self, name, data):
            print("New Data",name, ":", data )

        @pyqtSlot(str, str)
        def slotNewDesc(self, name, desc):
            print("New Desc", name, ":", desc)

        @pyqtSlot( list)
        def slotNames(self, names : list):
            print("New Name", names)
            for name in names :
                self.cBridge.subscribe(name)



    from PyQt5.QtCore import QCoreApplication
    import sys

    if "--version" in sys.argv:
        print("1.5.00")
        sys.exit()

    app = QCoreApplication(sys.argv)
    w = stdcomPyQt()
    client = stdcomClientPyQt(w)
    w.LoadcBridge()


    app.exec_()
    w.terminate()
    sys.exit(0)
