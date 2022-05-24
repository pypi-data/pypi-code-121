# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'signpsbtdialog.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_SignPSBTDialog(object):
    def setupUi(self, SignPSBTDialog):
        if not SignPSBTDialog.objectName():
            SignPSBTDialog.setObjectName(u"SignPSBTDialog")
        SignPSBTDialog.resize(987, 813)
        self.buttonBox = QDialogButtonBox(SignPSBTDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(630, 760, 341, 32))
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Close)
        self.label = QLabel(SignPSBTDialog)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(20, 180, 58, 61))
        self.label.setWordWrap(True)
        self.psbt_in_textedit = QPlainTextEdit(SignPSBTDialog)
        self.psbt_in_textedit.setObjectName(u"psbt_in_textedit")
        self.psbt_in_textedit.setGeometry(QRect(90, 20, 881, 321))
        self.psbt_out_textedit = QPlainTextEdit(SignPSBTDialog)
        self.psbt_out_textedit.setObjectName(u"psbt_out_textedit")
        self.psbt_out_textedit.setGeometry(QRect(90, 410, 881, 331))
        self.psbt_out_textedit.setTextInteractionFlags(Qt.TextSelectableByKeyboard|Qt.TextSelectableByMouse)
        self.label_2 = QLabel(SignPSBTDialog)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(30, 530, 58, 61))
        self.label_2.setWordWrap(True)
        self.sign_psbt_button = QPushButton(SignPSBTDialog)
        self.sign_psbt_button.setObjectName(u"sign_psbt_button")
        self.sign_psbt_button.setGeometry(QRect(480, 350, 88, 34))
        self.sign_psbt_button.setAutoDefault(False)

        self.retranslateUi(SignPSBTDialog)
        self.buttonBox.accepted.connect(SignPSBTDialog.accept)
        self.buttonBox.rejected.connect(SignPSBTDialog.reject)

        self.sign_psbt_button.setDefault(True)


        QMetaObject.connectSlotsByName(SignPSBTDialog)
    # setupUi

    def retranslateUi(self, SignPSBTDialog):
        SignPSBTDialog.setWindowTitle(QCoreApplication.translate("SignPSBTDialog", u"Dialog", None))
        self.label.setText(QCoreApplication.translate("SignPSBTDialog", u"PSBT To Sign", None))
        self.label_2.setText(QCoreApplication.translate("SignPSBTDialog", u"PSBT Result", None))
        self.sign_psbt_button.setText(QCoreApplication.translate("SignPSBTDialog", u"Sign PSBT", None))
    # retranslateUi

