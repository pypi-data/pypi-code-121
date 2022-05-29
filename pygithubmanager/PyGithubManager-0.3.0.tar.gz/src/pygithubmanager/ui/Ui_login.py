# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'loginwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.3.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QLineEdit, QMainWindow, QMenu, QMenuBar,
    QPushButton, QSizePolicy, QSpacerItem, QStatusBar,
    QVBoxLayout, QWidget)

from widgets.IconLabel import IconLabel

class Ui_GitHubManagerLogin(object):
    def setupUi(self, GitHubManagerLogin):
        if not GitHubManagerLogin.objectName():
            GitHubManagerLogin.setObjectName(u"GitHubManagerLogin")
        GitHubManagerLogin.resize(369, 247)
        self.actionAbout = QAction(GitHubManagerLogin)
        self.actionAbout.setObjectName(u"actionAbout")
        self.actionHow_to_get_an_GitHub_acces_token = QAction(GitHubManagerLogin)
        self.actionHow_to_get_an_GitHub_acces_token.setObjectName(u"actionHow_to_get_an_GitHub_acces_token")
        self.actionExit = QAction(GitHubManagerLogin)
        self.actionExit.setObjectName(u"actionExit")
        self.centralwidget = QWidget(GitHubManagerLogin)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.ghmImageLabel = QLabel(self.centralwidget)
        self.ghmImageLabel.setObjectName(u"ghmImageLabel")
        self.ghmImageLabel.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.ghmImageLabel)

        self.signInLabel = QLabel(self.centralwidget)
        self.signInLabel.setObjectName(u"signInLabel")
        font = QFont()
        font.setPointSize(15)
        font.setBold(True)
        self.signInLabel.setFont(font)
        self.signInLabel.setLayoutDirection(Qt.LeftToRight)
        self.signInLabel.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.signInLabel)

        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")

        self.verticalLayout.addWidget(self.label)

        self.frame = QFrame(self.centralwidget)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frame)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.tokenLineEdit = QLineEdit(self.frame)
        self.tokenLineEdit.setObjectName(u"tokenLineEdit")

        self.horizontalLayout_2.addWidget(self.tokenLineEdit)

        self.switchVisibilityButton = QPushButton(self.frame)
        self.switchVisibilityButton.setObjectName(u"switchVisibilityButton")

        self.horizontalLayout_2.addWidget(self.switchVisibilityButton)


        self.verticalLayout.addWidget(self.frame)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.signInButton = QPushButton(self.centralwidget)
        self.signInButton.setObjectName(u"signInButton")

        self.horizontalLayout.addWidget(self.signInButton)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.githubAccesTokenButton = QPushButton(self.centralwidget)
        self.githubAccesTokenButton.setObjectName(u"githubAccesTokenButton")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.githubAccesTokenButton.sizePolicy().hasHeightForWidth())
        self.githubAccesTokenButton.setSizePolicy(sizePolicy)
        self.githubAccesTokenButton.setLayoutDirection(Qt.LeftToRight)

        self.horizontalLayout.addWidget(self.githubAccesTokenButton)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.errorWidget = IconLabel(self.centralwidget)
        self.errorWidget.setObjectName(u"errorWidget")
        sizePolicy.setHeightForWidth(self.errorWidget.sizePolicy().hasHeightForWidth())
        self.errorWidget.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.errorWidget)

        GitHubManagerLogin.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(GitHubManagerLogin)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 369, 22))
        self.menuMenu = QMenu(self.menubar)
        self.menuMenu.setObjectName(u"menuMenu")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        GitHubManagerLogin.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(GitHubManagerLogin)
        self.statusbar.setObjectName(u"statusbar")
        GitHubManagerLogin.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuMenu.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuMenu.addAction(self.actionExit)
        self.menuHelp.addAction(self.actionHow_to_get_an_GitHub_acces_token)
        self.menuHelp.addSeparator()
        self.menuHelp.addAction(self.actionAbout)

        self.retranslateUi(GitHubManagerLogin)

        QMetaObject.connectSlotsByName(GitHubManagerLogin)
    # setupUi

    def retranslateUi(self, GitHubManagerLogin):
        GitHubManagerLogin.setWindowTitle(QCoreApplication.translate("GitHubManagerLogin", u"Login", None))
        self.actionAbout.setText(QCoreApplication.translate("GitHubManagerLogin", u"About", None))
        self.actionHow_to_get_an_GitHub_acces_token.setText(QCoreApplication.translate("GitHubManagerLogin", u"How to get an GitHub acces token", None))
        self.actionExit.setText(QCoreApplication.translate("GitHubManagerLogin", u"Exit", None))
        self.ghmImageLabel.setText("")
        self.signInLabel.setText(QCoreApplication.translate("GitHubManagerLogin", u"Sign in to GitHub Manager", None))
        self.label.setText(QCoreApplication.translate("GitHubManagerLogin", u"Personal acces token:", None))
        self.tokenLineEdit.setText("")
        self.tokenLineEdit.setPlaceholderText(QCoreApplication.translate("GitHubManagerLogin", u"ghp_W5FU93CFrM5y5a56fsaFFFV1EYaIf", None))
        self.switchVisibilityButton.setText("")
        self.signInButton.setText(QCoreApplication.translate("GitHubManagerLogin", u"Sign in", None))
        self.githubAccesTokenButton.setText(QCoreApplication.translate("GitHubManagerLogin", u"Generate Access Token", None))
        self.menuMenu.setTitle(QCoreApplication.translate("GitHubManagerLogin", u"Menu", None))
        self.menuHelp.setTitle(QCoreApplication.translate("GitHubManagerLogin", u"Help", None))
    # retranslateUi

