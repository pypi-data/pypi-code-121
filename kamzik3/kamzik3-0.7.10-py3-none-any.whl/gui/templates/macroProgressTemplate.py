# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'macroProgressTemplate.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(913, 462)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
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
        self.label_status.setStyleSheet("QLabel {background:silver}")
        self.label_status.setAlignment(QtCore.Qt.AlignCenter)
        self.label_status.setObjectName("label_status")
        self.horizontalLayout_2.addWidget(self.label_status)
        self.progress_bar = QtWidgets.QProgressBar(Form)
        self.progress_bar.setProperty("value", 0)
        self.progress_bar.setObjectName("progress_bar")
        self.horizontalLayout_2.addWidget(self.progress_bar)
        self.label = QtWidgets.QLabel(Form)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.label_macro_step_progress = QtWidgets.QLabel(Form)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.label_macro_step_progress.sizePolicy().hasHeightForWidth()
        )
        self.label_macro_step_progress.setSizePolicy(sizePolicy)
        self.label_macro_step_progress.setMinimumSize(QtCore.QSize(70, 0))
        self.label_macro_step_progress.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.label_macro_step_progress.setStyleSheet("QLabel {background:#fff}")
        self.label_macro_step_progress.setAlignment(QtCore.Qt.AlignCenter)
        self.label_macro_step_progress.setObjectName("label_macro_step_progress")
        self.horizontalLayout_2.addWidget(self.label_macro_step_progress)
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.label_running_time = QtWidgets.QLabel(Form)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.label_running_time.sizePolicy().hasHeightForWidth()
        )
        self.label_running_time.setSizePolicy(sizePolicy)
        self.label_running_time.setMinimumSize(QtCore.QSize(70, 0))
        self.label_running_time.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.label_running_time.setStyleSheet("QLabel {background:#fff}")
        self.label_running_time.setAlignment(QtCore.Qt.AlignCenter)
        self.label_running_time.setObjectName("label_running_time")
        self.horizontalLayout_2.addWidget(self.label_running_time)
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_2.addWidget(self.label_3)
        self.label_remaining_time = QtWidgets.QLabel(Form)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.label_remaining_time.sizePolicy().hasHeightForWidth()
        )
        self.label_remaining_time.setSizePolicy(sizePolicy)
        self.label_remaining_time.setMinimumSize(QtCore.QSize(70, 0))
        self.label_remaining_time.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.label_remaining_time.setStyleSheet("QLabel {background:#fff}")
        self.label_remaining_time.setAlignment(QtCore.Qt.AlignCenter)
        self.label_remaining_time.setObjectName("label_remaining_time")
        self.horizontalLayout_2.addWidget(self.label_remaining_time)
        spacerItem = QtWidgets.QSpacerItem(
            0, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.horizontalLayout_2.addItem(spacerItem)
        self.label_4 = QtWidgets.QLabel(Form)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_2.addWidget(self.label_4)
        self.label_estimated_finish = QtWidgets.QLabel(Form)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.label_estimated_finish.sizePolicy().hasHeightForWidth()
        )
        self.label_estimated_finish.setSizePolicy(sizePolicy)
        self.label_estimated_finish.setMinimumSize(QtCore.QSize(70, 0))
        self.label_estimated_finish.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.label_estimated_finish.setStyleSheet("QLabel {background:#fff}")
        self.label_estimated_finish.setAlignment(QtCore.Qt.AlignCenter)
        self.label_estimated_finish.setObjectName("label_estimated_finish")
        self.horizontalLayout_2.addWidget(self.label_estimated_finish)
        self.button_stop = QtWidgets.QPushButton(Form)
        self.button_stop.setStyleSheet(
            "QPushButton { background-color: #ff4e00 }\\\\nQPushButton:pressed { background-color: #ff4e00 }\\\\nQPushButton:!enabled{background:silver;}QPushButton:checked{background:red;}\\nQPushButton:disabled{ background:silver;color:grey }"
        )
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/icons/icons/stop.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off
        )
        self.button_stop.setIcon(icon)
        self.button_stop.setIconSize(QtCore.QSize(16, 16))
        self.button_stop.setObjectName("button_stop")
        self.horizontalLayout_2.addWidget(self.button_stop)
        self.button_start = QtWidgets.QPushButton(Form)
        self.button_start.setStyleSheet(
            "QPushButton { background-color: #68d532 }\n"
            "QPushButton:pressed { background-color: #28a900 }\n"
            "QPushButton:!enabled{background:silver;}QPushButton:checked{background:red;}\n"
            "QPushButton:disabled{ background:silver;color:grey }"
        )
        icon1 = QtGui.QIcon()
        icon1.addPixmap(
            QtGui.QPixmap(":/icons/icons/play.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off
        )
        self.button_start.setIcon(icon1)
        self.button_start.setIconSize(QtCore.QSize(16, 16))
        self.button_start.setObjectName("button_start")
        self.horizontalLayout_2.addWidget(self.button_start)
        self.gridLayout.addLayout(self.horizontalLayout_2, 2, 0, 1, 1)
        self.scroll_area_plot = QtWidgets.QScrollArea(Form)
        self.scroll_area_plot.setWidgetResizable(True)
        self.scroll_area_plot.setObjectName("scroll_area_plot")
        self.plot_widget = QtWidgets.QWidget()
        self.plot_widget.setGeometry(QtCore.QRect(0, 0, 911, 426))
        self.plot_widget.setObjectName("plot_widget")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.plot_widget)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.scroll_area_plot.setWidget(self.plot_widget)
        self.gridLayout.addWidget(self.scroll_area_plot, 1, 0, 1, 1)

        self.retranslateUi(Form)
        self.button_stop.clicked.connect(Form.stop)
        self.button_start.clicked.connect(Form.start)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label_status.setText(_translate("Form", "Disconnected"))
        self.progress_bar.setToolTip(_translate("Form", "Current scan progress"))
        self.label.setText(_translate("Form", "Points:"))
        self.label_macro_step_progress.setToolTip(
            _translate("Form", "Current scan step")
        )
        self.label_macro_step_progress.setText(_translate("Form", "0 / 0"))
        self.label_2.setText(_translate("Form", "Running:"))
        self.label_running_time.setToolTip(
            _translate("Form", "Current scan running time")
        )
        self.label_running_time.setText(_translate("Form", "00:00:00"))
        self.label_3.setText(_translate("Form", "Remaining:"))
        self.label_remaining_time.setToolTip(
            _translate("Form", "Current scan remaining time")
        )
        self.label_remaining_time.setText(_translate("Form", "00:00:00"))
        self.label_4.setText(_translate("Form", "Estimated end:"))
        self.label_estimated_finish.setToolTip(
            _translate("Form", "Current scan estimated finish")
        )
        self.label_estimated_finish.setText(_translate("Form", "00:00:00"))
        self.button_stop.setToolTip(_translate("Form", "Stop current scan"))
        self.button_stop.setText(_translate("Form", "Stop"))
        self.button_start.setToolTip(_translate("Form", "Resume current scan"))
        self.button_start.setText(_translate("Form", "Start"))


from kamzik3 import resource_kamzik3_rc
