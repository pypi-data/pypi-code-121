# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'signmessagedialog.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_SignMessageDialog(object):
    def setupUi(self, SignMessageDialog):
        if not SignMessageDialog.objectName():
            SignMessageDialog.setObjectName(u"SignMessageDialog")
        SignMessageDialog.resize(957, 350)
        self.buttonBox = QDialogButtonBox(SignMessageDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(600, 300, 341, 32))
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Close)
        self.label = QLabel(SignMessageDialog)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(20, 70, 61, 18))
        self.msg_textedit = QPlainTextEdit(SignMessageDialog)
        self.msg_textedit.setObjectName(u"msg_textedit")
        self.msg_textedit.setGeometry(QRect(80, 20, 861, 131))
        self.label_2 = QLabel(SignMessageDialog)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(20, 180, 121, 18))
        self.path_lineedit = QLineEdit(SignMessageDialog)
        self.path_lineedit.setObjectName(u"path_lineedit")
        self.path_lineedit.setGeometry(QRect(150, 170, 391, 32))
        self.signmsg_button = QPushButton(SignMessageDialog)
        self.signmsg_button.setObjectName(u"signmsg_button")
        self.signmsg_button.setGeometry(QRect(570, 170, 101, 34))
        self.signmsg_button.setAutoDefault(False)
        self.label_3 = QLabel(SignMessageDialog)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(20, 230, 71, 18))
        self.sig_textedit = QPlainTextEdit(SignMessageDialog)
        self.sig_textedit.setObjectName(u"sig_textedit")
        self.sig_textedit.setGeometry(QRect(90, 220, 851, 61))
        self.sig_textedit.setTextInteractionFlags(Qt.TextSelectableByKeyboard|Qt.TextSelectableByMouse)

        self.retranslateUi(SignMessageDialog)
        self.buttonBox.accepted.connect(SignMessageDialog.accept)
        self.buttonBox.rejected.connect(SignMessageDialog.reject)

        self.signmsg_button.setDefault(True)


        QMetaObject.connectSlotsByName(SignMessageDialog)
    # setupUi

    def retranslateUi(self, SignMessageDialog):
        SignMessageDialog.setWindowTitle(QCoreApplication.translate("SignMessageDialog", u"Dialog", None))
        self.label.setText(QCoreApplication.translate("SignMessageDialog", u"Message", None))
        self.label_2.setText(QCoreApplication.translate("SignMessageDialog", u"Key Derivation Path", None))
        self.signmsg_button.setText(QCoreApplication.translate("SignMessageDialog", u"Sign Message", None))
        self.label_3.setText(QCoreApplication.translate("SignMessageDialog", u"Signature", None))
    # retranslateUi

