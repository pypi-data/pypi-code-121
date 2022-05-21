from sudoku.gui.Ui_AboutWindow import Ui_AboutWindow

from PyQt5 import QtWidgets

class AboutWindow(QtWidgets.QDialog, Ui_AboutWindow):
    def __init__(self, parent: QtWidgets.QWidget = None) -> None:
        super(AboutWindow, self).__init__(parent)

        self.setupUi(self)
