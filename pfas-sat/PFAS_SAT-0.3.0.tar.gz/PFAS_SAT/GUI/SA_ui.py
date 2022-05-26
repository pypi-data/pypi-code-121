# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SA.ui',
# licensing of 'SA.ui' applies.
#
# Created: Mon Aug 31 21:55:18 2020
#      by: pyside2-uic  running on PySide2 5.13.1
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_SA_Plot(object):
    def setupUi(self, SA_Plot):
        SA_Plot.setObjectName("SA_Plot")
        SA_Plot.resize(1510, 1021)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/ICONS/PySWOLF_ICONS/PySWOLF.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        SA_Plot.setWindowIcon(icon)
        self.gridLayout = QtWidgets.QGridLayout(SA_Plot)
        self.gridLayout.setObjectName("gridLayout")
        self.frame = QtWidgets.QFrame(SA_Plot)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.frame)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.groupBox = QtWidgets.QGroupBox(self.frame)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.gridLayout_3.addWidget(self.label, 0, 0, 1, 1)
        self.x_axis = QtWidgets.QComboBox(self.groupBox)
        self.x_axis.setMinimumSize(QtCore.QSize(300, 0))
        self.x_axis.setObjectName("x_axis")
        self.gridLayout_3.addWidget(self.x_axis, 0, 1, 1, 3)
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.gridLayout_3.addWidget(self.label_2, 1, 0, 2, 1)
        self.plot = QtWidgets.QWidget(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plot.sizePolicy().hasHeightForWidth())
        self.plot.setSizePolicy(sizePolicy)
        self.plot.setMinimumSize(QtCore.QSize(0, 100))
        self.plot.setObjectName("plot")
        self.gridLayout_3.addWidget(self.plot, 4, 0, 1, 5)
        self.y_axis = QtWidgets.QComboBox(self.groupBox)
        self.y_axis.setObjectName("y_axis")
        self.gridLayout_3.addWidget(self.y_axis, 1, 1, 1, 3)
        spacerItem = QtWidgets.QSpacerItem(1051, 31, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem, 3, 4, 1, 1)
        self.Update_plot = QtWidgets.QPushButton(self.groupBox)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/ICONS/Update.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.Update_plot.setIcon(icon1)
        self.Update_plot.setObjectName("Update_plot")
        self.gridLayout_3.addWidget(self.Update_plot, 3, 3, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.frame, 0, 0, 1, 1)

        self.retranslateUi(SA_Plot)
        QtCore.QMetaObject.connectSlotsByName(SA_Plot)

    def retranslateUi(self, SA_Plot):
        SA_Plot.setWindowTitle(QtWidgets.QApplication.translate("SA_Plot", "Sensitivity analysis Results", None, -1))
        self.groupBox.setTitle(QtWidgets.QApplication.translate("SA_Plot", "Plot", None, -1))
        self.label.setText(QtWidgets.QApplication.translate("SA_Plot", "X axis", None, -1))
        self.label_2.setText(QtWidgets.QApplication.translate("SA_Plot", "Y axis", None, -1))
        self.Update_plot.setText(QtWidgets.QApplication.translate("SA_Plot", "Update", None, -1))

from . import PFAS_SAT_rc
