# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'setpassphrasedialog.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_SetPassphraseDialog(object):
    def setupUi(self, SetPassphraseDialog):
        if not SetPassphraseDialog.objectName():
            SetPassphraseDialog.setObjectName(u"SetPassphraseDialog")
        SetPassphraseDialog.resize(400, 96)
        self.buttonBox = QDialogButtonBox(SetPassphraseDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(40, 50, 341, 32))
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.passphrase_lineedit = QLineEdit(SetPassphraseDialog)
        self.passphrase_lineedit.setObjectName(u"passphrase_lineedit")
        self.passphrase_lineedit.setGeometry(QRect(30, 10, 351, 32))
        self.passphrase_lineedit.setClearButtonEnabled(False)

        self.retranslateUi(SetPassphraseDialog)
        self.buttonBox.accepted.connect(SetPassphraseDialog.accept)
        self.buttonBox.rejected.connect(SetPassphraseDialog.reject)

        QMetaObject.connectSlotsByName(SetPassphraseDialog)
    # setupUi

    def retranslateUi(self, SetPassphraseDialog):
        SetPassphraseDialog.setWindowTitle(QCoreApplication.translate("SetPassphraseDialog", u"Dialog", None))
    # retranslateUi

