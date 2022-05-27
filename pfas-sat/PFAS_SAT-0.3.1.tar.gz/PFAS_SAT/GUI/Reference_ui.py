# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Reference.ui',
# licensing of 'Reference.ui' applies.
#
# Created: Fri Sep 18 16:32:01 2020
#      by: pyside2-uic  running on PySide2 5.13.1
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_References(object):
    def setupUi(self, References):
        References.setObjectName("References")
        References.resize(1083, 847)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/ICONS/PFAS_SAT_1.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        References.setWindowIcon(icon)
        self.gridLayout = QtWidgets.QGridLayout(References)
        self.gridLayout.setObjectName("gridLayout")
        self.groupBox = QtWidgets.QGroupBox(References)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.kwrd = QtWidgets.QLineEdit(self.groupBox)
        self.kwrd.setInputMask("")
        self.kwrd.setObjectName("kwrd")
        self.horizontalLayout.addWidget(self.kwrd)
        self.Filter = QtWidgets.QPushButton(self.groupBox)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/ICONS/Filter.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.Filter.setIcon(icon1)
        self.Filter.setObjectName("Filter")
        self.horizontalLayout.addWidget(self.Filter)
        self.Export = QtWidgets.QPushButton(self.groupBox)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icons/ICONS/save.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.Export.setIcon(icon2)
        self.Export.setObjectName("Export")
        self.horizontalLayout.addWidget(self.Export)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.gridLayout_2.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.TableRef = QtWidgets.QTableView(self.groupBox)
        self.TableRef.setObjectName("TableRef")
        self.gridLayout_2.addWidget(self.TableRef, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 1)

        self.retranslateUi(References)
        QtCore.QMetaObject.connectSlotsByName(References)

    def retranslateUi(self, References):
        References.setWindowTitle(QtWidgets.QApplication.translate("References", "PFAS SAT References ", None, -1))
        self.groupBox.setTitle(QtWidgets.QApplication.translate("References", "References", None, -1))
        self.kwrd.setPlaceholderText(QtWidgets.QApplication.translate("References", "Filter", None, -1))
        self.Filter.setText(QtWidgets.QApplication.translate("References", "Filter", None, -1))
        self.Export.setText(QtWidgets.QApplication.translate("References", "Export", None, -1))

from . import PFAS_SAT_rc
