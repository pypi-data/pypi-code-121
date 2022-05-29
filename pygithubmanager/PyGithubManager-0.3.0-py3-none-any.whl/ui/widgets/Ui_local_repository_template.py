# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'local_repository_template.ui'
##
## Created by: Qt User Interface Compiler version 6.3.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject)
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QLineEdit,
                               QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout)


class Ui_LocalRepositoryTemplate(object):
    def setupUi(self, LocalRepositoryTemplate):
        if not LocalRepositoryTemplate.objectName():
            LocalRepositoryTemplate.setObjectName(u"LocalRepositoryTemplate")
        LocalRepositoryTemplate.resize(554, 85)
        self.verticalLayout_2 = QVBoxLayout(LocalRepositoryTemplate)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.repoNameLabel = QLabel(LocalRepositoryTemplate)
        self.repoNameLabel.setObjectName(u"repoNameLabel")

        self.horizontalLayout.addWidget(self.repoNameLabel)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.githubButton = QPushButton(LocalRepositoryTemplate)
        self.githubButton.setObjectName(u"githubButton")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.githubButton.sizePolicy().hasHeightForWidth())
        self.githubButton.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.githubButton)

        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label = QLabel(LocalRepositoryTemplate)
        self.label.setObjectName(u"label")

        self.horizontalLayout_2.addWidget(self.label)

        self.pathLineEdit = QLineEdit(LocalRepositoryTemplate)
        self.pathLineEdit.setObjectName(u"pathLineEdit")

        self.horizontalLayout_2.addWidget(self.pathLineEdit)

        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.retranslateUi(LocalRepositoryTemplate)

        QMetaObject.connectSlotsByName(LocalRepositoryTemplate)

    # setupUi

    def retranslateUi(self, LocalRepositoryTemplate):
        LocalRepositoryTemplate.setWindowTitle(QCoreApplication.translate("LocalRepositoryTemplate", u"Form", None))
        self.repoNameLabel.setText(QCoreApplication.translate("LocalRepositoryTemplate", u"repo-name", None))
        self.githubButton.setText("")
        self.label.setText(QCoreApplication.translate("LocalRepositoryTemplate", u"Path:", None))
    # retranslateUi
