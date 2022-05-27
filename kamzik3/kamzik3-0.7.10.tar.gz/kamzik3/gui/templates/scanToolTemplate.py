# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'scanToolTemplate.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1133, 883)
        self.gridLayout_3 = QtWidgets.QGridLayout(Form)
        self.gridLayout_3.setContentsMargins(6, 6, 6, 6)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.splitter = QtWidgets.QSplitter(Form)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setStyleSheet(
            "QSplitter::handle {image: url(:/icons/icons/splitter.png);}"
        )
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setOpaqueResize(True)
        self.splitter.setHandleWidth(12)
        self.splitter.setChildrenCollapsible(True)
        self.splitter.setObjectName("splitter")
        self.widget_scan_settings = QtWidgets.QWidget(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.widget_scan_settings.sizePolicy().hasHeightForWidth()
        )
        self.widget_scan_settings.setSizePolicy(sizePolicy)
        self.widget_scan_settings.setObjectName("widget_scan_settings")
        self.gridLayout = QtWidgets.QGridLayout(self.widget_scan_settings)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.formLayout_2 = QtWidgets.QFormLayout()
        self.formLayout_2.setFieldGrowthPolicy(
            QtWidgets.QFormLayout.AllNonFixedFieldsGrow
        )
        self.formLayout_2.setLabelAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter
        )
        self.formLayout_2.setObjectName("formLayout_2")
        self.label = QtWidgets.QLabel(self.widget_scan_settings)
        self.label.setObjectName("label")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.combobox_template = QtWidgets.QComboBox(self.widget_scan_settings)
        self.combobox_template.setObjectName("combobox_template")
        self.combobox_template.addItem("")
        self.formLayout_2.setWidget(
            0, QtWidgets.QFormLayout.FieldRole, self.combobox_template
        )
        self.gridLayout.addLayout(self.formLayout_2, 1, 0, 1, 1)
        self.label_scan_settings = QtWidgets.QLabel(self.widget_scan_settings)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.label_scan_settings.sizePolicy().hasHeightForWidth()
        )
        self.label_scan_settings.setSizePolicy(sizePolicy)
        self.label_scan_settings.setStyleSheet(
            "font-weight:bold;background:#f6b442;padding:5"
        )
        self.label_scan_settings.setObjectName("label_scan_settings")
        self.gridLayout.addWidget(self.label_scan_settings, 0, 0, 1, 1)
        self.stackedWidget = QtWidgets.QStackedWidget(self.widget_scan_settings)
        self.stackedWidget.setObjectName("stackedWidget")
        self.page_scan_settings = QtWidgets.QWidget()
        self.page_scan_settings.setObjectName("page_scan_settings")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.page_scan_settings)
        self.gridLayout_4.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.button_start_scan = QtWidgets.QPushButton(self.page_scan_settings)
        self.button_start_scan.setStatusTip("")
        self.button_start_scan.setStyleSheet(
            "QPushButton { background-color: #68d532 }\\nQPushButton:pressed { background-color: #28a900 }\\nQPushButton:!enabled{background:silver;}QPushButton:checked{background:red;}\n"
            "QPushButton:disabled{ background:silver;color:grey }"
        )
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/icons/icons/play.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off
        )
        self.button_start_scan.setIcon(icon)
        self.button_start_scan.setIconSize(QtCore.QSize(16, 16))
        self.button_start_scan.setObjectName("button_start_scan")
        self.horizontalLayout.addWidget(self.button_start_scan)
        spacerItem = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.horizontalLayout.addItem(spacerItem)
        self.button_remove = QtWidgets.QPushButton(self.page_scan_settings)
        self.button_remove.setStyleSheet(
            "QPushButton { background-color: #ff4e00 }\\\\nQPushButton:pressed { background-color: #ff4e00 }\\\\nQPushButton:!enabled{background:silver;}QPushButton:checked{background:red;}\\nQPushButton:disabled{ background:silver;color:grey }"
        )
        icon1 = QtGui.QIcon()
        icon1.addPixmap(
            QtGui.QPixmap(":/icons/icons/remove.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.button_remove.setIcon(icon1)
        self.button_remove.setIconSize(QtCore.QSize(16, 16))
        self.button_remove.setObjectName("button_remove")
        self.horizontalLayout.addWidget(self.button_remove)
        self.gridLayout_4.addLayout(self.horizontalLayout, 3, 0, 1, 1)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(
            QtWidgets.QFormLayout.AllNonFixedFieldsGrow
        )
        self.formLayout.setLabelAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter
        )
        self.formLayout.setObjectName("formLayout")
        self.label_2 = QtWidgets.QLabel(self.page_scan_settings)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.input_comment = QtWidgets.QLineEdit(self.page_scan_settings)
        self.input_comment.setObjectName("input_comment")
        self.formLayout.setWidget(
            1, QtWidgets.QFormLayout.FieldRole, self.input_comment
        )
        self.label_3 = QtWidgets.QLabel(self.page_scan_settings)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.input_output = QtWidgets.QLineEdit(self.page_scan_settings)
        self.input_output.setReadOnly(True)
        self.input_output.setObjectName("input_output")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.input_output)
        self.label_4 = QtWidgets.QLabel(self.page_scan_settings)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.input_repeat_scan = QtWidgets.QDoubleSpinBox(self.page_scan_settings)
        self.input_repeat_scan.setDecimals(0)
        self.input_repeat_scan.setMaximum(2140000000.0)
        self.input_repeat_scan.setObjectName("input_repeat_scan")
        self.formLayout.setWidget(
            3, QtWidgets.QFormLayout.FieldRole, self.input_repeat_scan
        )
        self.gridLayout_4.addLayout(self.formLayout, 1, 0, 1, 1)
        self.scroll_area_scan = QtWidgets.QScrollArea(self.page_scan_settings)
        self.scroll_area_scan.setWidgetResizable(True)
        self.scroll_area_scan.setObjectName("scroll_area_scan")
        self.widget_scan = QtWidgets.QWidget()
        self.widget_scan.setGeometry(QtCore.QRect(0, 0, 98, 28))
        self.widget_scan.setObjectName("widget_scan")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget_scan)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.scroll_area_scan.setWidget(self.widget_scan)
        self.gridLayout_4.addWidget(self.scroll_area_scan, 2, 0, 1, 1)
        self.stackedWidget.addWidget(self.page_scan_settings)
        self.page_template_designer = QtWidgets.QWidget()
        self.page_template_designer.setObjectName("page_template_designer")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.page_template_designer)
        self.gridLayout_5.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.scroll_area_custom_template = QtWidgets.QScrollArea(
            self.page_template_designer
        )
        self.scroll_area_custom_template.setWidgetResizable(True)
        self.scroll_area_custom_template.setObjectName("scroll_area_custom_template")
        self.widget_custom_template = QtWidgets.QWidget()
        self.widget_custom_template.setGeometry(QtCore.QRect(0, 0, 273, 500))
        self.widget_custom_template.setObjectName("widget_custom_template")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.widget_custom_template)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.scroll_area_custom_template.setWidget(self.widget_custom_template)
        self.gridLayout_5.addWidget(self.scroll_area_custom_template, 0, 0, 1, 1)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.button_reset_template = QtWidgets.QPushButton(self.page_template_designer)
        self.button_reset_template.setStatusTip("")
        self.button_reset_template.setStyleSheet(
            "QPushButton { background-color: #ff4e00 }\\\\nQPushButton:pressed { background-color: #ff4e00 }\\\\nQPushButton:!enabled{background:silver;}QPushButton:checked{background:red;}\\nQPushButton:disabled{ background:silver;color:grey }"
        )
        icon2 = QtGui.QIcon()
        icon2.addPixmap(
            QtGui.QPixmap(":/icons/icons/reset_bw.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.button_reset_template.setIcon(icon2)
        self.button_reset_template.setIconSize(QtCore.QSize(16, 16))
        self.button_reset_template.setObjectName("button_reset_template")
        self.horizontalLayout_5.addWidget(self.button_reset_template)
        spacerItem1 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.horizontalLayout_5.addItem(spacerItem1)
        self.button_save_template = QtWidgets.QPushButton(self.page_template_designer)
        self.button_save_template.setStyleSheet(
            "QPushButton { background-color: #00b4ff }\\nQPushButton:pressed { background-color: #28a900 }\\nQPushButton:!enabled{background:silver;}QPushButton:checked{background:red;}\n"
            "QPushButton:disabled{ background:silver;color:grey }"
        )
        icon3 = QtGui.QIcon()
        icon3.addPixmap(
            QtGui.QPixmap(":/icons/icons/save_bw.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.button_save_template.setIcon(icon3)
        self.button_save_template.setIconSize(QtCore.QSize(16, 16))
        self.button_save_template.setObjectName("button_save_template")
        self.horizontalLayout_5.addWidget(self.button_save_template)
        self.button_import_template = QtWidgets.QPushButton(self.page_template_designer)
        self.button_import_template.setStyleSheet(
            "QPushButton { background-color: #00b4ff }\\nQPushButton:pressed { background-color: #28a900 }\\nQPushButton:!enabled{background:silver;}QPushButton:checked{background:red;}\n"
            "QPushButton:disabled{ background:silver;color:grey }"
        )
        icon4 = QtGui.QIcon()
        icon4.addPixmap(
            QtGui.QPixmap(":/icons/icons/load_bw.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.button_import_template.setIcon(icon4)
        self.button_import_template.setIconSize(QtCore.QSize(16, 16))
        self.button_import_template.setObjectName("button_import_template")
        self.horizontalLayout_5.addWidget(self.button_import_template)
        self.gridLayout_5.addLayout(self.horizontalLayout_5, 5, 0, 1, 1)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.button_add_scan_step = QtWidgets.QPushButton(self.page_template_designer)
        self.button_add_scan_step.setStatusTip("")
        self.button_add_scan_step.setStyleSheet(
            "QPushButton { background-color: #68d532 }\\nQPushButton:pressed { background-color: #28a900 }\\nQPushButton:!enabled{background:silver;}QPushButton:checked{background:red;}\n"
            "QPushButton:disabled{ background:silver;color:grey }"
        )
        self.button_add_scan_step.setIconSize(QtCore.QSize(16, 16))
        self.button_add_scan_step.setObjectName("button_add_scan_step")
        self.horizontalLayout_4.addWidget(self.button_add_scan_step)
        self.button_add_step = QtWidgets.QPushButton(self.page_template_designer)
        self.button_add_step.setStatusTip("")
        self.button_add_step.setStyleSheet(
            "QPushButton { background-color: #68d532 }\\nQPushButton:pressed { background-color: #28a900 }\\nQPushButton:!enabled{background:silver;}QPushButton:checked{background:red;}\n"
            "QPushButton:disabled{ background:silver;color:grey }"
        )
        self.button_add_step.setIconSize(QtCore.QSize(16, 16))
        self.button_add_step.setObjectName("button_add_step")
        self.horizontalLayout_4.addWidget(self.button_add_step)
        spacerItem2 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.horizontalLayout_4.addItem(spacerItem2)
        self.gridLayout_5.addLayout(self.horizontalLayout_4, 2, 0, 1, 1)
        self.label_output_log = QtWidgets.QLabel(self.page_template_designer)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.label_output_log.sizePolicy().hasHeightForWidth()
        )
        self.label_output_log.setSizePolicy(sizePolicy)
        self.label_output_log.setStyleSheet(
            "font-weight:bold;background:#f6b442;padding:5"
        )
        self.label_output_log.setObjectName("label_output_log")
        self.gridLayout_5.addWidget(self.label_output_log, 3, 0, 1, 1)
        self.list_measurement_groups = QtWidgets.QListWidget(
            self.page_template_designer
        )
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.list_measurement_groups.sizePolicy().hasHeightForWidth()
        )
        self.list_measurement_groups.setSizePolicy(sizePolicy)
        self.list_measurement_groups.setSelectionMode(
            QtWidgets.QAbstractItemView.MultiSelection
        )
        self.list_measurement_groups.setObjectName("list_measurement_groups")
        self.gridLayout_5.addWidget(self.list_measurement_groups, 4, 0, 1, 1)
        self.stackedWidget.addWidget(self.page_template_designer)
        self.gridLayout.addWidget(self.stackedWidget, 3, 0, 1, 1)
        self.widget_scan_output = QtWidgets.QWidget(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.widget_scan_output.sizePolicy().hasHeightForWidth()
        )
        self.widget_scan_output.setSizePolicy(sizePolicy)
        self.widget_scan_output.setObjectName("widget_scan_output")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.widget_scan_output)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.widget = QtWidgets.QWidget(self.widget_scan_output)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setObjectName("widget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_2.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_status = QtWidgets.QLabel(self.widget)
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
        self.progress_bar_scan = QtWidgets.QProgressBar(self.widget)
        self.progress_bar_scan.setProperty("value", 0)
        self.progress_bar_scan.setObjectName("progress_bar_scan")
        self.horizontalLayout_2.addWidget(self.progress_bar_scan)
        self.label_scan_step = QtWidgets.QLabel(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.label_scan_step.sizePolicy().hasHeightForWidth()
        )
        self.label_scan_step.setSizePolicy(sizePolicy)
        self.label_scan_step.setMinimumSize(QtCore.QSize(70, 0))
        self.label_scan_step.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.label_scan_step.setStyleSheet("QLabel {background:#fff}")
        self.label_scan_step.setAlignment(QtCore.Qt.AlignCenter)
        self.label_scan_step.setObjectName("label_scan_step")
        self.horizontalLayout_2.addWidget(self.label_scan_step)
        self.label_running_time = QtWidgets.QLabel(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred
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
        self.label_remaining_time = QtWidgets.QLabel(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred
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
        spacerItem3 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.horizontalLayout_2.addItem(spacerItem3)
        self.label_estimated_finish = QtWidgets.QLabel(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred
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
        self.button_stop_scan = QtWidgets.QPushButton(self.widget)
        self.button_stop_scan.setStyleSheet(
            "QPushButton { background-color: #ff4e00 }\\\\nQPushButton:pressed { background-color: #ff4e00 }\\\\nQPushButton:!enabled{background:silver;}QPushButton:checked{background:red;}\\nQPushButton:disabled{ background:silver;color:grey }"
        )
        icon5 = QtGui.QIcon()
        icon5.addPixmap(
            QtGui.QPixmap(":/icons/icons/stop.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off
        )
        self.button_stop_scan.setIcon(icon5)
        self.button_stop_scan.setIconSize(QtCore.QSize(16, 16))
        self.button_stop_scan.setObjectName("button_stop_scan")
        self.horizontalLayout_2.addWidget(self.button_stop_scan)
        self.button_resume_scan = QtWidgets.QPushButton(self.widget)
        self.button_resume_scan.setStyleSheet(
            "QPushButton { background-color: #68d532 }\n"
            "QPushButton:pressed { background-color: #28a900 }\n"
            "QPushButton:!enabled{background:silver;}QPushButton:checked{background:red;}\n"
            "QPushButton:disabled{ background:silver;color:grey }"
        )
        icon6 = QtGui.QIcon()
        icon6.addPixmap(
            QtGui.QPixmap(":/icons/icons/resume.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.button_resume_scan.setIcon(icon6)
        self.button_resume_scan.setIconSize(QtCore.QSize(16, 16))
        self.button_resume_scan.setObjectName("button_resume_scan")
        self.horizontalLayout_2.addWidget(self.button_resume_scan)
        self.button_pause_scan = QtWidgets.QPushButton(self.widget)
        self.button_pause_scan.setStyleSheet(
            "QPushButton { background-color: #00b4ff }\\nQPushButton:pressed { background-color: #28a900 }\\nQPushButton:!enabled{background:silver;}QPushButton:checked{background:red;}\n"
            "QPushButton:disabled{ background:silver;color:grey }"
        )
        icon7 = QtGui.QIcon()
        icon7.addPixmap(
            QtGui.QPixmap(":/icons/icons/pause.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.button_pause_scan.setIcon(icon7)
        self.button_pause_scan.setIconSize(QtCore.QSize(16, 16))
        self.button_pause_scan.setObjectName("button_pause_scan")
        self.horizontalLayout_2.addWidget(self.button_pause_scan)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.gridLayout_2.addWidget(self.widget, 4, 0, 1, 1)
        self.label_current_Scan = QtWidgets.QLabel(self.widget_scan_output)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.label_current_Scan.sizePolicy().hasHeightForWidth()
        )
        self.label_current_Scan.setSizePolicy(sizePolicy)
        self.label_current_Scan.setStyleSheet(
            "font-weight:bold;background:#f6b442;padding:5"
        )
        self.label_current_Scan.setObjectName("label_current_Scan")
        self.gridLayout_2.addWidget(self.label_current_Scan, 0, 0, 1, 1)
        self.scroll_area_plot = QtWidgets.QScrollArea(self.widget_scan_output)
        self.scroll_area_plot.setWidgetResizable(True)
        self.scroll_area_plot.setObjectName("scroll_area_plot")
        self.plot_widget = QtWidgets.QWidget()
        self.plot_widget.setGeometry(QtCore.QRect(0, 0, 832, 801))
        self.plot_widget.setObjectName("plot_widget")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.plot_widget)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.scroll_area_plot.setWidget(self.plot_widget)
        self.gridLayout_2.addWidget(self.scroll_area_plot, 1, 0, 1, 1)
        self.gridLayout_3.addWidget(self.splitter, 0, 0, 1, 1)

        self.retranslateUi(Form)
        self.stackedWidget.setCurrentIndex(1)
        self.button_start_scan.clicked.connect(Form.start_scan)
        self.button_pause_scan.clicked.connect(Form.pause_current_scan)
        self.button_resume_scan.clicked.connect(Form.resume_current_scan)
        self.button_add_scan_step.clicked.connect(Form.add_iterative_step)
        self.button_add_step.clicked.connect(Form.add_action_step)
        self.button_reset_template.clicked.connect(Form.reset_template_input)
        self.button_save_template.clicked.connect(Form.export_template)
        self.button_import_template.clicked.connect(Form.import_template)
        self.combobox_template.currentTextChanged["QString"].connect(
            Form.template_selected
        )
        self.button_stop_scan.clicked.connect(Form.stop_current_scan)
        self.button_remove.clicked.connect(Form.remove_template)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Scanning tool"))
        self.label.setText(_translate("Form", "Template:"))
        self.combobox_template.setItemText(0, _translate("Form", "Custom"))
        self.label_scan_settings.setText(_translate("Form", "Scan settings"))
        self.button_start_scan.setToolTip(_translate("Form", "Start scan"))
        self.button_start_scan.setText(_translate("Form", "Start"))
        self.button_remove.setToolTip(_translate("Form", "Remove selected template"))
        self.button_remove.setText(_translate("Form", "Remove"))
        self.label_2.setText(_translate("Form", "Comment:"))
        self.label_3.setText(_translate("Form", "Output file:"))
        self.label_4.setText(_translate("Form", "Repeat:"))
        self.button_reset_template.setToolTip(_translate("Form", "Reset template"))
        self.button_reset_template.setText(_translate("Form", "Reset"))
        self.button_save_template.setToolTip(_translate("Form", "Save template"))
        self.button_save_template.setText(_translate("Form", "Save"))
        self.button_import_template.setToolTip(
            _translate("Form", "Import template from file")
        )
        self.button_import_template.setText(_translate("Form", "Import"))
        self.button_add_scan_step.setToolTip(_translate("Form", "Add iterative step"))
        self.button_add_scan_step.setText(_translate("Form", "+ Iterative step"))
        self.button_add_step.setToolTip(_translate("Form", "Add action step"))
        self.button_add_step.setText(_translate("Form", "+ Action step"))
        self.label_output_log.setText(_translate("Form", "Select measurement group(s)"))
        self.list_measurement_groups.setSortingEnabled(True)
        self.label_status.setText(_translate("Form", "Idle"))
        self.progress_bar_scan.setToolTip(_translate("Form", "Current scan progress"))
        self.label_scan_step.setToolTip(_translate("Form", "Current scan step"))
        self.label_scan_step.setText(_translate("Form", "0 / 0"))
        self.label_running_time.setToolTip(
            _translate("Form", "Current scan running time")
        )
        self.label_running_time.setText(_translate("Form", "00:00:00"))
        self.label_remaining_time.setToolTip(
            _translate("Form", "Current scan remaining time")
        )
        self.label_remaining_time.setText(_translate("Form", "00:00:00"))
        self.label_estimated_finish.setToolTip(
            _translate("Form", "Current scan estimated finish")
        )
        self.label_estimated_finish.setText(_translate("Form", "00:00:00"))
        self.button_stop_scan.setToolTip(_translate("Form", "Stop current scan"))
        self.button_stop_scan.setText(_translate("Form", "Stop"))
        self.button_resume_scan.setToolTip(_translate("Form", "Resume current scan"))
        self.button_resume_scan.setText(_translate("Form", "Resume"))
        self.button_pause_scan.setToolTip(_translate("Form", "Pause current scan"))
        self.button_pause_scan.setText(_translate("Form", "Pause"))
        self.label_current_Scan.setText(_translate("Form", "Current scan"))


from kamzik3 import resource_kamzik3_rc
