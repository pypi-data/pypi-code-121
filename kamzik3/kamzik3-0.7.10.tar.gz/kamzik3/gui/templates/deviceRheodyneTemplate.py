# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'deviceRheodyneTemplate.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(855, 98)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.gridLayout.addItem(spacerItem, 0, 2, 1, 1)
        self.layout_switch_list = QtWidgets.QGridLayout()
        self.layout_switch_list.setObjectName("layout_switch_list")
        self.gridLayout.addLayout(self.layout_switch_list, 1, 0, 1, 4)
        self.label_device_name = QtWidgets.QLabel(Form)
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
        self.gridLayout.addWidget(self.label_device_name, 0, 0, 1, 1)
        self.button_debug = QtWidgets.QPushButton(Form)
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
        self.gridLayout.addWidget(self.button_debug, 0, 3, 1, 1)
        self.label_status = QtWidgets.QLabel(Form)
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
        self.gridLayout.addWidget(self.label_status, 0, 1, 1, 1)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setContentsMargins(-1, -1, 6, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_macro_list = QtWidgets.QLabel(Form)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.label_macro_list.sizePolicy().hasHeightForWidth()
        )
        self.label_macro_list.setSizePolicy(sizePolicy)
        self.label_macro_list.setStyleSheet(
            "font-weight:bold;background:#f6b442;padding:5"
        )
        self.label_macro_list.setObjectName("label_macro_list")
        self.gridLayout_2.addWidget(self.label_macro_list, 0, 0, 1, 1)
        self.layout_macro_grid = QtWidgets.QGridLayout()
        self.layout_macro_grid.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.layout_macro_grid.setObjectName("layout_macro_grid")
        self.gridLayout_2.addLayout(self.layout_macro_grid, 1, 0, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_2, 2, 0, 1, 5)
        spacerItem1 = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
        )
        self.gridLayout.addItem(spacerItem1, 3, 0, 1, 1)

        self.retranslateUi(Form)
        self.button_debug.clicked.connect(Form.show_debug_widget)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label_device_name.setText(_translate("Form", "ID"))
        self.button_debug.setToolTip(_translate("Form", "Settings"))
        self.label_status.setText(_translate("Form", "STATUS"))
        self.label_macro_list.setText(_translate("Form", "Macros"))


from kamzik3 import resource_kamzik3_rc
