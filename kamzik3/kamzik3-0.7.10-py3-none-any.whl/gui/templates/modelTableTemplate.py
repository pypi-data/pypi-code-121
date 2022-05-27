# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'modelTableTemplate.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(264, 326)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.input_table_view = QtWidgets.QTableView(Form)
        self.input_table_view.setAlternatingRowColors(True)
        self.input_table_view.setSelectionMode(
            QtWidgets.QAbstractItemView.SingleSelection
        )
        self.input_table_view.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectItems
        )
        self.input_table_view.setGridStyle(QtCore.Qt.SolidLine)
        self.input_table_view.setObjectName("input_table_view")
        self.input_table_view.horizontalHeader().setCascadingSectionResizes(True)
        self.input_table_view.horizontalHeader().setSortIndicatorShown(False)
        self.input_table_view.horizontalHeader().setStretchLastSection(True)
        self.input_table_view.verticalHeader().setCascadingSectionResizes(False)
        self.gridLayout.addWidget(self.input_table_view, 0, 0, 1, 1)
        self.layout_controls = QtWidgets.QVBoxLayout()
        self.layout_controls.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.layout_controls.setObjectName("layout_controls")
        self.button_copy_item = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.button_copy_item.sizePolicy().hasHeightForWidth()
        )
        self.button_copy_item.setSizePolicy(sizePolicy)
        self.button_copy_item.setMinimumSize(QtCore.QSize(32, 32))
        self.button_copy_item.setMaximumSize(QtCore.QSize(32, 32))
        self.button_copy_item.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/icons/icons/copy.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off
        )
        self.button_copy_item.setIcon(icon)
        self.button_copy_item.setIconSize(QtCore.QSize(25, 25))
        self.button_copy_item.setCheckable(False)
        self.button_copy_item.setObjectName("button_copy_item")
        self.layout_controls.addWidget(self.button_copy_item)
        spacerItem = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
        )
        self.layout_controls.addItem(spacerItem)
        self.button_move_item_top = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.button_move_item_top.sizePolicy().hasHeightForWidth()
        )
        self.button_move_item_top.setSizePolicy(sizePolicy)
        self.button_move_item_top.setMinimumSize(QtCore.QSize(32, 32))
        self.button_move_item_top.setMaximumSize(QtCore.QSize(32, 32))
        self.button_move_item_top.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(
            QtGui.QPixmap(":/icons/icons/top.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off
        )
        self.button_move_item_top.setIcon(icon1)
        self.button_move_item_top.setIconSize(QtCore.QSize(25, 25))
        self.button_move_item_top.setObjectName("button_move_item_top")
        self.layout_controls.addWidget(self.button_move_item_top)
        self.button_move_item_up = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.button_move_item_up.sizePolicy().hasHeightForWidth()
        )
        self.button_move_item_up.setSizePolicy(sizePolicy)
        self.button_move_item_up.setMinimumSize(QtCore.QSize(32, 32))
        self.button_move_item_up.setMaximumSize(QtCore.QSize(32, 32))
        self.button_move_item_up.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(
            QtGui.QPixmap(":/icons/icons/plus.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off
        )
        self.button_move_item_up.setIcon(icon2)
        self.button_move_item_up.setIconSize(QtCore.QSize(25, 25))
        self.button_move_item_up.setCheckable(False)
        self.button_move_item_up.setChecked(False)
        self.button_move_item_up.setObjectName("button_move_item_up")
        self.layout_controls.addWidget(self.button_move_item_up)
        spacerItem1 = QtWidgets.QSpacerItem(
            20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed
        )
        self.layout_controls.addItem(spacerItem1)
        self.button_add_item = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.button_add_item.sizePolicy().hasHeightForWidth()
        )
        self.button_add_item.setSizePolicy(sizePolicy)
        self.button_add_item.setMinimumSize(QtCore.QSize(32, 32))
        self.button_add_item.setMaximumSize(QtCore.QSize(32, 32))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.button_add_item.setFont(font)
        self.button_add_item.setStyleSheet("QPushButton {color:green}")
        self.button_add_item.setObjectName("button_add_item")
        self.layout_controls.addWidget(self.button_add_item)
        self.button_remove_item = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.button_remove_item.sizePolicy().hasHeightForWidth()
        )
        self.button_remove_item.setSizePolicy(sizePolicy)
        self.button_remove_item.setMinimumSize(QtCore.QSize(32, 32))
        self.button_remove_item.setMaximumSize(QtCore.QSize(32, 32))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.button_remove_item.setFont(font)
        self.button_remove_item.setStyleSheet("QPushButton {color:red}")
        self.button_remove_item.setObjectName("button_remove_item")
        self.layout_controls.addWidget(self.button_remove_item)
        spacerItem2 = QtWidgets.QSpacerItem(
            20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed
        )
        self.layout_controls.addItem(spacerItem2)
        self.button_move_item_down = QtWidgets.QPushButton(Form)
        self.button_move_item_down.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.button_move_item_down.sizePolicy().hasHeightForWidth()
        )
        self.button_move_item_down.setSizePolicy(sizePolicy)
        self.button_move_item_down.setMinimumSize(QtCore.QSize(32, 32))
        self.button_move_item_down.setMaximumSize(QtCore.QSize(32, 32))
        self.button_move_item_down.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(
            QtGui.QPixmap(":/icons/icons/minus.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.button_move_item_down.setIcon(icon3)
        self.button_move_item_down.setIconSize(QtCore.QSize(25, 25))
        self.button_move_item_down.setObjectName("button_move_item_down")
        self.layout_controls.addWidget(self.button_move_item_down)
        self.button_move_item_bottom = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.button_move_item_bottom.sizePolicy().hasHeightForWidth()
        )
        self.button_move_item_bottom.setSizePolicy(sizePolicy)
        self.button_move_item_bottom.setMinimumSize(QtCore.QSize(32, 32))
        self.button_move_item_bottom.setMaximumSize(QtCore.QSize(32, 32))
        self.button_move_item_bottom.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(
            QtGui.QPixmap(":/icons/icons/bottom.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.button_move_item_bottom.setIcon(icon4)
        self.button_move_item_bottom.setIconSize(QtCore.QSize(25, 25))
        self.button_move_item_bottom.setObjectName("button_move_item_bottom")
        self.layout_controls.addWidget(self.button_move_item_bottom)
        spacerItem3 = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
        )
        self.layout_controls.addItem(spacerItem3)
        self.gridLayout.addLayout(self.layout_controls, 0, 1, 1, 1)

        self.retranslateUi(Form)
        self.button_add_item.clicked.connect(Form.slot_add_item)
        self.button_remove_item.clicked.connect(Form.slot_remove_item)
        self.button_move_item_top.clicked.connect(Form.slot_move_item_top)
        self.button_move_item_up.clicked.connect(Form.slot_move_item_up)
        self.button_move_item_down.clicked.connect(Form.slot_move_item_down)
        self.button_move_item_bottom.clicked.connect(Form.slot_move_item_bottom)
        self.button_copy_item.clicked.connect(Form.slot_copy_item)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.button_copy_item.setToolTip(_translate("Form", "Copy selected rows"))
        self.button_move_item_top.setToolTip(
            _translate("Form", "Move selected row on top")
        )
        self.button_move_item_up.setToolTip(_translate("Form", "Move selected row up"))
        self.button_add_item.setToolTip(_translate("Form", "Add row"))
        self.button_add_item.setText(_translate("Form", "+"))
        self.button_remove_item.setToolTip(_translate("Form", "Remove selected row"))
        self.button_remove_item.setText(_translate("Form", "-"))
        self.button_move_item_down.setToolTip(
            _translate("Form", "Move selected row down")
        )
        self.button_move_item_bottom.setToolTip(
            _translate("Form", "Move selected row to bottom")
        )


from kamzik3 import resource_kamzik3_rc
