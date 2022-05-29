# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'local_repository.ui'
##
## Created by: Qt User Interface Compiler version 6.3.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject)
from PySide6.QtGui import (QFont)
from PySide6.QtWidgets import (QFormLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSizePolicy,
                               QSpacerItem, QTabWidget, QTreeView, QVBoxLayout,
                               QWidget)

class Ui_localRepository(object):
    def setupUi(self, localRepository):
        if not localRepository.objectName():
            localRepository.setObjectName(u"localRepository")
        localRepository.resize(936, 557)
        self.verticalLayout = QVBoxLayout(localRepository)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.repoLabel = QLabel(localRepository)
        self.repoLabel.setObjectName(u"repoLabel")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.repoLabel.sizePolicy().hasHeightForWidth())
        self.repoLabel.setSizePolicy(sizePolicy)
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.repoLabel.setFont(font)

        self.verticalLayout.addWidget(self.repoLabel)

        self.tabWidget = QTabWidget(localRepository)
        self.tabWidget.setObjectName(u"tabWidget")
        self.infoTab = QWidget()
        self.infoTab.setObjectName(u"infoTab")
        self.verticalLayout_3 = QVBoxLayout(self.infoTab)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.fullNameLabel = QLabel(self.infoTab)
        self.fullNameLabel.setObjectName(u"fullNameLabel")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.fullNameLabel)

        self.fullNameLineEdit = QLineEdit(self.infoTab)
        self.fullNameLineEdit.setObjectName(u"fullNameLineEdit")
        self.fullNameLineEdit.setReadOnly(True)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.fullNameLineEdit)

        self.ownerLabel = QLabel(self.infoTab)
        self.ownerLabel.setObjectName(u"ownerLabel")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.ownerLabel)

        self.ownerLineEdit = QLineEdit(self.infoTab)
        self.ownerLineEdit.setObjectName(u"ownerLineEdit")
        self.ownerLineEdit.setReadOnly(True)

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.ownerLineEdit)

        self.descriptionLabel = QLabel(self.infoTab)
        self.descriptionLabel.setObjectName(u"descriptionLabel")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.descriptionLabel)

        self.descriptionLineEdit = QLineEdit(self.infoTab)
        self.descriptionLineEdit.setObjectName(u"descriptionLineEdit")
        self.descriptionLineEdit.setReadOnly(True)

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.descriptionLineEdit)

        self.createdAtLabel = QLabel(self.infoTab)
        self.createdAtLabel.setObjectName(u"createdAtLabel")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.createdAtLabel)

        self.createdAtLineEdit = QLineEdit(self.infoTab)
        self.createdAtLineEdit.setObjectName(u"createdAtLineEdit")
        self.createdAtLineEdit.setReadOnly(True)

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.createdAtLineEdit)

        self.updatedLabel = QLabel(self.infoTab)
        self.updatedLabel.setObjectName(u"updatedLabel")

        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.updatedLabel)

        self.updatedLineEdit = QLineEdit(self.infoTab)
        self.updatedLineEdit.setObjectName(u"updatedLineEdit")
        self.updatedLineEdit.setReadOnly(True)

        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.updatedLineEdit)

        self.languageLabel = QLabel(self.infoTab)
        self.languageLabel.setObjectName(u"languageLabel")

        self.formLayout.setWidget(5, QFormLayout.LabelRole, self.languageLabel)

        self.languageLineEdit = QLineEdit(self.infoTab)
        self.languageLineEdit.setObjectName(u"languageLineEdit")
        self.languageLineEdit.setReadOnly(True)

        self.formLayout.setWidget(5, QFormLayout.FieldRole, self.languageLineEdit)

        self.forksLabel = QLabel(self.infoTab)
        self.forksLabel.setObjectName(u"forksLabel")

        self.formLayout.setWidget(6, QFormLayout.LabelRole, self.forksLabel)

        self.forksLineEdit = QLineEdit(self.infoTab)
        self.forksLineEdit.setObjectName(u"forksLineEdit")
        self.forksLineEdit.setReadOnly(True)

        self.formLayout.setWidget(6, QFormLayout.FieldRole, self.forksLineEdit)

        self.starsLabel = QLabel(self.infoTab)
        self.starsLabel.setObjectName(u"starsLabel")

        self.formLayout.setWidget(7, QFormLayout.LabelRole, self.starsLabel)

        self.starsLineEdit = QLineEdit(self.infoTab)
        self.starsLineEdit.setObjectName(u"starsLineEdit")
        self.starsLineEdit.setReadOnly(True)

        self.formLayout.setWidget(7, QFormLayout.FieldRole, self.starsLineEdit)

        self.subscribersLabel = QLabel(self.infoTab)
        self.subscribersLabel.setObjectName(u"subscribersLabel")

        self.formLayout.setWidget(8, QFormLayout.LabelRole, self.subscribersLabel)

        self.subscribersLineEdit = QLineEdit(self.infoTab)
        self.subscribersLineEdit.setObjectName(u"subscribersLineEdit")
        self.subscribersLineEdit.setReadOnly(True)

        self.formLayout.setWidget(8, QFormLayout.FieldRole, self.subscribersLineEdit)


        self.verticalLayout_3.addLayout(self.formLayout)

        self.tabWidget.addTab(self.infoTab, "")
        self.filesTab = QWidget()
        self.filesTab.setObjectName(u"filesTab")
        self.verticalLayout_4 = QVBoxLayout(self.filesTab)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.label_2 = QLabel(self.filesTab)
        self.label_2.setObjectName(u"label_2")
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        font1 = QFont()
        font1.setPointSize(11)
        font1.setBold(True)
        self.label_2.setFont(font1)

        self.verticalLayout_4.addWidget(self.label_2)

        self.treeView = QTreeView(self.filesTab)
        self.treeView.setObjectName(u"treeView")

        self.verticalLayout_4.addWidget(self.treeView)

        self.tabWidget.addTab(self.filesTab, "")
        self.commitsTab = QWidget()
        self.commitsTab.setObjectName(u"commitsTab")
        self.verticalLayout_5 = QVBoxLayout(self.commitsTab)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.commitsImageWidget = QWidget(self.commitsTab)
        self.commitsImageWidget.setObjectName(u"commitsImageWidget")

        self.verticalLayout_2.addWidget(self.commitsImageWidget)

        self.verticalLayout_5.addLayout(self.verticalLayout_2)

        self.tabWidget.addTab(self.commitsTab, "")

        self.verticalLayout.addWidget(self.tabWidget)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.deleteButton = QPushButton(localRepository)
        self.deleteButton.setObjectName(u"deleteButton")
        sizePolicy.setHeightForWidth(self.deleteButton.sizePolicy().hasHeightForWidth())
        self.deleteButton.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.deleteButton)

        self.openBrowserButton = QPushButton(localRepository)
        self.openBrowserButton.setObjectName(u"openBrowserButton")
        sizePolicy.setHeightForWidth(self.openBrowserButton.sizePolicy().hasHeightForWidth())
        self.openBrowserButton.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.openBrowserButton)

        self.openFolderButton = QPushButton(localRepository)
        self.openFolderButton.setObjectName(u"openFolderButton")
        sizePolicy.setHeightForWidth(self.openFolderButton.sizePolicy().hasHeightForWidth())
        self.openFolderButton.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.openFolderButton)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(localRepository)

        self.tabWidget.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(localRepository)
    # setupUi

    def retranslateUi(self, localRepository):
        localRepository.setWindowTitle(QCoreApplication.translate("localRepository", u"Form", None))
        self.repoLabel.setText(QCoreApplication.translate("localRepository", u"repo", None))
        self.fullNameLabel.setText(QCoreApplication.translate("localRepository", u"Full name", None))
        self.ownerLabel.setText(QCoreApplication.translate("localRepository", u"Owner", None))
        self.descriptionLabel.setText(QCoreApplication.translate("localRepository", u"Description", None))
        self.createdAtLabel.setText(QCoreApplication.translate("localRepository", u"Created at", None))
        self.updatedLabel.setText(QCoreApplication.translate("localRepository", u"Updated", None))
        self.languageLabel.setText(QCoreApplication.translate("localRepository", u"Language", None))
        self.forksLabel.setText(QCoreApplication.translate("localRepository", u"Forks", None))
        self.starsLabel.setText(QCoreApplication.translate("localRepository", u"Stars", None))
        self.subscribersLabel.setText(QCoreApplication.translate("localRepository", u"Subscribers", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.infoTab),
                                  QCoreApplication.translate("localRepository", u"Info", None))
        self.label_2.setText(QCoreApplication.translate("localRepository", u"Repository files", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.filesTab),
                                  QCoreApplication.translate("localRepository", u"Files", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.commitsTab),
                                  QCoreApplication.translate("localRepository", u"Commits", None))
        self.deleteButton.setText(QCoreApplication.translate("localRepository", u"Delete", None))
        self.openBrowserButton.setText(QCoreApplication.translate("localRepository", u"Open in GitHub", None))
        self.openFolderButton.setText(QCoreApplication.translate("localRepository", u"Open folder", None))
    # retranslateUi

