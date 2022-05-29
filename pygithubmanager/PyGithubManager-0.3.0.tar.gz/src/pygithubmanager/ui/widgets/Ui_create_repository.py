# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'create_repository.ui'
##
## Created by: Qt User Interface Compiler version 6.3.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject, Qt)
from PySide6.QtGui import (QFont)
from PySide6.QtWidgets import (QCheckBox, QFormLayout, QHBoxLayout,
                               QLabel, QLineEdit, QPushButton, QSizePolicy,
                               QVBoxLayout)

from widgets.AutocompletableComboBox import Autocomplete
from widgets.IconLabel import IconLabel


class Ui_CreateRepo(object):
    def setupUi(self, CreateRepo):
        if not CreateRepo.objectName():
            CreateRepo.setObjectName(u"CreateRepo")
        CreateRepo.resize(498, 398)
        self.verticalLayout = QVBoxLayout(CreateRepo)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(CreateRepo)
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
        self.label.setAlignment(Qt.AlignCenter)

        self.horizontalLayout.addWidget(self.label)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.warningLabel = IconLabel(CreateRepo)
        self.warningLabel.setObjectName(u"warningLabel")
        sizePolicy.setHeightForWidth(self.warningLabel.sizePolicy().hasHeightForWidth())
        self.warningLabel.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.warningLabel)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.nameLabel = QLabel(CreateRepo)
        self.nameLabel.setObjectName(u"nameLabel")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.nameLabel)

        self.nameLineEdit = QLineEdit(CreateRepo)
        self.nameLineEdit.setObjectName(u"nameLineEdit")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.nameLineEdit)

        self.descriptionLabel = QLabel(CreateRepo)
        self.descriptionLabel.setObjectName(u"descriptionLabel")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.descriptionLabel)

        self.descriptionLineEdit = QLineEdit(CreateRepo)
        self.descriptionLineEdit.setObjectName(u"descriptionLineEdit")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.descriptionLineEdit)

        self.homepageLabel = QLabel(CreateRepo)
        self.homepageLabel.setObjectName(u"homepageLabel")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.homepageLabel)

        self.homepageLineEdit = QLineEdit(CreateRepo)
        self.homepageLineEdit.setObjectName(u"homepageLineEdit")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.homepageLineEdit)

        self.privateLabel = QLabel(CreateRepo)
        self.privateLabel.setObjectName(u"privateLabel")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.privateLabel)

        self.privateCheckBox = QCheckBox(CreateRepo)
        self.privateCheckBox.setObjectName(u"privateCheckBox")

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.privateCheckBox)

        self.hasIssuesLabel = QLabel(CreateRepo)
        self.hasIssuesLabel.setObjectName(u"hasIssuesLabel")

        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.hasIssuesLabel)

        self.hasIssuesCheckBox = QCheckBox(CreateRepo)
        self.hasIssuesCheckBox.setObjectName(u"hasIssuesCheckBox")

        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.hasIssuesCheckBox)

        self.hasWikiLabel = QLabel(CreateRepo)
        self.hasWikiLabel.setObjectName(u"hasWikiLabel")

        self.formLayout.setWidget(5, QFormLayout.LabelRole, self.hasWikiLabel)

        self.hasWikiCheckBox = QCheckBox(CreateRepo)
        self.hasWikiCheckBox.setObjectName(u"hasWikiCheckBox")

        self.formLayout.setWidget(5, QFormLayout.FieldRole, self.hasWikiCheckBox)

        self.hasDownloadsLabel = QLabel(CreateRepo)
        self.hasDownloadsLabel.setObjectName(u"hasDownloadsLabel")

        self.formLayout.setWidget(6, QFormLayout.LabelRole, self.hasDownloadsLabel)

        self.hasDownloadsCheckBox = QCheckBox(CreateRepo)
        self.hasDownloadsCheckBox.setObjectName(u"hasDownloadsCheckBox")

        self.formLayout.setWidget(6, QFormLayout.FieldRole, self.hasDownloadsCheckBox)

        self.hasProjectsLabel = QLabel(CreateRepo)
        self.hasProjectsLabel.setObjectName(u"hasProjectsLabel")

        self.formLayout.setWidget(7, QFormLayout.LabelRole, self.hasProjectsLabel)

        self.hasProjectsCheckBox = QCheckBox(CreateRepo)
        self.hasProjectsCheckBox.setObjectName(u"hasProjectsCheckBox")

        self.formLayout.setWidget(7, QFormLayout.FieldRole, self.hasProjectsCheckBox)

        self.autoInitLabel = QLabel(CreateRepo)
        self.autoInitLabel.setObjectName(u"autoInitLabel")

        self.formLayout.setWidget(8, QFormLayout.LabelRole, self.autoInitLabel)

        self.autoInitCheckBox = QCheckBox(CreateRepo)
        self.autoInitCheckBox.setObjectName(u"autoInitCheckBox")

        self.formLayout.setWidget(8, QFormLayout.FieldRole, self.autoInitCheckBox)

        self.licenseTemplateLabel = QLabel(CreateRepo)
        self.licenseTemplateLabel.setObjectName(u"licenseTemplateLabel")

        self.formLayout.setWidget(9, QFormLayout.LabelRole, self.licenseTemplateLabel)

        self.licenseTemplateComboBox = Autocomplete(CreateRepo)
        self.licenseTemplateComboBox.setObjectName(u"licenseTemplateComboBox")

        self.formLayout.setWidget(9, QFormLayout.FieldRole, self.licenseTemplateComboBox)

        self.allowRebaseMergeLabel = QLabel(CreateRepo)
        self.allowRebaseMergeLabel.setObjectName(u"allowRebaseMergeLabel")

        self.formLayout.setWidget(10, QFormLayout.LabelRole, self.allowRebaseMergeLabel)

        self.allowRebaseMergeCheckBox = QCheckBox(CreateRepo)
        self.allowRebaseMergeCheckBox.setObjectName(u"allowRebaseMergeCheckBox")

        self.formLayout.setWidget(10, QFormLayout.FieldRole, self.allowRebaseMergeCheckBox)

        self.allowMergeCommitLabel = QLabel(CreateRepo)
        self.allowMergeCommitLabel.setObjectName(u"allowMergeCommitLabel")

        self.formLayout.setWidget(11, QFormLayout.LabelRole, self.allowMergeCommitLabel)

        self.allowMergeCommitCheckBox = QCheckBox(CreateRepo)
        self.allowMergeCommitCheckBox.setObjectName(u"allowMergeCommitCheckBox")

        self.formLayout.setWidget(11, QFormLayout.FieldRole, self.allowMergeCommitCheckBox)

        self.gitignoreTemplateLabel = QLabel(CreateRepo)
        self.gitignoreTemplateLabel.setObjectName(u"gitignoreTemplateLabel")

        self.formLayout.setWidget(12, QFormLayout.LabelRole, self.gitignoreTemplateLabel)

        self.gitignoreTemplateComboBox = Autocomplete(CreateRepo)
        self.gitignoreTemplateComboBox.setObjectName(u"gitignoreTemplateComboBox")

        self.formLayout.setWidget(12, QFormLayout.FieldRole, self.gitignoreTemplateComboBox)

        self.verticalLayout.addLayout(self.formLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.createRepoButton = QPushButton(CreateRepo)
        self.createRepoButton.setObjectName(u"createRepoButton")

        self.horizontalLayout_2.addWidget(self.createRepoButton)

        self.cancelButton = QPushButton(CreateRepo)
        self.cancelButton.setObjectName(u"cancelButton")
        sizePolicy.setHeightForWidth(self.cancelButton.sizePolicy().hasHeightForWidth())
        self.cancelButton.setSizePolicy(sizePolicy)

        self.horizontalLayout_2.addWidget(self.cancelButton)

        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(CreateRepo)

        QMetaObject.connectSlotsByName(CreateRepo)
    # setupUi

    def retranslateUi(self, CreateRepo):
        CreateRepo.setWindowTitle(QCoreApplication.translate("CreateRepo", u"New Repository", None))
        self.label.setText(QCoreApplication.translate("CreateRepo", u"Create new repository", None))
        self.nameLabel.setText(QCoreApplication.translate("CreateRepo", u"Name", None))
        self.descriptionLabel.setText(QCoreApplication.translate("CreateRepo", u"Description", None))
        self.homepageLabel.setText(QCoreApplication.translate("CreateRepo", u"Homepage", None))
        self.privateLabel.setText(QCoreApplication.translate("CreateRepo", u"Private", None))
        self.hasIssuesLabel.setText(QCoreApplication.translate("CreateRepo", u"Has issues", None))
        self.hasWikiLabel.setText(QCoreApplication.translate("CreateRepo", u"Has wiki", None))
        self.hasDownloadsLabel.setText(QCoreApplication.translate("CreateRepo", u"Has downloads", None))
        self.hasProjectsLabel.setText(QCoreApplication.translate("CreateRepo", u"Has projects", None))
        self.autoInitLabel.setText(QCoreApplication.translate("CreateRepo", u"Auto init", None))
        self.licenseTemplateLabel.setText(QCoreApplication.translate("CreateRepo", u"License template", None))
        self.allowRebaseMergeLabel.setText(QCoreApplication.translate("CreateRepo", u"Allow rebase merge", None))
        self.allowMergeCommitLabel.setText(QCoreApplication.translate("CreateRepo", u"Allow merge commit", None))
        self.gitignoreTemplateLabel.setText(QCoreApplication.translate("CreateRepo", u"Gitignore template", None))
        self.createRepoButton.setText(QCoreApplication.translate("CreateRepo", u"Create repository", None))
        self.cancelButton.setText(QCoreApplication.translate("CreateRepo", u"Cancel", None))
    # retranslateUi

