# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'clone.ui'
##
## Created by: Qt User Interface Compiler version 6.3.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject)
from PySide6.QtGui import (QFont)
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QLineEdit,
                               QPushButton, QSizePolicy, QTabWidget, QVBoxLayout,
                               QWidget)

from widgets.IconLabel import IconLabel


class Ui_Clone(object):
    def setupUi(self, Clone):
        if not Clone.objectName():
            Clone.setObjectName(u"Clone")
        Clone.resize(441, 162)
        self.verticalLayout = QVBoxLayout(Clone)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.cloneWidget = IconLabel(Clone)
        self.cloneWidget.setObjectName(u"cloneWidget")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cloneWidget.sizePolicy().hasHeightForWidth())
        self.cloneWidget.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.cloneWidget)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.tabWidget = QTabWidget(Clone)
        self.tabWidget.setObjectName(u"tabWidget")
        self.https = QWidget()
        self.https.setObjectName(u"https")
        self.horizontalLayout_3 = QHBoxLayout(self.https)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.httpsUrlLineEdit = QLineEdit(self.https)
        self.httpsUrlLineEdit.setObjectName(u"httpsUrlLineEdit")

        self.horizontalLayout_3.addWidget(self.httpsUrlLineEdit)

        self.httpsCopyButton = QPushButton(self.https)
        self.httpsCopyButton.setObjectName(u"httpsCopyButton")
        sizePolicy.setHeightForWidth(self.httpsCopyButton.sizePolicy().hasHeightForWidth())
        self.httpsCopyButton.setSizePolicy(sizePolicy)

        self.horizontalLayout_3.addWidget(self.httpsCopyButton)

        self.tabWidget.addTab(self.https, "")
        self.ssh = QWidget()
        self.ssh.setObjectName(u"ssh")
        self.horizontalLayout_2 = QHBoxLayout(self.ssh)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.sshUrlLineEdit = QLineEdit(self.ssh)
        self.sshUrlLineEdit.setObjectName(u"sshUrlLineEdit")
        self.sshUrlLineEdit.setReadOnly(True)

        self.horizontalLayout_2.addWidget(self.sshUrlLineEdit)

        self.sshCopyButton = QPushButton(self.ssh)
        self.sshCopyButton.setObjectName(u"sshCopyButton")
        sizePolicy.setHeightForWidth(self.sshCopyButton.sizePolicy().hasHeightForWidth())
        self.sshCopyButton.setSizePolicy(sizePolicy)

        self.horizontalLayout_2.addWidget(self.sshCopyButton)

        self.tabWidget.addTab(self.ssh, "")
        self.cloneTab = QWidget()
        self.cloneTab.setObjectName(u"cloneTab")
        self.verticalLayout_2 = QVBoxLayout(self.cloneTab)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.savePathLabel = QLabel(self.cloneTab)
        self.savePathLabel.setObjectName(u"savePathLabel")
        font = QFont()
        font.setBold(True)
        self.savePathLabel.setFont(font)

        self.verticalLayout_2.addWidget(self.savePathLabel)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.repoSavePathLineEdit = QLineEdit(self.cloneTab)
        self.repoSavePathLineEdit.setObjectName(u"repoSavePathLineEdit")

        self.horizontalLayout_4.addWidget(self.repoSavePathLineEdit)

        self.selectDirectoryButton = QPushButton(self.cloneTab)
        self.selectDirectoryButton.setObjectName(u"selectDirectoryButton")

        self.horizontalLayout_4.addWidget(self.selectDirectoryButton)

        self.verticalLayout_2.addLayout(self.horizontalLayout_4)

        self.cloneButton = QPushButton(self.cloneTab)
        self.cloneButton.setObjectName(u"cloneButton")
        sizePolicy.setHeightForWidth(self.cloneButton.sizePolicy().hasHeightForWidth())
        self.cloneButton.setSizePolicy(sizePolicy)

        self.verticalLayout_2.addWidget(self.cloneButton)

        self.tabWidget.addTab(self.cloneTab, "")

        self.horizontalLayout.addWidget(self.tabWidget)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(Clone)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Clone)
    # setupUi

    def retranslateUi(self, Clone):
        Clone.setWindowTitle(QCoreApplication.translate("Clone", u"Form", None))
        self.httpsCopyButton.setText("")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.https),
                                  QCoreApplication.translate("Clone", u"HTTPS", None))
        self.sshCopyButton.setText("")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.ssh), QCoreApplication.translate("Clone", u"SSH", None))
        self.savePathLabel.setText(QCoreApplication.translate("Clone", u"Save path:", None))
        # if QT_CONFIG(tooltip)
        self.repoSavePathLineEdit.setToolTip(QCoreApplication.translate("Clone",
                                                                        u"<html><head/><body><p>Path where the repository will be saved.</p><p>Ex: C:\\Users\\User</p><p>Cloning automatically creates a folder with the name of the repository.</p></body></html>",
                                                                        None))
        # endif // QT_CONFIG(tooltip)
        self.selectDirectoryButton.setText(QCoreApplication.translate("Clone", u"Select directory", None))
        self.cloneButton.setText(QCoreApplication.translate("Clone", u"Clone", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.cloneTab),
                                  QCoreApplication.translate("Clone", u"CLONE", None))
    # retranslateUi

