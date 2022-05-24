# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(828, 430)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayoutWidget = QWidget(self.centralwidget)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(19, 29, 794, 375))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(200, 20, QSizePolicy.Maximum, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.enumerate_combobox = QComboBox(self.verticalLayoutWidget)
        self.enumerate_combobox.setObjectName(u"enumerate_combobox")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.enumerate_combobox.sizePolicy().hasHeightForWidth())
        self.enumerate_combobox.setSizePolicy(sizePolicy)
        self.enumerate_combobox.setMinimumSize(QSize(0, 0))

        self.horizontalLayout.addWidget(self.enumerate_combobox)

        self.enumerate_refresh_button = QPushButton(self.verticalLayoutWidget)
        self.enumerate_refresh_button.setObjectName(u"enumerate_refresh_button")
        sizePolicy1 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.enumerate_refresh_button.sizePolicy().hasHeightForWidth())
        self.enumerate_refresh_button.setSizePolicy(sizePolicy1)
        self.enumerate_refresh_button.setMaximumSize(QSize(100, 30))

        self.horizontalLayout.addWidget(self.enumerate_refresh_button)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.line = QFrame(self.verticalLayoutWidget)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.verticalLayout.addWidget(self.line)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.sendpin_button = QPushButton(self.verticalLayoutWidget)
        self.sendpin_button.setObjectName(u"sendpin_button")
        self.sendpin_button.setEnabled(False)

        self.gridLayout.addWidget(self.sendpin_button, 1, 1, 1, 1)

        self.setpass_button = QPushButton(self.verticalLayoutWidget)
        self.setpass_button.setObjectName(u"setpass_button")

        self.gridLayout.addWidget(self.setpass_button, 1, 0, 1, 1)

        self.signtx_button = QPushButton(self.verticalLayoutWidget)
        self.signtx_button.setObjectName(u"signtx_button")
        self.signtx_button.setEnabled(False)

        self.gridLayout.addWidget(self.signtx_button, 2, 1, 1, 1)

        self.getxpub_button = QPushButton(self.verticalLayoutWidget)
        self.getxpub_button.setObjectName(u"getxpub_button")
        self.getxpub_button.setEnabled(False)

        self.gridLayout.addWidget(self.getxpub_button, 2, 0, 1, 1)

        self.signmsg_button = QPushButton(self.verticalLayoutWidget)
        self.signmsg_button.setObjectName(u"signmsg_button")
        self.signmsg_button.setEnabled(False)

        self.gridLayout.addWidget(self.signmsg_button, 2, 2, 1, 1)

        self.actions_label = QLabel(self.verticalLayoutWidget)
        self.actions_label.setObjectName(u"actions_label")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.actions_label.sizePolicy().hasHeightForWidth())
        self.actions_label.setSizePolicy(sizePolicy2)
        self.actions_label.setMaximumSize(QSize(100, 20))

        self.gridLayout.addWidget(self.actions_label, 0, 0, 1, 1)

        self.getkeypool_opts_button = QPushButton(self.verticalLayoutWidget)
        self.getkeypool_opts_button.setObjectName(u"getkeypool_opts_button")
        self.getkeypool_opts_button.setEnabled(False)

        self.gridLayout.addWidget(self.getkeypool_opts_button, 1, 2, 1, 1)

        self.display_addr_button = QPushButton(self.verticalLayoutWidget)
        self.display_addr_button.setObjectName(u"display_addr_button")
        self.display_addr_button.setEnabled(False)

        self.gridLayout.addWidget(self.display_addr_button, 3, 0, 1, 1)

        self.toggle_passphrase_button = QPushButton(self.verticalLayoutWidget)
        self.toggle_passphrase_button.setObjectName(u"toggle_passphrase_button")
        self.toggle_passphrase_button.setEnabled(False)

        self.gridLayout.addWidget(self.toggle_passphrase_button, 3, 1, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.keypool_label = QLabel(self.verticalLayoutWidget)
        self.keypool_label.setObjectName(u"keypool_label")

        self.horizontalLayout_2.addWidget(self.keypool_label)

        self.keypool_textedit = QPlainTextEdit(self.verticalLayoutWidget)
        self.keypool_textedit.setObjectName(u"keypool_textedit")
        self.keypool_textedit.setReadOnly(True)

        self.horizontalLayout_2.addWidget(self.keypool_textedit)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.desc_label = QLabel(self.verticalLayoutWidget)
        self.desc_label.setObjectName(u"desc_label")

        self.horizontalLayout_3.addWidget(self.desc_label)

        self.desc_textedit = QPlainTextEdit(self.verticalLayoutWidget)
        self.desc_textedit.setObjectName(u"desc_textedit")
        self.desc_textedit.setReadOnly(True)

        self.horizontalLayout_3.addWidget(self.desc_textedit)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.enumerate_refresh_button.setText(QCoreApplication.translate("MainWindow", u"Refresh", None))
        self.sendpin_button.setText(QCoreApplication.translate("MainWindow", u"Send Pin", None))
        self.setpass_button.setText(QCoreApplication.translate("MainWindow", u"Set Passphrase", None))
        self.signtx_button.setText(QCoreApplication.translate("MainWindow", u"Sign PSBT", None))
        self.getxpub_button.setText(QCoreApplication.translate("MainWindow", u"Get an xpub", None))
        self.signmsg_button.setText(QCoreApplication.translate("MainWindow", u"Sign Message", None))
        self.actions_label.setText(QCoreApplication.translate("MainWindow", u"Actions:", None))
#if QT_CONFIG(tooltip)
        self.getkeypool_opts_button.setToolTip(QCoreApplication.translate("MainWindow", u"Change the options used for getkeypool", None))
#endif // QT_CONFIG(tooltip)
        self.getkeypool_opts_button.setText(QCoreApplication.translate("MainWindow", u"Change getkeypool options", None))
        self.display_addr_button.setText(QCoreApplication.translate("MainWindow", u"Display Address", None))
        self.toggle_passphrase_button.setText(QCoreApplication.translate("MainWindow", u"Toggle Passphrase", None))
        self.keypool_label.setText(QCoreApplication.translate("MainWindow", u"Keypool:", None))
        self.desc_label.setText(QCoreApplication.translate("MainWindow", u"Descriptors:", None))
    # retranslateUi

