# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'deviceNumAttributeTemplate.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(875, 39)
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
        self.button_minus_double = QtWidgets.QPushButton(self.widget_holder)
        self.button_minus_double.setMinimumSize(QtCore.QSize(40, 0))
        self.button_minus_double.setMaximumSize(QtCore.QSize(50, 16777215))
        self.button_minus_double.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/icons/icons/minus_double.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.button_minus_double.setIcon(icon)
        self.button_minus_double.setIconSize(QtCore.QSize(24, 19))
        self.button_minus_double.setObjectName("button_minus_double")
        self.horizontalLayout_2.addWidget(self.button_minus_double)
        self.button_minus = QtWidgets.QPushButton(self.widget_holder)
        self.button_minus.setMinimumSize(QtCore.QSize(40, 0))
        self.button_minus.setMaximumSize(QtCore.QSize(50, 16777215))
        self.button_minus.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(
            QtGui.QPixmap(":/icons/icons/minus.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.button_minus.setIcon(icon1)
        self.button_minus.setIconSize(QtCore.QSize(24, 19))
        self.button_minus.setObjectName("button_minus")
        self.horizontalLayout_2.addWidget(self.button_minus)
        self.input_not_ready_placeholder = QtWidgets.QSpinBox(self.widget_holder)
        self.input_not_ready_placeholder.setEnabled(False)
        self.input_not_ready_placeholder.setReadOnly(True)
        self.input_not_ready_placeholder.setObjectName("input_not_ready_placeholder")
        self.horizontalLayout_2.addWidget(self.input_not_ready_placeholder)
        self.button_plus = QtWidgets.QPushButton(self.widget_holder)
        self.button_plus.setMinimumSize(QtCore.QSize(40, 19))
        self.button_plus.setMaximumSize(QtCore.QSize(50, 16777215))
        self.button_plus.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(
            QtGui.QPixmap(":/icons/icons/plus.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off
        )
        self.button_plus.setIcon(icon2)
        self.button_plus.setIconSize(QtCore.QSize(24, 19))
        self.button_plus.setObjectName("button_plus")
        self.horizontalLayout_2.addWidget(self.button_plus)
        self.button_plus_double = QtWidgets.QPushButton(self.widget_holder)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.button_plus_double.sizePolicy().hasHeightForWidth()
        )
        self.button_plus_double.setSizePolicy(sizePolicy)
        self.button_plus_double.setMinimumSize(QtCore.QSize(40, 19))
        self.button_plus_double.setMaximumSize(QtCore.QSize(50, 16777215))
        self.button_plus_double.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(
            QtGui.QPixmap(":/icons/icons/plus_double.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.button_plus_double.setIcon(icon3)
        self.button_plus_double.setIconSize(QtCore.QSize(24, 19))
        self.button_plus_double.setObjectName("button_plus_double")
        self.horizontalLayout_2.addWidget(self.button_plus_double)
        self.label_step_size = QtWidgets.QLabel(self.widget_holder)
        self.label_step_size.setObjectName("label_step_size")
        self.horizontalLayout_2.addWidget(self.label_step_size)
        self.input_step_size = QtWidgets.QDoubleSpinBox(self.widget_holder)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.input_step_size.sizePolicy().hasHeightForWidth()
        )
        self.input_step_size.setSizePolicy(sizePolicy)
        self.input_step_size.setMinimumSize(QtCore.QSize(70, 0))
        self.input_step_size.setMaximumSize(QtCore.QSize(100, 16777215))
        self.input_step_size.setDecimals(3)
        self.input_step_size.setMinimum(0.0)
        self.input_step_size.setMaximum(9999999.0)
        self.input_step_size.setSingleStep(1.0)
        self.input_step_size.setProperty("value", 1.0)
        self.input_step_size.setObjectName("input_step_size")
        self.horizontalLayout_2.addWidget(self.input_step_size)
        self.button_debug = QtWidgets.QPushButton(self.widget_holder)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_debug.sizePolicy().hasHeightForWidth())
        self.button_debug.setSizePolicy(sizePolicy)
        self.button_debug.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(
            QtGui.QPixmap(":/icons/icons/settings.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.button_debug.setIcon(icon4)
        self.button_debug.setIconSize(QtCore.QSize(19, 19))
        self.button_debug.setObjectName("button_debug")
        self.horizontalLayout_2.addWidget(self.button_debug)
        self.button_stop = QtWidgets.QPushButton(self.widget_holder)
        self.button_stop.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_stop.sizePolicy().hasHeightForWidth())
        self.button_stop.setSizePolicy(sizePolicy)
        self.button_stop.setStyleSheet(
            "QPushButton{background:#c43300;font-weight:bold;color:#000;}\n"
            "QPushButton:disabled{ background:silver;color:grey }\n"
            ""
        )
        self.button_stop.setObjectName("button_stop")
        self.horizontalLayout_2.addWidget(self.button_stop)
        self.horizontalLayout.addWidget(self.widget_holder)

        self.retranslateUi(Form)
        self.button_minus.clicked.connect(Form.decrease_value)
        self.button_minus_double.clicked.connect(Form.decrease_value_double)
        self.button_plus.clicked.connect(Form.increase_value)
        self.button_plus_double.clicked.connect(Form.increase_value_double)
        self.button_stop.clicked.connect(Form.stop)
        self.button_debug.clicked.connect(Form.show_debug_widget)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label_device_name.setText(_translate("Form", "ID"))
        self.label_status.setText(_translate("Form", "STATUS"))
        self.button_minus_double.setToolTip(
            _translate("Form", "Decrease value by (step size * 10)")
        )
        self.button_minus.setToolTip(_translate("Form", "Decrease value by step size"))
        self.input_not_ready_placeholder.setSpecialValueText(
            _translate("Form", "Not ready")
        )
        self.button_plus.setToolTip(_translate("Form", "Increase value by step size"))
        self.button_plus_double.setToolTip(
            _translate("Form", "Increase value by (step size * 10)")
        )
        self.label_step_size.setText(_translate("Form", "Step size:"))
        self.button_debug.setToolTip(_translate("Form", "Settings"))
        self.button_stop.setText(_translate("Form", "STOP"))


from kamzik3 import resource_kamzik3_rc
