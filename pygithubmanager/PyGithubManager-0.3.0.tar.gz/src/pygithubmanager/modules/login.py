import re

from PySide6.QtCore import QSize
from PySide6.QtGui import QPixmap, QIcon, QScreen
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QMainWindow, QLineEdit, QApplication
from github import Github, BadCredentialsException
from requests import ConnectTimeout

from modules import About
from modules.user import User
from ui import Ui_GitHubManagerLogin
from utils import LOGO, get_icon
from widgets import CustomWebEnginePage


class Login(QMainWindow):
    def __init__(self, main_window):
        """
        Constructor of the login window class

        Configure the interface of the login window.

        Parameters
        ----------
        main_window:
            Main window of the application
        """
        super(Login, self).__init__()

        self.ui = Ui_GitHubManagerLogin()
        self.ui.setupUi(self)

        self.browser = QMainWindow()

        self.about = About()

        self.main_window = main_window

        self.visible_token = True

        self.config()
        self.config_ui()

    def config_ui(self):
        """
        Configure the interface of the login window
        """
        self.setWindowIcon(QIcon(LOGO))
        self.browser.setWindowIcon(QIcon(LOGO))
        self.browser.setWindowTitle("Get personal access token")
        self.ui.ghmImageLabel.setPixmap(QPixmap(LOGO).scaled(QSize(120, 120)))
        self.ui.switchVisibilityButton.setIcon(QIcon(get_icon("dark_ocultar.png")))  # Al modo oscuro
        self.ui.errorWidget.set_icon("fa5s.exclamation-triangle")
        self.ui.errorWidget.set_text_style(color="red", font_size=13, bold=True)

        center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        geo = self.frameGeometry()
        geo.moveCenter(center)
        self.move(geo.topLeft())

    def config(self):
        """
        Configure the login window widgets and signals
        """
        self.ui.switchVisibilityButton.clicked.connect(self.switch_visibility)
        self.ui.githubAccesTokenButton.clicked.connect(self.get_access_token)
        self.ui.signInButton.clicked.connect(self.login)
        self.ui.signInButton.setShortcut("Return")
        self.ui.signInButton.setShortcut("Enter")

        self.ui.tokenLineEdit.textChanged.connect(self.check_text)
        self.ui.signInButton.setDisabled(True)

        self.ui.actionExit.triggered.connect(self.close)
        self.ui.actionAbout.triggered.connect(lambda x: self.about.show())
        self.ui.errorWidget.hide()

    def switch_visibility(self):
        """
        Switch the visibility of the password field and the button to show/hide the password
        """
        if self.visible_token:
            self.ui.tokenLineEdit.setEchoMode(QLineEdit.Password)
            self.ui.switchVisibilityButton.setIcon(QIcon(get_icon("dark_visible.png")))
        else:
            self.ui.tokenLineEdit.setEchoMode(QLineEdit.Normal)
            self.ui.switchVisibilityButton.setIcon(QIcon(get_icon("dark_ocultar.png")))
        self.visible_token = not self.visible_token

    def check_text(self, text):
        """
        Check if the text is correct and enable the button

        Parameters
        ----------
        text: str
            Text to check
        """
        if re.search(r"^[a-zA-Z]+_.*$", text):
            self.ui.signInButton.setEnabled(True)
        else:
            self.ui.signInButton.setDisabled(True)

        self.ui.errorWidget.hide()

    def login(self):
        """
        Check the token and create the Github object and the user object
        """
        try:
            github = Github(self.ui.tokenLineEdit.text())
            user = github.get_user()
            self.main_window.start(User(github, user, self.ui.tokenLineEdit.text()))
            self.hide()
        except BadCredentialsException:
            self.ui.errorWidget.setText("Invalid token")
            self.ui.errorWidget.show()
        except ConnectTimeout:
            self.ui.errorWidget.setText("Connection timeout")
            self.ui.errorWidget.show()
        except Exception as e:
            self.ui.errorWidget.setText("Unknown error")
            self.ui.errorWidget.show()
            print(e)

    def get_access_token(self):
        """
        This method is used to generate a personal access token for the user.
        """
        browser = QWebEngineView()
        browser.setPage(CustomWebEnginePage(self))
        browser.setUrl("https://github.com/settings/tokens/new")
        self.browser.setCentralWidget(browser)
        self.browser.show()

    def closeEvent(self, event):
        """
        Close event

        Parameters
        ----------
        event: QCloseEvent
            Close event
        """
        quit()
