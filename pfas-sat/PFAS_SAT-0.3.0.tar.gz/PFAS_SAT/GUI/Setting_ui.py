# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Setting.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from . import PFAS_SAT_rc

class Ui_Setting(object):
    def setupUi(self, Setting):
        if not Setting.objectName():
            Setting.setObjectName(u"Setting")
        Setting.resize(500, 443)
        Setting.setMaximumSize(QSize(500, 16777215))
        icon = QIcon()
        icon.addFile(u":/icons/ICONS/PFAS_SAT_1.png", QSize(), QIcon.Normal, QIcon.Off)
        Setting.setWindowIcon(icon)
        self.gridLayout_2 = QGridLayout(Setting)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.label = QLabel(Setting)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setWordWrap(True)

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.CutOff = QLineEdit(Setting)
        self.CutOff.setObjectName(u"CutOff")
        self.CutOff.setMaximumSize(QSize(200, 16777215))

        self.gridLayout.addWidget(self.CutOff, 0, 1, 1, 1)

        self.label_3 = QLabel(Setting)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setWordWrap(True)

        self.gridLayout.addWidget(self.label_3, 0, 2, 1, 1)

        self.label_2 = QLabel(Setting)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setFont(font)
        self.label_2.setWordWrap(True)

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.ErrorLimit = QLineEdit(Setting)
        self.ErrorLimit.setObjectName(u"ErrorLimit")
        self.ErrorLimit.setMaximumSize(QSize(200, 16777215))

        self.gridLayout.addWidget(self.ErrorLimit, 1, 1, 1, 1)

        self.label_4 = QLabel(Setting)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 1, 2, 1, 1)


        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.Cancel = QPushButton(Setting)
        self.Cancel.setObjectName(u"Cancel")
        icon1 = QIcon()
        icon1.addFile(u":/icons/ICONS/Remove.png", QSize(), QIcon.Normal, QIcon.Off)
        self.Cancel.setIcon(icon1)

        self.horizontalLayout.addWidget(self.Cancel)

        self.Apply = QPushButton(Setting)
        self.Apply.setObjectName(u"Apply")
        icon2 = QIcon()
        icon2.addFile(u":/icons/ICONS/Update.png", QSize(), QIcon.Normal, QIcon.Off)
        self.Apply.setIcon(icon2)

        self.horizontalLayout.addWidget(self.Apply)


        self.gridLayout_2.addLayout(self.horizontalLayout, 2, 0, 1, 1)

        self.PFAS_box = QGroupBox(Setting)
        self.PFAS_box.setObjectName(u"PFAS_box")
        self.PFAS_box.setFont(font)
        self.gridLayout_4 = QGridLayout(self.PFAS_box)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.PFAS_Layout = QGridLayout()
        self.PFAS_Layout.setObjectName(u"PFAS_Layout")

        self.gridLayout_4.addLayout(self.PFAS_Layout, 0, 0, 1, 1)


        self.gridLayout_2.addWidget(self.PFAS_box, 1, 0, 1, 1)


        self.retranslateUi(Setting)

        QMetaObject.connectSlotsByName(Setting)
    # setupUi

    def retranslateUi(self, Setting):
        Setting.setWindowTitle(QCoreApplication.translate("Setting", u"PFAS SAT Setting", None))
        self.label.setText(QCoreApplication.translate("Setting", u"Cut-off", None))
        self.label_3.setText(QCoreApplication.translate("Setting", u"Fraction of Total Incoming PFAS", None))
        self.label_2.setText(QCoreApplication.translate("Setting", u"Acceptable error limit", None))
        self.label_4.setText(QCoreApplication.translate("Setting", u"%", None))
        self.Cancel.setText(QCoreApplication.translate("Setting", u"Cancel", None))
        self.Apply.setText(QCoreApplication.translate("Setting", u"Apply", None))
        self.PFAS_box.setTitle(QCoreApplication.translate("Setting", u"Included PFAS", None))
    # retranslateUi

