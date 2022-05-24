from PyQt5 import QtWidgets, QtCore, QtGui

from boxjelly.delegates.TrackHeadersDelegate import TrackHeadersDelegate


class TrackHeadersView(QtWidgets.QListView):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setItemDelegate(TrackHeadersDelegate(self))
        
        self.setFrameStyle(QtWidgets.QFrame.NoFrame)
        
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
    
    def set_vertical_scroll(self, value: int):
        self.verticalScrollBar().setValue(value)
    
    def wheelEvent(self, e: QtGui.QWheelEvent):
        pass