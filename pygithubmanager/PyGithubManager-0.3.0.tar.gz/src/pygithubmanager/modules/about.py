from importlib.metadata import version

from PySide6.QtCore import QSize
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QMainWindow
from ui import Ui_GitHubManagerAbout
from utils import LOGO


class About(QMainWindow):
    def __init__(self):
        super(About, self).__init__()

        self.ui = Ui_GitHubManagerAbout()
        self.ui.setupUi(self)

        self.config_ui()

    def config_ui(self):
        self.ui.ghmImageLabel.setPixmap(QPixmap(LOGO).scaled(QSize(120, 120)))
        self.ui.versionLabel.setText(version("pygithubmanager"))
