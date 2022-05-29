# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'aboutwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.3.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject, Qt)
from PySide6.QtGui import (QAction, QFont)
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QLayout,
                               QSizePolicy, QStatusBar, QVBoxLayout,
                               QWidget)

from widgets.HyperlinkLabel import HyperlinkLabel


class Ui_GitHubManagerAbout(object):
    def setupUi(self, GitHubManagerAbout):
        if not GitHubManagerAbout.objectName():
            GitHubManagerAbout.setObjectName(u"GitHubManagerAbout")
        GitHubManagerAbout.setEnabled(True)
        GitHubManagerAbout.resize(432, 192)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(GitHubManagerAbout.sizePolicy().hasHeightForWidth())
        GitHubManagerAbout.setSizePolicy(sizePolicy)
        GitHubManagerAbout.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.actionAbout = QAction(GitHubManagerAbout)
        self.actionAbout.setObjectName(u"actionAbout")
        self.actionHow_to_get_an_GitHub_acces_token = QAction(GitHubManagerAbout)
        self.actionHow_to_get_an_GitHub_acces_token.setObjectName(u"actionHow_to_get_an_GitHub_acces_token")
        self.actionExit = QAction(GitHubManagerAbout)
        self.actionExit.setObjectName(u"actionExit")
        self.centralwidget = QWidget(GitHubManagerAbout)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_2 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.signInLabel = QLabel(self.centralwidget)
        self.signInLabel.setObjectName(u"signInLabel")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.signInLabel.sizePolicy().hasHeightForWidth())
        self.signInLabel.setSizePolicy(sizePolicy1)
        font = QFont()
        font.setPointSize(15)
        font.setBold(True)
        self.signInLabel.setFont(font)
        self.signInLabel.setLayoutDirection(Qt.LeftToRight)
        self.signInLabel.setAlignment(Qt.AlignCenter)

        self.verticalLayout_2.addWidget(self.signInLabel)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.ghmImageLabel = QLabel(self.centralwidget)
        self.ghmImageLabel.setObjectName(u"ghmImageLabel")
        sizePolicy2 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.ghmImageLabel.sizePolicy().hasHeightForWidth())
        self.ghmImageLabel.setSizePolicy(sizePolicy2)
        self.ghmImageLabel.setAlignment(Qt.AlignCenter)

        self.horizontalLayout.addWidget(self.ghmImageLabel)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        sizePolicy3 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy3)
        font1 = QFont()
        font1.setBold(True)
        self.label.setFont(font1)

        self.horizontalLayout_2.addWidget(self.label)

        self.versionLabel = QLabel(self.centralwidget)
        self.versionLabel.setObjectName(u"versionLabel")
        sizePolicy1.setHeightForWidth(self.versionLabel.sizePolicy().hasHeightForWidth())
        self.versionLabel.setSizePolicy(sizePolicy1)

        self.horizontalLayout_2.addWidget(self.versionLabel)

        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")
        sizePolicy3.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy3)
        self.label_2.setFont(font1)

        self.horizontalLayout_3.addWidget(self.label_2)

        self.gitHubLabel = HyperlinkLabel(self.centralwidget)
        self.gitHubLabel.setObjectName(u"gitHubLabel")
        sizePolicy1.setHeightForWidth(self.gitHubLabel.sizePolicy().hasHeightForWidth())
        self.gitHubLabel.setSizePolicy(sizePolicy1)

        self.horizontalLayout_3.addWidget(self.gitHubLabel)

        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_4 = QLabel(self.centralwidget)
        self.label_4.setObjectName(u"label_4")
        sizePolicy3.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy3)
        self.label_4.setFont(font1)

        self.horizontalLayout_4.addWidget(self.label_4)

        self.issueTrackerLabel = HyperlinkLabel(self.centralwidget)
        self.issueTrackerLabel.setObjectName(u"issueTrackerLabel")
        sizePolicy1.setHeightForWidth(self.issueTrackerLabel.sizePolicy().hasHeightForWidth())
        self.issueTrackerLabel.setSizePolicy(sizePolicy1)

        self.horizontalLayout_4.addWidget(self.issueTrackerLabel)

        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_6 = QLabel(self.centralwidget)
        self.label_6.setObjectName(u"label_6")
        sizePolicy3.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy3)
        self.label_6.setFont(font1)

        self.horizontalLayout_5.addWidget(self.label_6)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_7 = QLabel(self.centralwidget)
        self.label_7.setObjectName(u"label_7")
        sizePolicy3.setHeightForWidth(self.label_7.sizePolicy().hasHeightForWidth())
        self.label_7.setSizePolicy(sizePolicy3)

        self.horizontalLayout_6.addWidget(self.label_7)

        self.icons8Label = HyperlinkLabel(self.centralwidget)
        self.icons8Label.setObjectName(u"icons8Label")
        sizePolicy1.setHeightForWidth(self.icons8Label.sizePolicy().hasHeightForWidth())
        self.icons8Label.setSizePolicy(sizePolicy1)

        self.horizontalLayout_6.addWidget(self.icons8Label)

        self.verticalLayout_3.addLayout(self.horizontalLayout_6)

        self.horizontalLayout_5.addLayout(self.verticalLayout_3)

        self.verticalLayout.addLayout(self.horizontalLayout_5)

        self.horizontalLayout.addLayout(self.verticalLayout)

        self.verticalLayout_2.addLayout(self.horizontalLayout)

        GitHubManagerAbout.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(GitHubManagerAbout)
        self.statusbar.setObjectName(u"statusbar")
        GitHubManagerAbout.setStatusBar(self.statusbar)

        self.retranslateUi(GitHubManagerAbout)

        QMetaObject.connectSlotsByName(GitHubManagerAbout)

    # setupUi

    def retranslateUi(self, GitHubManagerAbout):
        GitHubManagerAbout.setWindowTitle(QCoreApplication.translate("GitHubManagerAbout", u"About", None))
        self.actionAbout.setText(QCoreApplication.translate("GitHubManagerAbout", u"About", None))
        self.actionHow_to_get_an_GitHub_acces_token.setText(
            QCoreApplication.translate("GitHubManagerAbout", u"How to get an GitHub acces token", None))
        self.actionExit.setText(QCoreApplication.translate("GitHubManagerAbout", u"Exit", None))
        self.signInLabel.setText(QCoreApplication.translate("GitHubManagerAbout", u"About GitHub Manager", None))
        self.ghmImageLabel.setText("")
        self.label.setText(QCoreApplication.translate("GitHubManagerAbout", u"Version:", None))
        self.versionLabel.setText(QCoreApplication.translate("GitHubManagerAbout", u"0.0", None))
        self.label_2.setText(QCoreApplication.translate("GitHubManagerAbout", u"GitHub:", None))
        self.gitHubLabel.setText(
            QCoreApplication.translate("GitHubManagerAbout", u"https://github.com/DomiTP/GitHub-Manager", None))
        self.label_4.setText(QCoreApplication.translate("GitHubManagerAbout", u"GitHub Issue Tracker:", None))
        self.issueTrackerLabel.setText(
            QCoreApplication.translate("GitHubManagerAbout", u"https://github.com/DomiTP/GitHub-Manager/issues", None))
        self.label_6.setText(QCoreApplication.translate("GitHubManagerAbout", u"Resources:", None))
        self.label_7.setText(QCoreApplication.translate("GitHubManagerAbout", u"Icons by icons8:", None))
        self.icons8Label.setText(QCoreApplication.translate("GitHubManagerAbout", u"https://icons8.com", None))
    # retranslateUi
