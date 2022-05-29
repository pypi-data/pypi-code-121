# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'overview.ui'
##
## Created by: Qt User Interface Compiler version 6.3.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject)
from PySide6.QtGui import (QFont)
from PySide6.QtWidgets import (QGridLayout, QLabel, QLayout,
                               QSizePolicy, QVBoxLayout, QWidget)

class Ui_Overview(object):
    def setupUi(self, Overview):
        if not Overview.objectName():
            Overview.setObjectName(u"Overview")
        Overview.resize(827, 439)
        self.verticalLayout = QVBoxLayout(Overview)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(Overview)
        self.label.setObjectName(u"label")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        font = QFont()
        font.setPointSize(13)
        font.setBold(True)
        self.label.setFont(font)

        self.verticalLayout.addWidget(self.label)

        self.gridLayout = QGridLayout()
        self.gridLayout.setSpacing(2)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setSizeConstraint(QLayout.SetDefaultConstraint)

        self.verticalLayout.addLayout(self.gridLayout)

        self.label_2 = QLabel(Overview)
        self.label_2.setObjectName(u"label_2")
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setFont(font)

        self.verticalLayout.addWidget(self.label_2)

        self.contributionsWidget = QWidget(Overview)
        self.contributionsWidget.setObjectName(u"contributionsWidget")

        self.verticalLayout.addWidget(self.contributionsWidget)

        self.retranslateUi(Overview)

        QMetaObject.connectSlotsByName(Overview)
    # setupUi

    def retranslateUi(self, Overview):
        Overview.setWindowTitle(QCoreApplication.translate("Overview", u"Form", None))
        self.label.setText(QCoreApplication.translate("Overview", u"Popular repositories", None))
        self.label_2.setText(QCoreApplication.translate("Overview", u"Last year contributions", None))
    # retranslateUi

