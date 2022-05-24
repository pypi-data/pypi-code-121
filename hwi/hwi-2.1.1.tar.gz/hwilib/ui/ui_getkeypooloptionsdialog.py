# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'getkeypooloptionsdialog.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_GetKeypoolOptionsDialog(object):
    def setupUi(self, GetKeypoolOptionsDialog):
        if not GetKeypoolOptionsDialog.objectName():
            GetKeypoolOptionsDialog.setObjectName(u"GetKeypoolOptionsDialog")
        GetKeypoolOptionsDialog.resize(440, 224)
        self.buttonBox = QDialogButtonBox(GetKeypoolOptionsDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(80, 180, 341, 32))
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.label = QLabel(GetKeypoolOptionsDialog)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(20, 20, 41, 18))
        self.label_2 = QLabel(GetKeypoolOptionsDialog)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(20, 60, 31, 18))
        self.start_spinbox = QSpinBox(GetKeypoolOptionsDialog)
        self.start_spinbox.setObjectName(u"start_spinbox")
        self.start_spinbox.setGeometry(QRect(80, 10, 161, 32))
        self.start_spinbox.setMaximum(2147483647)
        self.end_spinbox = QSpinBox(GetKeypoolOptionsDialog)
        self.end_spinbox.setObjectName(u"end_spinbox")
        self.end_spinbox.setGeometry(QRect(80, 50, 161, 32))
        self.end_spinbox.setMaximum(2147483647)
        self.end_spinbox.setValue(1000)
        self.internal_checkbox = QCheckBox(GetKeypoolOptionsDialog)
        self.internal_checkbox.setObjectName(u"internal_checkbox")
        self.internal_checkbox.setGeometry(QRect(280, 10, 88, 22))
        self.keypool_checkbox = QCheckBox(GetKeypoolOptionsDialog)
        self.keypool_checkbox.setObjectName(u"keypool_checkbox")
        self.keypool_checkbox.setGeometry(QRect(280, 40, 88, 22))
        self.keypool_checkbox.setChecked(True)
        self.groupBox = QGroupBox(GetKeypoolOptionsDialog)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(280, 70, 141, 101))
        self.sh_wpkh_radio = QRadioButton(self.groupBox)
        self.sh_wpkh_radio.setObjectName(u"sh_wpkh_radio")
        self.sh_wpkh_radio.setGeometry(QRect(10, 10, 121, 22))
        self.sh_wpkh_radio.setChecked(True)
        self.wpkh_radio = QRadioButton(self.groupBox)
        self.wpkh_radio.setObjectName(u"wpkh_radio")
        self.wpkh_radio.setGeometry(QRect(10, 40, 105, 22))
        self.pkh_radio = QRadioButton(self.groupBox)
        self.pkh_radio.setObjectName(u"pkh_radio")
        self.pkh_radio.setGeometry(QRect(10, 70, 105, 22))
        self.groupBox_2 = QGroupBox(GetKeypoolOptionsDialog)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setGeometry(QRect(10, 90, 231, 91))
        self.account_spinbox = QSpinBox(self.groupBox_2)
        self.account_spinbox.setObjectName(u"account_spinbox")
        self.account_spinbox.setGeometry(QRect(100, 10, 111, 32))
        self.account_spinbox.setMaximum(2147483647)
        self.account_spinbox.setValue(0)
        self.account_radio = QRadioButton(self.groupBox_2)
        self.account_radio.setObjectName(u"account_radio")
        self.account_radio.setGeometry(QRect(10, 10, 81, 22))
        self.account_radio.setChecked(True)
        self.path_radio = QRadioButton(self.groupBox_2)
        self.path_radio.setObjectName(u"path_radio")
        self.path_radio.setGeometry(QRect(10, 50, 61, 22))
        self.path_lineedit = QLineEdit(self.groupBox_2)
        self.path_lineedit.setObjectName(u"path_lineedit")
        self.path_lineedit.setEnabled(False)
        self.path_lineedit.setGeometry(QRect(80, 50, 141, 32))

        self.retranslateUi(GetKeypoolOptionsDialog)
        self.buttonBox.accepted.connect(GetKeypoolOptionsDialog.accept)
        self.buttonBox.rejected.connect(GetKeypoolOptionsDialog.reject)

        QMetaObject.connectSlotsByName(GetKeypoolOptionsDialog)
    # setupUi

    def retranslateUi(self, GetKeypoolOptionsDialog):
        GetKeypoolOptionsDialog.setWindowTitle(QCoreApplication.translate("GetKeypoolOptionsDialog", u"Dialog", None))
        self.label.setText(QCoreApplication.translate("GetKeypoolOptionsDialog", u"Start", None))
        self.label_2.setText(QCoreApplication.translate("GetKeypoolOptionsDialog", u"End", None))
        self.internal_checkbox.setText(QCoreApplication.translate("GetKeypoolOptionsDialog", u"Internal", None))
        self.keypool_checkbox.setText(QCoreApplication.translate("GetKeypoolOptionsDialog", u"keypool", None))
        self.groupBox.setTitle("")
        self.sh_wpkh_radio.setText(QCoreApplication.translate("GetKeypoolOptionsDialog", u"P2SH-P2WPKH", None))
        self.wpkh_radio.setText(QCoreApplication.translate("GetKeypoolOptionsDialog", u"P2WPKH", None))
        self.pkh_radio.setText(QCoreApplication.translate("GetKeypoolOptionsDialog", u"P2PKH", None))
        self.groupBox_2.setTitle("")
        self.account_radio.setText(QCoreApplication.translate("GetKeypoolOptionsDialog", u"Account", None))
        self.path_radio.setText(QCoreApplication.translate("GetKeypoolOptionsDialog", u"Path", None))
        self.path_lineedit.setText(QCoreApplication.translate("GetKeypoolOptionsDialog", u"m/0'/0'/*", None))
    # retranslateUi

