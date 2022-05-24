# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'getxpubdialog.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_GetXpubDialog(object):
    def setupUi(self, GetXpubDialog):
        if not GetXpubDialog.objectName():
            GetXpubDialog.setObjectName(u"GetXpubDialog")
        GetXpubDialog.resize(1205, 158)
        self.path_label = QLabel(GetXpubDialog)
        self.path_label.setObjectName(u"path_label")
        self.path_label.setGeometry(QRect(320, 20, 101, 31))
        self.path_lineedit = QLineEdit(GetXpubDialog)
        self.path_lineedit.setObjectName(u"path_lineedit")
        self.path_lineedit.setGeometry(QRect(430, 20, 401, 32))
        self.buttonBox = QDialogButtonBox(GetXpubDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(1100, 110, 91, 34))
        self.buttonBox.setFocusPolicy(Qt.NoFocus)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Close)
        self.getxpub_button = QPushButton(GetXpubDialog)
        self.getxpub_button.setObjectName(u"getxpub_button")
        self.getxpub_button.setGeometry(QRect(840, 20, 88, 34))
        self.getxpub_button.setAutoDefault(False)
        self.xpub_label = QLabel(GetXpubDialog)
        self.xpub_label.setObjectName(u"xpub_label")
        self.xpub_label.setGeometry(QRect(30, 70, 41, 31))
        self.xpub_lineedit = QLineEdit(GetXpubDialog)
        self.xpub_lineedit.setObjectName(u"xpub_lineedit")
        self.xpub_lineedit.setGeometry(QRect(70, 70, 1121, 32))
        self.xpub_lineedit.setFocusPolicy(Qt.NoFocus)
        self.xpub_lineedit.setReadOnly(True)
        self.buttonBox.raise_()
        self.path_label.raise_()
        self.path_lineedit.raise_()
        self.getxpub_button.raise_()
        self.xpub_label.raise_()
        self.xpub_lineedit.raise_()

        self.retranslateUi(GetXpubDialog)

        self.getxpub_button.setDefault(True)


        QMetaObject.connectSlotsByName(GetXpubDialog)
    # setupUi

    def retranslateUi(self, GetXpubDialog):
        GetXpubDialog.setWindowTitle(QCoreApplication.translate("GetXpubDialog", u"Dialog", None))
        self.path_label.setText(QCoreApplication.translate("GetXpubDialog", u"Derivation Path", None))
        self.getxpub_button.setText(QCoreApplication.translate("GetXpubDialog", u"Get xpub", None))
        self.xpub_label.setText(QCoreApplication.translate("GetXpubDialog", u"xpub", None))
    # retranslateUi

