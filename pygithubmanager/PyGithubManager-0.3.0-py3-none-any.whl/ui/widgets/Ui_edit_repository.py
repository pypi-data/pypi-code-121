# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'edit_repository.ui'
##
## Created by: Qt User Interface Compiler version 6.3.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject)
from PySide6.QtGui import (QFont)
from PySide6.QtWidgets import (QCheckBox, QComboBox, QFormLayout,
                               QHBoxLayout, QLabel, QLayout, QLineEdit,
                               QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout)

class Ui_RepositoryEdit(object):
    def setupUi(self, RepositoryEdit):
        if not RepositoryEdit.objectName():
            RepositoryEdit.setObjectName(u"RepositoryEdit")
        RepositoryEdit.resize(400, 261)
        self.verticalLayout = QVBoxLayout(RepositoryEdit)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(RepositoryEdit)
        self.label.setObjectName(u"label")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.label.setFont(font)

        self.verticalLayout.addWidget(self.label)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.nameLabel = QLabel(RepositoryEdit)
        self.nameLabel.setObjectName(u"nameLabel")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.nameLabel)

        self.nameLineEdit = QLineEdit(RepositoryEdit)
        self.nameLineEdit.setObjectName(u"nameLineEdit")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.nameLineEdit)

        self.descriptionLabel = QLabel(RepositoryEdit)
        self.descriptionLabel.setObjectName(u"descriptionLabel")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.descriptionLabel)

        self.descriptionLineEdit = QLineEdit(RepositoryEdit)
        self.descriptionLineEdit.setObjectName(u"descriptionLineEdit")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.descriptionLineEdit)

        self.homePageLabel = QLabel(RepositoryEdit)
        self.homePageLabel.setObjectName(u"homePageLabel")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.homePageLabel)

        self.homePageLineEdit = QLineEdit(RepositoryEdit)
        self.homePageLineEdit.setObjectName(u"homePageLineEdit")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.homePageLineEdit)

        self.privateLabel = QLabel(RepositoryEdit)
        self.privateLabel.setObjectName(u"privateLabel")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.privateLabel)

        self.privateCheckBox = QCheckBox(RepositoryEdit)
        self.privateCheckBox.setObjectName(u"privateCheckBox")

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.privateCheckBox)

        self.defaultBranchLabel = QLabel(RepositoryEdit)
        self.defaultBranchLabel.setObjectName(u"defaultBranchLabel")

        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.defaultBranchLabel)

        self.defaultBranchComboBox = QComboBox(RepositoryEdit)
        self.defaultBranchComboBox.setObjectName(u"defaultBranchComboBox")

        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.defaultBranchComboBox)

        self.verticalLayout.addLayout(self.formLayout)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.deleteButton = QPushButton(RepositoryEdit)
        self.deleteButton.setObjectName(u"deleteButton")
        sizePolicy.setHeightForWidth(self.deleteButton.sizePolicy().hasHeightForWidth())
        self.deleteButton.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.deleteButton)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.acceptButton = QPushButton(RepositoryEdit)
        self.acceptButton.setObjectName(u"acceptButton")
        sizePolicy.setHeightForWidth(self.acceptButton.sizePolicy().hasHeightForWidth())
        self.acceptButton.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.acceptButton)

        self.cancelButton = QPushButton(RepositoryEdit)
        self.cancelButton.setObjectName(u"cancelButton")
        sizePolicy.setHeightForWidth(self.cancelButton.sizePolicy().hasHeightForWidth())
        self.cancelButton.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.cancelButton)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(RepositoryEdit)

        QMetaObject.connectSlotsByName(RepositoryEdit)
    # setupUi

    def retranslateUi(self, RepositoryEdit):
        RepositoryEdit.setWindowTitle(QCoreApplication.translate("RepositoryEdit", u"Edit repository", None))
        self.label.setText(QCoreApplication.translate("RepositoryEdit", u"Edit repository", None))
        self.nameLabel.setText(QCoreApplication.translate("RepositoryEdit", u"Name", None))
        self.descriptionLabel.setText(QCoreApplication.translate("RepositoryEdit", u"Description", None))
        self.homePageLabel.setText(QCoreApplication.translate("RepositoryEdit", u"Home Page", None))
        self.privateLabel.setText(QCoreApplication.translate("RepositoryEdit", u"Private", None))
        self.defaultBranchLabel.setText(QCoreApplication.translate("RepositoryEdit", u"Default Branch", None))
        self.deleteButton.setText(QCoreApplication.translate("RepositoryEdit", u"Delete", None))
        self.acceptButton.setText(QCoreApplication.translate("RepositoryEdit", u"Accept", None))
        self.cancelButton.setText(QCoreApplication.translate("RepositoryEdit", u"Cancel", None))
    # retranslateUi

