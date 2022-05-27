# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'deviceDisplayAttributeTemplate.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(416, 39)
        Form.setStyleSheet("QWidget#widget_holder {background:#fff}")
        self.horizontalLayout = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.widget_holder = QtWidgets.QWidget(Form)
        self.widget_holder.setObjectName("widget_holder")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.widget_holder)
        self.horizontalLayout_2.setContentsMargins(6, 6, 6, 6)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_device_name = QtWidgets.QLabel(self.widget_holder)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.label_device_name.sizePolicy().hasHeightForWidth()
        )
        self.label_device_name.setSizePolicy(sizePolicy)
        self.label_device_name.setMinimumSize(QtCore.QSize(150, 0))
        self.label_device_name.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setFamily("Sans Serif")
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.label_device_name.setFont(font)
        self.label_device_name.setStyleSheet("")
        self.label_device_name.setScaledContents(False)
        self.label_device_name.setObjectName("label_device_name")
        self.horizontalLayout_2.addWidget(self.label_device_name)
        self.label_status = QtWidgets.QLabel(self.widget_holder)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_status.sizePolicy().hasHeightForWidth())
        self.label_status.setSizePolicy(sizePolicy)
        self.label_status.setMinimumSize(QtCore.QSize(100, 0))
        self.label_status.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        font.setKerning(True)
        self.label_status.setFont(font)
        self.label_status.setStyleSheet("QLabel {background:#68d532}")
        self.label_status.setAlignment(QtCore.Qt.AlignCenter)
        self.label_status.setObjectName("label_status")
        self.horizontalLayout_2.addWidget(self.label_status)
        self.input_not_ready_placeholder = QtWidgets.QSpinBox(self.widget_holder)
        self.input_not_ready_placeholder.setEnabled(False)
        self.input_not_ready_placeholder.setReadOnly(True)
        self.input_not_ready_placeholder.setObjectName("input_not_ready_placeholder")
        self.horizontalLayout_2.addWidget(self.input_not_ready_placeholder)
        self.button_debug = QtWidgets.QPushButton(self.widget_holder)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_debug.sizePolicy().hasHeightForWidth())
        self.button_debug.setSizePolicy(sizePolicy)
        self.button_debug.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/icons/icons/settings.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.button_debug.setIcon(icon)
        self.button_debug.setIconSize(QtCore.QSize(19, 19))
        self.button_debug.setObjectName("button_debug")
        self.horizontalLayout_2.addWidget(self.button_debug)
        self.horizontalLayout.addWidget(self.widget_holder)

        self.retranslateUi(Form)
        self.button_debug.clicked.connect(Form.show_debug_widget)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label_device_name.setText(_translate("Form", "ID"))
        self.label_status.setText(_translate("Form", "STATUS"))
        self.input_not_ready_placeholder.setSpecialValueText(
            _translate("Form", "Not ready")
        )
        self.button_debug.setToolTip(_translate("Form", "Settings"))


from kamzik3 import resource_kamzik3_rc
