# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'deviceListTemplate.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(567, 348)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.label_device_id = QtWidgets.QLabel(Form)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.label_device_id.sizePolicy().hasHeightForWidth()
        )
        self.label_device_id.setSizePolicy(sizePolicy)
        self.label_device_id.setMinimumSize(QtCore.QSize(0, 35))
        font = QtGui.QFont()
        font.setPointSize(23)
        font.setBold(True)
        font.setWeight(75)
        self.label_device_id.setFont(font)
        self.label_device_id.setStyleSheet("QLabel{background:#68d532;}")
        self.label_device_id.setAlignment(QtCore.Qt.AlignCenter)
        self.label_device_id.setObjectName("label_device_id")
        self.gridLayout.addWidget(self.label_device_id, 0, 0, 1, 1)
        self.widget_scroll_content = QtWidgets.QScrollArea(Form)
        self.widget_scroll_content.setStyleSheet("")
        self.widget_scroll_content.setWidgetResizable(True)
        self.widget_scroll_content.setObjectName("widget_scroll_content")
        self.widget_content = QtWidgets.QWidget()
        self.widget_content.setGeometry(QtCore.QRect(0, 0, 547, 253))
        self.widget_content.setStyleSheet("QWidget#widget_content {background:#fff}")
        self.widget_content.setObjectName("widget_content")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.widget_content)
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3.setSpacing(0)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.widget_scroll_content.setWidget(self.widget_content)
        self.gridLayout.addWidget(self.widget_scroll_content, 3, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.input_command = QtWidgets.QLineEdit(Form)
        self.input_command.setInputMask("")
        self.input_command.setObjectName("input_command")
        self.horizontalLayout.addWidget(self.input_command)
        self.pushButton = QtWidgets.QPushButton(Form)
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/icons/icons/search.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.pushButton.setIcon(icon)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.gridLayout.addLayout(self.horizontalLayout, 2, 0, 1, 1)

        self.retranslateUi(Form)
        self.pushButton.clicked.connect(Form.filter_devices)
        self.input_command.returnPressed.connect(self.pushButton.click)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label_device_id.setText(_translate("Form", "Device list"))
        self.input_command.setPlaceholderText(
            _translate("Form", "Filter devices by name")
        )
        self.pushButton.setText(_translate("Form", "Filter"))


from kamzik3 import resource_kamzik3_rc
