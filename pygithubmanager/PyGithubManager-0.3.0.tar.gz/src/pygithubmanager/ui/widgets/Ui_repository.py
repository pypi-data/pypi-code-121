# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'repository.ui'
##
## Created by: Qt User Interface Compiler version 6.3.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject, Qt)
from PySide6.QtGui import (QFont)
from PySide6.QtWidgets import (QComboBox, QFrame, QHBoxLayout,
                               QLabel, QLayout, QListWidget, QPushButton, QSizePolicy, QSpacerItem, QTabWidget,
                               QVBoxLayout, QWidget)

from widgets.IconLabel import IconLabel


class Ui_repository(object):
    def setupUi(self, repository):
        if not repository.objectName():
            repository.setObjectName(u"repository")
        repository.resize(936, 640)
        self.verticalLayout = QVBoxLayout(repository)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(-1, -1, -1, 0)
        self.repoLabel = QLabel(repository)
        self.repoLabel.setObjectName(u"repoLabel")

        self.horizontalLayout_5.addWidget(self.repoLabel)

        self.watchButton = QPushButton(repository)
        self.watchButton.setObjectName(u"watchButton")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.watchButton.sizePolicy().hasHeightForWidth())
        self.watchButton.setSizePolicy(sizePolicy)

        self.horizontalLayout_5.addWidget(self.watchButton)

        self.forkButton = QPushButton(repository)
        self.forkButton.setObjectName(u"forkButton")
        sizePolicy.setHeightForWidth(self.forkButton.sizePolicy().hasHeightForWidth())
        self.forkButton.setSizePolicy(sizePolicy)

        self.horizontalLayout_5.addWidget(self.forkButton)

        self.starButton = QPushButton(repository)
        self.starButton.setObjectName(u"starButton")
        sizePolicy.setHeightForWidth(self.starButton.sizePolicy().hasHeightForWidth())
        self.starButton.setSizePolicy(sizePolicy)

        self.horizontalLayout_5.addWidget(self.starButton)


        self.verticalLayout.addLayout(self.horizontalLayout_5)

        self.tabWidget = QTabWidget(repository)
        self.tabWidget.setObjectName(u"tabWidget")
        self.code = QWidget()
        self.code.setObjectName(u"code")
        self.horizontalLayout = QHBoxLayout(self.code)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.branchComboBox = QComboBox(self.code)
        self.branchComboBox.setObjectName(u"branchComboBox")
        sizePolicy.setHeightForWidth(self.branchComboBox.sizePolicy().hasHeightForWidth())
        self.branchComboBox.setSizePolicy(sizePolicy)

        self.horizontalLayout_3.addWidget(self.branchComboBox)

        self.branchWidget = QWidget(self.code)
        self.branchWidget.setObjectName(u"branchWidget")
        sizePolicy.setHeightForWidth(self.branchWidget.sizePolicy().hasHeightForWidth())
        self.branchWidget.setSizePolicy(sizePolicy)

        self.horizontalLayout_3.addWidget(self.branchWidget)

        self.tagsWidget = QWidget(self.code)
        self.tagsWidget.setObjectName(u"tagsWidget")
        sizePolicy.setHeightForWidth(self.tagsWidget.sizePolicy().hasHeightForWidth())
        self.tagsWidget.setSizePolicy(sizePolicy)

        self.horizontalLayout_3.addWidget(self.tagsWidget)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)

        self.codeButton = QPushButton(self.code)
        self.codeButton.setObjectName(u"codeButton")
        sizePolicy.setHeightForWidth(self.codeButton.sizePolicy().hasHeightForWidth())
        self.codeButton.setSizePolicy(sizePolicy)

        self.horizontalLayout_3.addWidget(self.codeButton)


        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.frame = QFrame(self.code)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Plain)
        self.horizontalLayout_4 = QHBoxLayout(self.frame)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.profileImageLabel = QLabel(self.frame)
        self.profileImageLabel.setObjectName(u"profileImageLabel")
        sizePolicy.setHeightForWidth(self.profileImageLabel.sizePolicy().hasHeightForWidth())
        self.profileImageLabel.setSizePolicy(sizePolicy)

        self.horizontalLayout_4.addWidget(self.profileImageLabel)

        self.usernameLabel = QLabel(self.frame)
        self.usernameLabel.setObjectName(u"usernameLabel")
        sizePolicy.setHeightForWidth(self.usernameLabel.sizePolicy().hasHeightForWidth())
        self.usernameLabel.setSizePolicy(sizePolicy)

        self.horizontalLayout_4.addWidget(self.usernameLabel)

        self.commitLabel = QLabel(self.frame)
        self.commitLabel.setObjectName(u"commitLabel")
        sizePolicy.setHeightForWidth(self.commitLabel.sizePolicy().hasHeightForWidth())
        self.commitLabel.setSizePolicy(sizePolicy)

        self.horizontalLayout_4.addWidget(self.commitLabel)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_3)

        self.numsLabel = QLabel(self.frame)
        self.numsLabel.setObjectName(u"numsLabel")
        sizePolicy.setHeightForWidth(self.numsLabel.sizePolicy().hasHeightForWidth())
        self.numsLabel.setSizePolicy(sizePolicy)

        self.horizontalLayout_4.addWidget(self.numsLabel)

        self.timeLabel = QLabel(self.frame)
        self.timeLabel.setObjectName(u"timeLabel")
        sizePolicy.setHeightForWidth(self.timeLabel.sizePolicy().hasHeightForWidth())
        self.timeLabel.setSizePolicy(sizePolicy)

        self.horizontalLayout_4.addWidget(self.timeLabel)

        self.commitsWidget = IconLabel(self.frame)
        self.commitsWidget.setObjectName(u"commitsWidget")
        sizePolicy.setHeightForWidth(self.commitsWidget.sizePolicy().hasHeightForWidth())
        self.commitsWidget.setSizePolicy(sizePolicy)

        self.horizontalLayout_4.addWidget(self.commitsWidget)


        self.verticalLayout_2.addWidget(self.frame)

        self.filesListWidget = QListWidget(self.code)
        self.filesListWidget.setObjectName(u"filesListWidget")

        self.verticalLayout_2.addWidget(self.filesListWidget)


        self.horizontalLayout.addLayout(self.verticalLayout_2)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setSizeConstraint(QLayout.SetFixedSize)
        self.verticalLayout_3.setContentsMargins(-1, -1, -1, 0)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setSizeConstraint(QLayout.SetFixedSize)
        self.label = QLabel(self.code)
        self.label.setObjectName(u"label")
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        font = QFont()
        font.setBold(True)
        self.label.setFont(font)

        self.horizontalLayout_2.addWidget(self.label)

        self.configButton = QPushButton(self.code)
        self.configButton.setObjectName(u"configButton")
        sizePolicy.setHeightForWidth(self.configButton.sizePolicy().hasHeightForWidth())
        self.configButton.setSizePolicy(sizePolicy)
        self.configButton.setLayoutDirection(Qt.RightToLeft)

        self.horizontalLayout_2.addWidget(self.configButton)

        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        self.descLabel = QLabel(self.code)
        self.descLabel.setObjectName(u"descLabel")
        sizePolicy.setHeightForWidth(self.descLabel.sizePolicy().hasHeightForWidth())
        self.descLabel.setSizePolicy(sizePolicy)

        self.verticalLayout_3.addWidget(self.descLabel)

        self.licenseWidget = IconLabel(self.code)
        self.licenseWidget.setObjectName(u"licenseWidget")
        sizePolicy.setHeightForWidth(self.licenseWidget.sizePolicy().hasHeightForWidth())
        self.licenseWidget.setSizePolicy(sizePolicy)

        self.verticalLayout_3.addWidget(self.licenseWidget)

        self.starWidget = IconLabel(self.code)
        self.starWidget.setObjectName(u"starWidget")
        sizePolicy.setHeightForWidth(self.starWidget.sizePolicy().hasHeightForWidth())
        self.starWidget.setSizePolicy(sizePolicy)

        self.verticalLayout_3.addWidget(self.starWidget)

        self.watchingWidget = IconLabel(self.code)
        self.watchingWidget.setObjectName(u"watchingWidget")
        sizePolicy.setHeightForWidth(self.watchingWidget.sizePolicy().hasHeightForWidth())
        self.watchingWidget.setSizePolicy(sizePolicy)

        self.verticalLayout_3.addWidget(self.watchingWidget)

        self.forksWidget = IconLabel(self.code)
        self.forksWidget.setObjectName(u"forksWidget")
        sizePolicy.setHeightForWidth(self.forksWidget.sizePolicy().hasHeightForWidth())
        self.forksWidget.setSizePolicy(sizePolicy)

        self.verticalLayout_3.addWidget(self.forksWidget)

        self.line = QFrame(self.code)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_3.addWidget(self.line)

        self.label_2 = QLabel(self.code)
        self.label_2.setObjectName(u"label_2")
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setFont(font)

        self.verticalLayout_3.addWidget(self.label_2)

        self.releasesWidget = IconLabel(self.code)
        self.releasesWidget.setObjectName(u"releasesWidget")
        sizePolicy.setHeightForWidth(self.releasesWidget.sizePolicy().hasHeightForWidth())
        self.releasesWidget.setSizePolicy(sizePolicy)

        self.verticalLayout_3.addWidget(self.releasesWidget)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)

        self.horizontalLayout.addLayout(self.verticalLayout_3)

        self.tabWidget.addTab(self.code, "")
        self.issues = QWidget()
        self.issues.setObjectName(u"issues")
        self.verticalLayout_4 = QVBoxLayout(self.issues)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.issuesListWidget = QListWidget(self.issues)
        self.issuesListWidget.setObjectName(u"issuesListWidget")

        self.verticalLayout_4.addWidget(self.issuesListWidget)

        self.tabWidget.addTab(self.issues, "")

        self.verticalLayout.addWidget(self.tabWidget)

        self.retranslateUi(repository)

        self.tabWidget.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(repository)
    # setupUi

    def retranslateUi(self, repository):
        repository.setWindowTitle(QCoreApplication.translate("repository", u"Form", None))
        self.repoLabel.setText(QCoreApplication.translate("repository", u"repo", None))
        self.watchButton.setText(QCoreApplication.translate("repository", u"Watch", None))
        self.forkButton.setText(QCoreApplication.translate("repository", u"Fork", None))
        self.starButton.setText(QCoreApplication.translate("repository", u"Star", None))
        self.codeButton.setText(QCoreApplication.translate("repository", u"Code", None))
        self.profileImageLabel.setText(QCoreApplication.translate("repository", u"img", None))
        self.usernameLabel.setText(QCoreApplication.translate("repository", u"username", None))
        self.commitLabel.setText(QCoreApplication.translate("repository", u"commit desc", None))
        self.numsLabel.setText(QCoreApplication.translate("repository", u"nums", None))
        self.timeLabel.setText(QCoreApplication.translate("repository", u"1 day ago", None))
        self.label.setText(QCoreApplication.translate("repository", u"About", None))
        self.configButton.setText("")
        self.descLabel.setText(QCoreApplication.translate("repository", u"desc", None))
        self.label_2.setText(QCoreApplication.translate("repository", u"Releases", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.code),
                                  QCoreApplication.translate("repository", u"Code", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.issues),
                                  QCoreApplication.translate("repository", u"Issues", None))
    # retranslateUi

