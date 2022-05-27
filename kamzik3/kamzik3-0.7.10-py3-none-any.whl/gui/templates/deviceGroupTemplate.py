# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'deviceGroupTemplate.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(367, 212)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setContentsMargins(2, 0, 0, 0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.frame_label_area = QtWidgets.QFrame(Form)
        self.frame_label_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_label_area.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_label_area.setLineWidth(0)
        self.frame_label_area.setObjectName("frame_label_area")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame_label_area)
        self.horizontalLayout_2.setContentsMargins(2, 2, 2, 2)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.button_group_name = QtWidgets.QPushButton(self.frame_label_area)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.button_group_name.sizePolicy().hasHeightForWidth()
        )
        self.button_group_name.setSizePolicy(sizePolicy)
        self.button_group_name.setMaximumSize(QtCore.QSize(16777215, 21))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.button_group_name.setFont(font)
        self.button_group_name.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.button_group_name.setStyleSheet(
            "QPushButton {\n" "background:transparent;\n" "}"
        )
        self.button_group_name.setFlat(True)
        self.button_group_name.setObjectName("button_group_name")
        self.horizontalLayout_2.addWidget(self.button_group_name)
        self.button_toggle_attach = QtWidgets.QPushButton(self.frame_label_area)
        self.button_toggle_attach.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.button_toggle_attach.setStyleSheet(
            "QPushButton { background-color: transpare;padding:0;border:0;background-color:transparent }\n"
            "QPushButton:pressed { background-color: transparent }"
        )
        self.button_toggle_attach.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/icons/icons/detach.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.button_toggle_attach.setIcon(icon)
        self.button_toggle_attach.setIconSize(QtCore.QSize(20, 20))
        self.button_toggle_attach.setCheckable(False)
        self.button_toggle_attach.setChecked(False)
        self.button_toggle_attach.setAutoExclusive(True)
        self.button_toggle_attach.setObjectName("button_toggle_attach")
        self.horizontalLayout_2.addWidget(self.button_toggle_attach)
        self.horizontalLayout.addWidget(self.frame_label_area)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.button_device_group = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.button_device_group.sizePolicy().hasHeightForWidth()
        )
        self.button_device_group.setSizePolicy(sizePolicy)
        self.button_device_group.setMinimumSize(QtCore.QSize(50, 50))
        self.button_device_group.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.button_device_group.setFocusPolicy(QtCore.Qt.NoFocus)
        self.button_device_group.setAutoFillBackground(False)
        self.button_device_group.setStyleSheet(
            "QPushButton#button_device_group {{border:2px solid transparent; border-bottom:0px; border-left:2px solid transparent; border-right:2px solid transparent; background-color:transparent; margin:0px; padding:5px}} :checked {background-color: transparent} :pressed {border:0;background-color: transparent}"
        )
        self.button_device_group.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(
            QtGui.QPixmap(":/icons/icons/deviceExample.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.button_device_group.setIcon(icon1)
        self.button_device_group.setIconSize(QtCore.QSize(0, 0))
        self.button_device_group.setCheckable(True)
        self.button_device_group.setAutoDefault(False)
        self.button_device_group.setDefault(False)
        self.button_device_group.setFlat(True)
        self.button_device_group.setObjectName("button_device_group")
        self.gridLayout.addWidget(self.button_device_group, 2, 0, 1, 1)

        self.retranslateUi(Form)
        self.button_toggle_attach.clicked.connect(Form.toggle_attach)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.button_group_name.setText(_translate("Form", "Stages"))
        self.button_toggle_attach.setToolTip(
            _translate("Form", "Detach / attach group")
        )


from kamzik3 import resource_kamzik3_rc
