from PyQt6.QtWidgets import QDialog
from PyQt6 import uic
import webbrowser
import os


class AboutDialog(QDialog):
    def __init__(self, env):
        super().__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), "AboutDialog.ui"), self)

        self.icon_label.setPixmap(env.icon.pixmap(64, 64))
        self.version_label.setText(self.version_label.text().replace("{{version}}", env.version))

        self.button_view_source.clicked.connect(lambda: webbrowser.open("https://gitlab.com/JakobDev/jdDiff"))
        self.button_close.clicked.connect(self.close)
