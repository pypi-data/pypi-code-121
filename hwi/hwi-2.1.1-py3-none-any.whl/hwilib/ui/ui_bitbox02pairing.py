# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'bitbox02pairing.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_BitBox02PairingDialog(object):
    def setupUi(self, BitBox02PairingDialog):
        if not BitBox02PairingDialog.objectName():
            BitBox02PairingDialog.setObjectName(u"BitBox02PairingDialog")
        BitBox02PairingDialog.setWindowModality(Qt.WindowModal)
        BitBox02PairingDialog.resize(400, 209)
        self.buttonBox = QDialogButtonBox(BitBox02PairingDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(30, 160, 341, 32))
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.No|QDialogButtonBox.Yes)
        self.pairingCode = QLabel(BitBox02PairingDialog)
        self.pairingCode.setObjectName(u"pairingCode")
        self.pairingCode.setGeometry(QRect(20, 80, 331, 61))
        font = QFont()
        font.setFamily(u"DejaVu Sans Mono")
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.pairingCode.setFont(font)
        self.pairingCode.setTextFormat(Qt.RichText)
        self.pairingCode.setAlignment(Qt.AlignCenter)
        self.label_2 = QLabel(BitBox02PairingDialog)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(20, 10, 351, 61))
        font1 = QFont()
        font1.setPointSize(11)
        self.label_2.setFont(font1)
        self.label_2.setTextFormat(Qt.PlainText)

        self.retranslateUi(BitBox02PairingDialog)
        self.buttonBox.accepted.connect(BitBox02PairingDialog.accept)
        self.buttonBox.rejected.connect(BitBox02PairingDialog.reject)

        QMetaObject.connectSlotsByName(BitBox02PairingDialog)
    # setupUi

    def retranslateUi(self, BitBox02PairingDialog):
        BitBox02PairingDialog.setWindowTitle(QCoreApplication.translate("BitBox02PairingDialog", u"Dialog", None))
        self.pairingCode.setText("")
        self.label_2.setText(QCoreApplication.translate("BitBox02PairingDialog", u"Please verify the pairing code matches what is\n"
"shown on your BitBox02.", None))
    # retranslateUi

