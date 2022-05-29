# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'issue_template.ui'
##
## Created by: Qt User Interface Compiler version 6.3.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject)
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QSizePolicy,
                               QSpacerItem, QVBoxLayout)

from widgets.IconLabel import IconLabel


class Ui_IssueTemplate(object):
    def setupUi(self, IssueTemplate):
        if not IssueTemplate.objectName():
            IssueTemplate.setObjectName(u"IssueTemplate")
        IssueTemplate.resize(706, 87)
        self.verticalLayout = QVBoxLayout(IssueTemplate)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.statusNameWidget = IconLabel(IssueTemplate)
        self.statusNameWidget.setObjectName(u"statusNameWidget")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.statusNameWidget.sizePolicy().hasHeightForWidth())
        self.statusNameWidget.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.statusNameWidget)

        self.labelsLayout = QHBoxLayout()
        self.labelsLayout.setObjectName(u"labelsLayout")

        self.horizontalLayout.addLayout(self.labelsLayout)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.commentsWidget = IconLabel(IssueTemplate)
        self.commentsWidget.setObjectName(u"commentsWidget")
        sizePolicy.setHeightForWidth(self.commentsWidget.sizePolicy().hasHeightForWidth())
        self.commentsWidget.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.commentsWidget)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.issueNumberLabel = QLabel(IssueTemplate)
        self.issueNumberLabel.setObjectName(u"issueNumberLabel")

        self.horizontalLayout_2.addWidget(self.issueNumberLabel)

        self.openedLabel = QLabel(IssueTemplate)
        self.openedLabel.setObjectName(u"openedLabel")

        self.horizontalLayout_2.addWidget(self.openedLabel)

        self.byLabel = QLabel(IssueTemplate)
        self.byLabel.setObjectName(u"byLabel")

        self.horizontalLayout_2.addWidget(self.byLabel)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(IssueTemplate)

        QMetaObject.connectSlotsByName(IssueTemplate)

    # setupUi

    def retranslateUi(self, IssueTemplate):
        IssueTemplate.setWindowTitle(QCoreApplication.translate("IssueTemplate", u"Form", None))
        self.issueNumberLabel.setText(QCoreApplication.translate("IssueTemplate", u"#Issue", None))
        self.openedLabel.setText(QCoreApplication.translate("IssueTemplate", u"opened", None))
        self.byLabel.setText(QCoreApplication.translate("IssueTemplate", u"by", None))
    # retranslateUi
