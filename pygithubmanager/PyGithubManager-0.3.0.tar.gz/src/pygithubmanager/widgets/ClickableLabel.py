from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel


class ClickableLabel(QLabel):
    clicked = Signal()

    def __init__(self, *args):
        """
        ClickableLabel to open a repo

        Parameters
        ----------
        args : list
            Arguments to pass to QLabel
        """
        QLabel.__init__(self, *args)

    def mouseReleaseEvent(self, ev):
        """
        Emit clicked signal when mouse is released
        Parameters
        ----------
        ev : QMouseEvent
            Mouse event
        """
        self.clicked.emit()
