# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'sessionWindowTemplate.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(166, 76)
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/icons/icons/kamzik.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.label_header = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_header.sizePolicy().hasHeightForWidth())
        self.label_header.setSizePolicy(sizePolicy)
        self.label_header.setStyleSheet("font-weight:bold;background:#f6b442;padding:5")
        self.label_header.setObjectName("label_header")
        self.gridLayout.addWidget(self.label_header, 0, 0, 1, 1)
        self.layout_tool_buttons = QtWidgets.QGridLayout()
        self.layout_tool_buttons.setObjectName("layout_tool_buttons")
        self.gridLayout.addLayout(self.layout_tool_buttons, 1, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
        )
        self.gridLayout.addItem(spacerItem, 2, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 166, 21))
        self.menubar.setObjectName("menubar")
        self.menuApplication = QtWidgets.QMenu(self.menubar)
        self.menuApplication.setObjectName("menuApplication")
        MainWindow.setMenuBar(self.menubar)
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.menuApplication.addAction(self.actionExit)
        self.menubar.addAction(self.menuApplication.menuAction())

        self.retranslateUi(MainWindow)
        self.actionExit.triggered.connect(MainWindow.close)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label_header.setText(_translate("MainWindow", "Session tools"))
        self.menuApplication.setTitle(_translate("MainWindow", "Application"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))


from kamzik3 import resource_kamzik3_rc
