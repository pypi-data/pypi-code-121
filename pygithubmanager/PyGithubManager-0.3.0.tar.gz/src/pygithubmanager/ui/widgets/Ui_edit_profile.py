# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'edit_profile.ui'
##
## Created by: Qt User Interface Compiler version 6.3.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject)
from PySide6.QtGui import (QFont)
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QLineEdit,
                               QPushButton, QSizePolicy, QSpacerItem, QTextEdit,
                               QVBoxLayout)


class Ui_EditProfile(object):
    def setupUi(self, EditProfile):
        if not EditProfile.objectName():
            EditProfile.setObjectName(u"EditProfile")
        EditProfile.resize(400, 321)
        self.verticalLayout = QVBoxLayout(EditProfile)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(EditProfile)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.label.setFont(font)

        self.verticalLayout.addWidget(self.label)

        self.label_2 = QLabel(EditProfile)
        self.label_2.setObjectName(u"label_2")
        font1 = QFont()
        font1.setBold(True)
        self.label_2.setFont(font1)

        self.verticalLayout.addWidget(self.label_2)

        self.nameLineEdit = QLineEdit(EditProfile)
        self.nameLineEdit.setObjectName(u"nameLineEdit")

        self.verticalLayout.addWidget(self.nameLineEdit)

        self.label_3 = QLabel(EditProfile)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setFont(font1)

        self.verticalLayout.addWidget(self.label_3)

        self.bioTextEdit = QTextEdit(EditProfile)
        self.bioTextEdit.setObjectName(u"bioTextEdit")

        self.verticalLayout.addWidget(self.bioTextEdit)

        self.label_4 = QLabel(EditProfile)
        self.label_4.setObjectName(u"label_4")

        self.verticalLayout.addWidget(self.label_4)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(-1, -1, -1, 0)
        self.companyLabel = QLabel(EditProfile)
        self.companyLabel.setObjectName(u"companyLabel")

        self.horizontalLayout_2.addWidget(self.companyLabel)

        self.companyLineEdit = QLineEdit(EditProfile)
        self.companyLineEdit.setObjectName(u"companyLineEdit")

        self.horizontalLayout_2.addWidget(self.companyLineEdit)

        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(-1, -1, -1, 0)
        self.locationLabel = QLabel(EditProfile)
        self.locationLabel.setObjectName(u"locationLabel")

        self.horizontalLayout_3.addWidget(self.locationLabel)

        self.locationLineEdit = QLineEdit(EditProfile)
        self.locationLineEdit.setObjectName(u"locationLineEdit")

        self.horizontalLayout_3.addWidget(self.locationLineEdit)

        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(-1, -1, -1, 0)
        self.saveButton = QPushButton(EditProfile)
        self.saveButton.setObjectName(u"saveButton")

        self.horizontalLayout_7.addWidget(self.saveButton)

        self.cancelButton = QPushButton(EditProfile)
        self.cancelButton.setObjectName(u"cancelButton")

        self.horizontalLayout_7.addWidget(self.cancelButton)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_7.addItem(self.horizontalSpacer)

        self.verticalLayout.addLayout(self.horizontalLayout_7)

        self.retranslateUi(EditProfile)

        QMetaObject.connectSlotsByName(EditProfile)

    # setupUi

    def retranslateUi(self, EditProfile):
        EditProfile.setWindowTitle(QCoreApplication.translate("EditProfile", u"Form", None))
        self.label.setText(QCoreApplication.translate("EditProfile", u"Edit profile", None))
        self.label_2.setText(QCoreApplication.translate("EditProfile", u"Name", None))
        self.nameLineEdit.setPlaceholderText(QCoreApplication.translate("EditProfile", u"Name", None))
        self.label_3.setText(QCoreApplication.translate("EditProfile", u"Bio", None))
        self.bioTextEdit.setPlaceholderText(QCoreApplication.translate("EditProfile", u"Add a bio", None))
        self.label_4.setText(QCoreApplication.translate("EditProfile",
                                                        u"You can @mention other users and organizations to link to them.",
                                                        None))
        self.companyLabel.setText("")
        self.companyLineEdit.setPlaceholderText(QCoreApplication.translate("EditProfile", u"Company", None))
        self.locationLabel.setText("")
        self.locationLineEdit.setPlaceholderText(QCoreApplication.translate("EditProfile", u"Location", None))
        self.saveButton.setText(QCoreApplication.translate("EditProfile", u"Save", None))
        self.cancelButton.setText(QCoreApplication.translate("EditProfile", u"Cancel", None))
    # retranslateUi
