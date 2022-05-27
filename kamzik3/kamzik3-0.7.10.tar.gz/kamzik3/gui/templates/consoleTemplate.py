# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'consoleTemplate.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1009, 492)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.input_console_text = QtWidgets.QTextEdit(Form)
        self.input_console_text.setReadOnly(True)
        self.input_console_text.setObjectName("input_console_text")
        self.gridLayout.addWidget(self.input_console_text, 3, 0, 1, 1)
        self.label_console_header = QtWidgets.QLabel(Form)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.label_console_header.sizePolicy().hasHeightForWidth()
        )
        self.label_console_header.setSizePolicy(sizePolicy)
        self.label_console_header.setStyleSheet(
            "font-weight:bold;background:#f6b442;padding:5"
        )
        self.label_console_header.setObjectName("label_console_header")
        self.gridLayout.addWidget(self.label_console_header, 0, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_messages_count = QtWidgets.QLabel(Form)
        self.label_messages_count.setObjectName("label_messages_count")
        self.horizontalLayout.addWidget(self.label_messages_count)
        self.input_messages_count = QtWidgets.QSpinBox(Form)
        self.input_messages_count.setReadOnly(True)
        self.input_messages_count.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.input_messages_count.setMaximum(2099999999)
        self.input_messages_count.setObjectName("input_messages_count")
        self.horizontalLayout.addWidget(self.input_messages_count)
        self.label_errors_count = QtWidgets.QLabel(Form)
        self.label_errors_count.setObjectName("label_errors_count")
        self.horizontalLayout.addWidget(self.label_errors_count)
        self.input_errors_count = QtWidgets.QSpinBox(Form)
        self.input_errors_count.setReadOnly(True)
        self.input_errors_count.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.input_errors_count.setMaximum(2099999999)
        self.input_errors_count.setObjectName("input_errors_count")
        self.horizontalLayout.addWidget(self.input_errors_count)
        self.button_pause_output = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.button_pause_output.sizePolicy().hasHeightForWidth()
        )
        self.button_pause_output.setSizePolicy(sizePolicy)
        self.button_pause_output.setMinimumSize(QtCore.QSize(0, 0))
        self.button_pause_output.setMaximumSize(QtCore.QSize(16777215, 16777215))
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/icons/icons/pause.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.button_pause_output.setIcon(icon)
        self.button_pause_output.setIconSize(QtCore.QSize(16, 16))
        self.button_pause_output.setObjectName("button_pause_output")
        self.horizontalLayout.addWidget(self.button_pause_output)
        self.button_resume_output = QtWidgets.QPushButton(Form)
        self.button_resume_output.setEnabled(False)
        self.button_resume_output.setMaximumSize(QtCore.QSize(16777215, 16777215))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(
            QtGui.QPixmap(":/icons/icons/play.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off
        )
        self.button_resume_output.setIcon(icon1)
        self.button_resume_output.setIconSize(QtCore.QSize(16, 16))
        self.button_resume_output.setObjectName("button_resume_output")
        self.horizontalLayout.addWidget(self.button_resume_output)
        spacerItem = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.horizontalLayout.addItem(spacerItem)
        self.button_clear_console = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.button_clear_console.sizePolicy().hasHeightForWidth()
        )
        self.button_clear_console.setSizePolicy(sizePolicy)
        self.button_clear_console.setMinimumSize(QtCore.QSize(0, 0))
        self.button_clear_console.setMaximumSize(QtCore.QSize(16777215, 16777215))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(
            QtGui.QPixmap(":/icons/icons/cancel.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.button_clear_console.setIcon(icon2)
        self.button_clear_console.setIconSize(QtCore.QSize(16, 16))
        self.button_clear_console.setObjectName("button_clear_console")
        self.horizontalLayout.addWidget(self.button_clear_console)
        self.button_scroll_down = QtWidgets.QPushButton(Form)
        self.button_scroll_down.setMaximumSize(QtCore.QSize(16777215, 16777215))
        icon3 = QtGui.QIcon()
        icon3.addPixmap(
            QtGui.QPixmap(":/icons/icons/plus_double.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.button_scroll_down.setIcon(icon3)
        self.button_scroll_down.setIconSize(QtCore.QSize(16, 16))
        self.button_scroll_down.setObjectName("button_scroll_down")
        self.horizontalLayout.addWidget(self.button_scroll_down)
        self.button_scroll_down_2 = QtWidgets.QPushButton(Form)
        self.button_scroll_down_2.setMaximumSize(QtCore.QSize(16777215, 16777215))
        icon4 = QtGui.QIcon()
        icon4.addPixmap(
            QtGui.QPixmap(":/icons/icons/minus_double.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.button_scroll_down_2.setIcon(icon4)
        self.button_scroll_down_2.setIconSize(QtCore.QSize(16, 16))
        self.button_scroll_down_2.setObjectName("button_scroll_down_2")
        self.horizontalLayout.addWidget(self.button_scroll_down_2)
        self.gridLayout.addLayout(self.horizontalLayout, 4, 0, 1, 1)

        self.retranslateUi(Form)
        self.button_clear_console.clicked.connect(Form.clear_all)
        self.button_pause_output.clicked.connect(Form.pause_output)
        self.button_resume_output.clicked.connect(Form.resume_output)
        self.button_scroll_down_2.clicked.connect(Form.scroll_down)
        self.button_scroll_down.clicked.connect(Form.scroll_up)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label_console_header.setText(_translate("Form", "Standard output"))
        self.label_messages_count.setText(_translate("Form", "Messages:"))
        self.label_errors_count.setText(_translate("Form", "Errors:"))
        self.button_pause_output.setToolTip(_translate("Form", "Clear console output"))
        self.button_pause_output.setText(_translate("Form", " Pause output"))
        self.button_resume_output.setText(_translate("Form", " Resume output"))
        self.button_clear_console.setToolTip(_translate("Form", "Clear console output"))
        self.button_clear_console.setText(_translate("Form", " Clear all"))
        self.button_scroll_down.setText(_translate("Form", "Up"))
        self.button_scroll_down_2.setText(_translate("Form", "Down"))


from kamzik3 import resource_kamzik3_rc
