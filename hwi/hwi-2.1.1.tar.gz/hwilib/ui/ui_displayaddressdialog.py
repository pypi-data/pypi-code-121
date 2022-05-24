# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'displayaddressdialog.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_DisplayAddressDialog(object):
    def setupUi(self, DisplayAddressDialog):
        if not DisplayAddressDialog.objectName():
            DisplayAddressDialog.setObjectName(u"DisplayAddressDialog")
        DisplayAddressDialog.resize(469, 196)
        self.buttonBox = QDialogButtonBox(DisplayAddressDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(350, 150, 101, 32))
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Close)
        self.path_lineedit = QLineEdit(DisplayAddressDialog)
        self.path_lineedit.setObjectName(u"path_lineedit")
        self.path_lineedit.setGeometry(QRect(120, 10, 331, 32))
        self.label = QLabel(DisplayAddressDialog)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 20, 111, 18))
        self.go_button = QPushButton(DisplayAddressDialog)
        self.go_button.setObjectName(u"go_button")
        self.go_button.setGeometry(QRect(410, 50, 41, 41))
        self.go_button.setAutoDefault(False)
        self.label_2 = QLabel(DisplayAddressDialog)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(10, 120, 58, 18))
        self.address_lineedit = QLineEdit(DisplayAddressDialog)
        self.address_lineedit.setObjectName(u"address_lineedit")
        self.address_lineedit.setGeometry(QRect(70, 110, 381, 32))
        self.address_lineedit.setReadOnly(True)
        self.type_groupbox = QGroupBox(DisplayAddressDialog)
        self.type_groupbox.setObjectName(u"type_groupbox")
        self.type_groupbox.setGeometry(QRect(10, 50, 381, 40))
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.type_groupbox.sizePolicy().hasHeightForWidth())
        self.type_groupbox.setSizePolicy(sizePolicy)
        self.type_groupbox.setMinimumSize(QSize(0, 30))
        self.sh_wpkh_radio = QRadioButton(self.type_groupbox)
        self.sh_wpkh_radio.setObjectName(u"sh_wpkh_radio")
        self.sh_wpkh_radio.setGeometry(QRect(10, 10, 121, 22))
        self.sh_wpkh_radio.setChecked(True)
        self.wpkh_radio = QRadioButton(self.type_groupbox)
        self.wpkh_radio.setObjectName(u"wpkh_radio")
        self.wpkh_radio.setGeometry(QRect(150, 10, 91, 22))
        self.radioButton = QRadioButton(self.type_groupbox)
        self.radioButton.setObjectName(u"radioButton")
        self.radioButton.setGeometry(QRect(260, 10, 105, 22))

        self.retranslateUi(DisplayAddressDialog)
        self.buttonBox.accepted.connect(DisplayAddressDialog.accept)
        self.buttonBox.rejected.connect(DisplayAddressDialog.reject)

        self.go_button.setDefault(True)


        QMetaObject.connectSlotsByName(DisplayAddressDialog)
    # setupUi

    def retranslateUi(self, DisplayAddressDialog):
        DisplayAddressDialog.setWindowTitle(QCoreApplication.translate("DisplayAddressDialog", u"Dialog", None))
        self.label.setText(QCoreApplication.translate("DisplayAddressDialog", u"Derivation Path", None))
        self.go_button.setText(QCoreApplication.translate("DisplayAddressDialog", u"Go", None))
        self.label_2.setText(QCoreApplication.translate("DisplayAddressDialog", u"Address", None))
        self.type_groupbox.setTitle("")
        self.sh_wpkh_radio.setText(QCoreApplication.translate("DisplayAddressDialog", u"P2SH-P2WPKH", None))
        self.wpkh_radio.setText(QCoreApplication.translate("DisplayAddressDialog", u"P2WPKH", None))
        self.radioButton.setText(QCoreApplication.translate("DisplayAddressDialog", u"P2PKH", None))
    # retranslateUi

