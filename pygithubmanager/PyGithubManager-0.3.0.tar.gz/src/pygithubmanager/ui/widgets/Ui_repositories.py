# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'repositories.ui'
##
## Created by: Qt User Interface Compiler version 6.3.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject)
from PySide6.QtGui import (QFont)
from PySide6.QtWidgets import (QHBoxLayout, QLineEdit, QListWidget,
                               QPushButton, QSizePolicy, QVBoxLayout)


class Ui_Repositories(object):
    def setupUi(self, Repositories):
        if not Repositories.objectName():
            Repositories.setObjectName(u"Repositories")
        Repositories.resize(556, 357)
        self.verticalLayout = QVBoxLayout(Repositories)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(-1, -1, -1, 0)
        self.lineEdit = QLineEdit(Repositories)
        self.lineEdit.setObjectName(u"lineEdit")

        self.horizontalLayout.addWidget(self.lineEdit)

        self.newButton = QPushButton(Repositories)
        self.newButton.setObjectName(u"newButton")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.newButton.sizePolicy().hasHeightForWidth())
        self.newButton.setSizePolicy(sizePolicy)
        font = QFont()
        font.setBold(True)
        self.newButton.setFont(font)

        self.horizontalLayout.addWidget(self.newButton)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.listWidget = QListWidget(Repositories)
        self.listWidget.setObjectName(u"listWidget")

        self.verticalLayout.addWidget(self.listWidget)

        self.retranslateUi(Repositories)

        QMetaObject.connectSlotsByName(Repositories)
    # setupUi

    def retranslateUi(self, Repositories):
        Repositories.setWindowTitle(QCoreApplication.translate("Repositories", u"Form", None))
        self.lineEdit.setPlaceholderText(QCoreApplication.translate("Repositories", u"Find a repository...", None))
        self.newButton.setText(QCoreApplication.translate("Repositories", u"New", None))
    # retranslateUi

