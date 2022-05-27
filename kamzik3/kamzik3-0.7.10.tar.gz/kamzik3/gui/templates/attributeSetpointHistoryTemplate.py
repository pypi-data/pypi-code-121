# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'attributeSetpointHistoryTemplate.ui'
#
# Created by: PyQt5 UI code generator 5.13.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(785, 266)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.button_set_value = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.button_set_value.sizePolicy().hasHeightForWidth()
        )
        self.button_set_value.setSizePolicy(sizePolicy)
        self.button_set_value.setMinimumSize(QtCore.QSize(35, 35))
        self.button_set_value.setMaximumSize(QtCore.QSize(40, 40))
        self.button_set_value.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/icons/icons/target.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.button_set_value.setIcon(icon)
        self.button_set_value.setIconSize(QtCore.QSize(25, 25))
        self.button_set_value.setObjectName("button_set_value")
        self.verticalLayout.addWidget(self.button_set_value)
        self.button_refresh = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.button_refresh.sizePolicy().hasHeightForWidth()
        )
        self.button_refresh.setSizePolicy(sizePolicy)
        self.button_refresh.setMinimumSize(QtCore.QSize(35, 35))
        self.button_refresh.setMaximumSize(QtCore.QSize(40, 40))
        self.button_refresh.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(
            QtGui.QPixmap(":/icons/icons/reset_bw.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.button_refresh.setIcon(icon1)
        self.button_refresh.setIconSize(QtCore.QSize(25, 25))
        self.button_refresh.setObjectName("button_refresh")
        self.verticalLayout.addWidget(self.button_refresh)
        spacerItem = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
        )
        self.verticalLayout.addItem(spacerItem)
        self.button_reset = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_reset.sizePolicy().hasHeightForWidth())
        self.button_reset.setSizePolicy(sizePolicy)
        self.button_reset.setMinimumSize(QtCore.QSize(35, 35))
        self.button_reset.setMaximumSize(QtCore.QSize(40, 40))
        self.button_reset.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(
            QtGui.QPixmap(":/icons/icons/cancel.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.button_reset.setIcon(icon2)
        self.button_reset.setIconSize(QtCore.QSize(25, 25))
        self.button_reset.setObjectName("button_reset")
        self.verticalLayout.addWidget(self.button_reset)
        self.gridLayout.addLayout(self.verticalLayout, 0, 1, 1, 1)
        self.table_history_view = QtWidgets.QTableView(Form)
        self.table_history_view.setSelectionMode(
            QtWidgets.QAbstractItemView.SingleSelection
        )
        self.table_history_view.setObjectName("table_history_view")
        self.table_history_view.horizontalHeader().setStretchLastSection(True)
        self.gridLayout.addWidget(self.table_history_view, 0, 0, 1, 1)

        self.retranslateUi(Form)
        self.button_set_value.clicked.connect(Form.set_attribute_value)
        self.button_refresh.clicked.connect(Form.refresh)
        self.button_reset.clicked.connect(Form.reset)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.button_set_value.setToolTip(
            _translate("Form", "Set attribute to saved value")
        )
        self.button_refresh.setToolTip(_translate("Form", "Refresh table of setpoints"))
        self.button_reset.setToolTip(_translate("Form", "Reset all setpoints"))


from kamzik3 import resource_kamzik3_rc
