# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'loadingOverlayTemplate.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(158, 214)
        Form.setWindowOpacity(1.0)
        Form.setAutoFillBackground(False)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
        )
        self.gridLayout.addItem(spacerItem, 0, 1, 1, 1)
        self.button_cancel = QtWidgets.QPushButton(Form)
        self.button_cancel.setObjectName("button_cancel")
        self.gridLayout.addWidget(self.button_cancel, 3, 1, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
        )
        self.gridLayout.addItem(spacerItem1, 4, 0, 1, 3)
        spacerItem2 = QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.gridLayout.addItem(spacerItem2, 2, 2, 1, 1)
        self.label_loading = QtWidgets.QLabel(Form)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_loading.setFont(font)
        self.label_loading.setAlignment(QtCore.Qt.AlignCenter)
        self.label_loading.setObjectName("label_loading")
        self.gridLayout.addWidget(self.label_loading, 1, 1, 1, 1)
        self.frame = QtWidgets.QFrame(Form)
        self.frame.setMinimumSize(QtCore.QSize(128, 128))
        self.frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame.setLineWidth(0)
        self.frame.setObjectName("frame")
        self.image_loading = QtWidgets.QLabel(self.frame)
        self.image_loading.setGeometry(QtCore.QRect(0, 0, 128, 128))
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.image_loading.sizePolicy().hasHeightForWidth()
        )
        self.image_loading.setSizePolicy(sizePolicy)
        self.image_loading.setMinimumSize(QtCore.QSize(128, 128))
        self.image_loading.setMaximumSize(QtCore.QSize(128, 128))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.image_loading.setFont(font)
        self.image_loading.setLineWidth(0)
        self.image_loading.setText("")
        self.image_loading.setScaledContents(True)
        self.image_loading.setAlignment(QtCore.Qt.AlignCenter)
        self.image_loading.setObjectName("image_loading")
        self.label_progress = QtWidgets.QLabel(self.frame)
        self.label_progress.setGeometry(QtCore.QRect(0, 0, 128, 128))
        font = QtGui.QFont()
        font.setPointSize(15)
        self.label_progress.setFont(font)
        self.label_progress.setLineWidth(0)
        self.label_progress.setText("")
        self.label_progress.setAlignment(QtCore.Qt.AlignCenter)
        self.label_progress.setObjectName("label_progress")
        self.gridLayout.addWidget(self.frame, 2, 1, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.gridLayout.addItem(spacerItem3, 2, 0, 1, 1)

        self.retranslateUi(Form)
        self.button_cancel.clicked.connect(Form.cancel)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.button_cancel.setText(_translate("Form", "Cancel"))
        self.label_loading.setText(_translate("Form", "Loading..."))


from kamzik3 import resource_kamzik3_rc
