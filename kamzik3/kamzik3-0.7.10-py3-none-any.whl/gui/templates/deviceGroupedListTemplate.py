# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'deviceGroupedListTemplate.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(415, 264)
        MainWindow.setStyleSheet("QWidget#centralwidget {background:#dde9ff}")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setStyleSheet("centralwidget {background:#dde9ff}")
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setContentsMargins(6, 6, 6, 6)
        self.gridLayout.setObjectName("gridLayout")
        self.layout_top_controls = QtWidgets.QWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.MinimumExpanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.layout_top_controls.sizePolicy().hasHeightForWidth()
        )
        self.layout_top_controls.setSizePolicy(sizePolicy)
        self.layout_top_controls.setMinimumSize(QtCore.QSize(0, 200))
        self.layout_top_controls.setMaximumSize(QtCore.QSize(16777215, 200))
        self.layout_top_controls.setStyleSheet(
            "QWidget#layout_top_controls {\n"
            "    border-bottom: 2px solid #d1d1d1;\n"
            "    background: #e3e3e3;\n"
            "}"
        )
        self.layout_top_controls.setObjectName("layout_top_controls")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layout_top_controls)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.gridLayout.addWidget(self.layout_top_controls, 0, 0, 1, 1)
        self.tab_device_groups = QtWidgets.QTabWidget(self.centralwidget)
        self.tab_device_groups.setStyleSheet(
            "QTabBar::tab:selected {\n"
            "    font-weight: bold;\n"
            "    color: #003fb4;\n"
            "}"
        )
        self.tab_device_groups.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.tab_device_groups.setObjectName("tab_device_groups")
        self.gridLayout.addWidget(self.tab_device_groups, 1, 0, 1, 1)
        self.layout_bottom_controls = QtWidgets.QHBoxLayout()
        self.layout_bottom_controls.setContentsMargins(0, -1, 0, -1)
        self.layout_bottom_controls.setObjectName("layout_bottom_controls")
        spacerItem = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.layout_bottom_controls.addItem(spacerItem)
        self.button_stop_all_devices = QtWidgets.QPushButton(self.centralwidget)
        self.button_stop_all_devices.setMinimumSize(QtCore.QSize(0, 0))
        self.button_stop_all_devices.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))
        self.button_stop_all_devices.setFocusPolicy(QtCore.Qt.NoFocus)
        self.button_stop_all_devices.setStyleSheet(
            "QPushButton { background-color: #ff4e00 }\\\\nQPushButton:pressed { background-color: #ff4e00 }\\\\nQPushButton:!enabled{background:silver;}QPushButton:checked{background:red;}\\nQPushButton:disabled{ background:silver;color:grey }"
        )
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/icons/icons/stop.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off
        )
        self.button_stop_all_devices.setIcon(icon)
        self.button_stop_all_devices.setIconSize(QtCore.QSize(20, 24))
        self.button_stop_all_devices.setAutoExclusive(False)
        self.button_stop_all_devices.setObjectName("button_stop_all_devices")
        self.layout_bottom_controls.addWidget(self.button_stop_all_devices)
        spacerItem1 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.layout_bottom_controls.addItem(spacerItem1)
        self.button_unlock_controls = QtWidgets.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.button_unlock_controls.setFont(font)
        self.button_unlock_controls.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))
        self.button_unlock_controls.setStyleSheet(
            "QPushButton { background-color: orange }\\\\nQPushButton:pressed { background-color: #ff4e00 }\\\\nQPushButton:!enabled{background:silver;}QPushButton:checked{background:red;}\\nQPushButton:disabled{ background:silver;color:grey }"
        )
        icon1 = QtGui.QIcon()
        icon1.addPixmap(
            QtGui.QPixmap(":/icons/icons/unlock.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.button_unlock_controls.setIcon(icon1)
        self.button_unlock_controls.setIconSize(QtCore.QSize(20, 24))
        self.button_unlock_controls.setObjectName("button_unlock_controls")
        self.layout_bottom_controls.addWidget(self.button_unlock_controls)
        self.button_lock_controls = QtWidgets.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.button_lock_controls.setFont(font)
        self.button_lock_controls.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))
        self.button_lock_controls.setStyleSheet(
            "QPushButton { background-color: orange }\\\\nQPushButton:pressed { background-color: #ff4e00 }\\\\nQPushButton:!enabled{background:silver;}QPushButton:checked{background:red;}\\nQPushButton:disabled{ background:silver;color:grey }"
        )
        icon2 = QtGui.QIcon()
        icon2.addPixmap(
            QtGui.QPixmap(":/icons/icons/lock.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off
        )
        self.button_lock_controls.setIcon(icon2)
        self.button_lock_controls.setIconSize(QtCore.QSize(20, 24))
        self.button_lock_controls.setObjectName("button_lock_controls")
        self.layout_bottom_controls.addWidget(self.button_lock_controls)
        self.gridLayout.addLayout(self.layout_bottom_controls, 2, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.button_lock_controls.clicked.connect(MainWindow.lock_widget)
        self.button_stop_all_devices.clicked.connect(MainWindow.stop_all_devices)
        self.button_unlock_controls.clicked.connect(MainWindow.unlock_widget)
        self.tab_device_groups.currentChanged["int"].connect(MainWindow.tab_changed)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.button_stop_all_devices.setText(
            _translate("MainWindow", " Stop all devices (ESC) ")
        )
        self.button_unlock_controls.setToolTip(
            _translate("MainWindow", "Click to unlock device controls")
        )
        self.button_unlock_controls.setText(
            _translate("MainWindow", "Unlock controls ")
        )
        self.button_lock_controls.setToolTip(
            _translate("MainWindow", "Click to lock device controls")
        )
        self.button_lock_controls.setText(_translate("MainWindow", " Lock controls "))


from kamzik3 import resource_kamzik3_rc
