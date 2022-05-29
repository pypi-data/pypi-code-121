# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'popular_repositories.ui'
##
## Created by: Qt User Interface Compiler version 6.3.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject)
from PySide6.QtWidgets import (QFrame, QHBoxLayout, QLabel,
                               QSizePolicy, QSpacerItem, QVBoxLayout)

from widgets.ClickableLabel import ClickableLabel
from widgets.IconLabel import IconLabel


class Ui_PopularRepositories(object):
    def setupUi(self, PopularRepositories):
        if not PopularRepositories.objectName():
            PopularRepositories.setObjectName(u"PopularRepositories")
        PopularRepositories.resize(192, 128)
        self.verticalLayout = QVBoxLayout(PopularRepositories)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame = QFrame(PopularRepositories)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Box)
        self.frame.setFrameShadow(QFrame.Sunken)
        self.verticalLayout_2 = QVBoxLayout(self.frame)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.nameLabel = ClickableLabel(self.frame)
        self.nameLabel.setObjectName(u"nameLabel")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.nameLabel.sizePolicy().hasHeightForWidth())
        self.nameLabel.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.nameLabel)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.visibilityLabel = QLabel(self.frame)
        self.visibilityLabel.setObjectName(u"visibilityLabel")
        sizePolicy.setHeightForWidth(self.visibilityLabel.sizePolicy().hasHeightForWidth())
        self.visibilityLabel.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.visibilityLabel)

        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.forkWidget = IconLabel(self.frame)
        self.forkWidget.setObjectName(u"forkWidget")
        sizePolicy.setHeightForWidth(self.forkWidget.sizePolicy().hasHeightForWidth())
        self.forkWidget.setSizePolicy(sizePolicy)

        self.verticalLayout_2.addWidget(self.forkWidget)

        self.descLabel = QLabel(self.frame)
        self.descLabel.setObjectName(u"descLabel")

        self.verticalLayout_2.addWidget(self.descLabel)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.langWidget = IconLabel(self.frame)
        self.langWidget.setObjectName(u"langWidget")
        sizePolicy.setHeightForWidth(self.langWidget.sizePolicy().hasHeightForWidth())
        self.langWidget.setSizePolicy(sizePolicy)

        self.horizontalLayout_2.addWidget(self.langWidget)

        self.starsWidget = IconLabel(self.frame)
        self.starsWidget.setObjectName(u"starsWidget")
        sizePolicy.setHeightForWidth(self.starsWidget.sizePolicy().hasHeightForWidth())
        self.starsWidget.setSizePolicy(sizePolicy)

        self.horizontalLayout_2.addWidget(self.starsWidget)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.verticalLayout.addWidget(self.frame)

        self.retranslateUi(PopularRepositories)

        QMetaObject.connectSlotsByName(PopularRepositories)
    # setupUi

    def retranslateUi(self, PopularRepositories):
        PopularRepositories.setWindowTitle(QCoreApplication.translate("PopularRepositories", u"Form", None))
        self.nameLabel.setText(QCoreApplication.translate("PopularRepositories", u"TextLabel", None))
        self.visibilityLabel.setText(QCoreApplication.translate("PopularRepositories", u"TextLabel", None))
        self.descLabel.setText(QCoreApplication.translate("PopularRepositories", u"TextLabel", None))
    # retranslateUi

