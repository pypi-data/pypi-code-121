# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'file_template.ui'
##
## Created by: Qt User Interface Compiler version 6.3.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject, Qt)
from PySide6.QtWidgets import (QHBoxLayout, QLabel)

from widgets.IconLabel import IconLabel


class Ui_FileTemplate(object):
    def setupUi(self, FileTemplate):
        if not FileTemplate.objectName():
            FileTemplate.setObjectName(u"FileTemplate")
        FileTemplate.resize(440, 34)
        self.horizontalLayout = QHBoxLayout(FileTemplate)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.nameWidget = IconLabel(FileTemplate)
        self.nameWidget.setObjectName(u"nameWidget")

        self.horizontalLayout.addWidget(self.nameWidget)

        self.sizeLabel = QLabel(FileTemplate)
        self.sizeLabel.setObjectName(u"sizeLabel")
        self.sizeLabel.setLayoutDirection(Qt.LeftToRight)
        self.sizeLabel.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)

        self.horizontalLayout.addWidget(self.sizeLabel)

        self.retranslateUi(FileTemplate)

        QMetaObject.connectSlotsByName(FileTemplate)
    # setupUi

    def retranslateUi(self, FileTemplate):
        FileTemplate.setWindowTitle(QCoreApplication.translate("FileTemplate", u"Form", None))
        self.sizeLabel.setText(QCoreApplication.translate("FileTemplate", u"size", None))
    # retranslateUi

