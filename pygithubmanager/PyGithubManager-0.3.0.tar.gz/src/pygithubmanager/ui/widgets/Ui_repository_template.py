# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'repository_template.ui'
##
## Created by: Qt User Interface Compiler version 6.3.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject)
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QPushButton,
                               QSizePolicy, QSpacerItem, QVBoxLayout)

from widgets.IconLabel import IconLabel


class Ui_RepositoryTemplate(object):
    def setupUi(self, RepositoryTemplate):
        if not RepositoryTemplate.objectName():
            RepositoryTemplate.setObjectName(u"RepositoryTemplate")
        RepositoryTemplate.resize(505, 110)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(RepositoryTemplate.sizePolicy().hasHeightForWidth())
        RepositoryTemplate.setSizePolicy(sizePolicy)
        self.verticalLayout_2 = QVBoxLayout(RepositoryTemplate)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.repoNameLabel = QLabel(RepositoryTemplate)
        self.repoNameLabel.setObjectName(u"repoNameLabel")

        self.horizontalLayout.addWidget(self.repoNameLabel)

        self.visibilityLabel = QLabel(RepositoryTemplate)
        self.visibilityLabel.setObjectName(u"visibilityLabel")

        self.horizontalLayout.addWidget(self.visibilityLabel)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.starButton = QPushButton(RepositoryTemplate)
        self.starButton.setObjectName(u"starButton")

        self.horizontalLayout.addWidget(self.starButton)

        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.forkWidget = IconLabel(RepositoryTemplate)
        self.forkWidget.setObjectName(u"forkWidget")
        sizePolicy1 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.forkWidget.sizePolicy().hasHeightForWidth())
        self.forkWidget.setSizePolicy(sizePolicy1)

        self.verticalLayout_2.addWidget(self.forkWidget)

        self.repoDescLabel = QLabel(RepositoryTemplate)
        self.repoDescLabel.setObjectName(u"repoDescLabel")

        self.verticalLayout_2.addWidget(self.repoDescLabel)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.licenseIconLabel = QLabel(RepositoryTemplate)
        self.licenseIconLabel.setObjectName(u"licenseIconLabel")

        self.horizontalLayout_2.addWidget(self.licenseIconLabel)

        self.licenseNameLabel = QLabel(RepositoryTemplate)
        self.licenseNameLabel.setObjectName(u"licenseNameLabel")

        self.horizontalLayout_2.addWidget(self.licenseNameLabel)

        self.horizontalSpacer_3 = QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_3)

        self.updatedLabel = QLabel(RepositoryTemplate)
        self.updatedLabel.setObjectName(u"updatedLabel")

        self.horizontalLayout_2.addWidget(self.updatedLabel)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.retranslateUi(RepositoryTemplate)

        QMetaObject.connectSlotsByName(RepositoryTemplate)

    # setupUi

    def retranslateUi(self, RepositoryTemplate):
        RepositoryTemplate.setWindowTitle(QCoreApplication.translate("RepositoryTemplate", u"Form", None))
        self.repoNameLabel.setText(QCoreApplication.translate("RepositoryTemplate", u"repo-name", None))
        self.visibilityLabel.setText(QCoreApplication.translate("RepositoryTemplate", u"public", None))
        self.starButton.setText(QCoreApplication.translate("RepositoryTemplate", u"Star", None))
        self.repoDescLabel.setText(QCoreApplication.translate("RepositoryTemplate", u"repo desc", None))
        self.licenseIconLabel.setText("")
        self.licenseNameLabel.setText(QCoreApplication.translate("RepositoryTemplate", u"License Name", None))
        self.updatedLabel.setText(QCoreApplication.translate("RepositoryTemplate", u"Updated", None))
    # retranslateUi
