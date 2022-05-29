from PySide6.QtWidgets import QWidget
from github import GithubException

from modules.repository import Repository
from ui.widgets import Ui_CreateRepo
from utils import message


class CreateRepository(QWidget):
    def __init__(self, user):
        """
        Module for creating a new repository in the user's account.

        Parameters
        ----------
        user: User
            The user who will create the repository.
        """
        super(CreateRepository, self).__init__()

        self.ui = Ui_CreateRepo()
        self.ui.setupUi(self)

        self.user = user

        self.new_repo = None

        self.config()
        self.fill()

    def fill(self):
        """
        Fill the combo boxes with the available templates.
        """
        ignores = [""]
        repo = self.user.github.get_repo("github/gitignore")
        for file in repo.get_contents(""):
            if file.type == "file":
                ignores.append(file.name.split(".")[0])
        self.ui.gitignoreTemplateComboBox.add_items(ignores)

        licenses = ["", "MIT", "ISC", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "GPL-2.0", "GPL-3.0", "LGPL-2.1",
                    "LGPL-3.0", "Unlicense", "AGPL-3.0"]

        self.ui.licenseTemplateComboBox.add_items(licenses)

    def config(self):
        """
        Configure the module.
        """
        self.ui.cancelButton.clicked.connect(self.close)
        self.ui.createRepoButton.clicked.connect(self.create_repo)
        self.ui.nameLineEdit.textChanged.connect(self.check_name)
        self.ui.warningLabel.setText("")
        self.ui.warningLabel.set_icon("fa.warning", "orange")
        self.ui.warningLabel.hide()

    def check_name(self, text):
        """
        Check if the name of the repository is valid.

        Parameters
        ----------
        text : str
            The name of the repository.
        """
        if " " in text:
            self.ui.warningLabel.setText("Your new repository will be created as " + text.replace(" ", "-") + ".")
            if self.ui.warningLabel.isHidden():
                self.ui.warningLabel.show()
        else:
            self.ui.warningLabel.hide()

    def create_repo(self):
        """
        Create a new repository.
        """
        if message('warning', 'Are you sure you want to create this repository?'):
            if self.ui.nameLineEdit.text() != '':
                try:
                    repo = self.user.get_data().create_repo(
                        name=self.ui.nameLineEdit.text(),
                        description=self.ui.descriptionLineEdit.text(),
                        homepage=self.ui.homepageLineEdit.text(),
                        private=self.ui.privateCheckBox.isChecked(),
                        has_issues=self.ui.hasIssuesCheckBox.isChecked(),
                        has_wiki=self.ui.hasWikiCheckBox.isChecked(),
                        has_downloads=self.ui.hasDownloadsCheckBox.isChecked(),
                        auto_init=self.ui.autoInitCheckBox.isChecked(),
                        allow_merge_commit=self.ui.allowMergeCommitCheckBox.isChecked(),
                        allow_rebase_merge=self.ui.allowRebaseMergeCheckBox.isChecked(),
                        license_template=self.ui.licenseTemplateComboBox.currentText(),
                        gitignore_template=self.ui.gitignoreTemplateComboBox.currentText())

                    self.new_repo = Repository(repo, self.user)
                    self.new_repo.show()

                    self.close()
                except GithubException as e:
                    message('error', e.data['message'])
            else:
                message('error', 'Repository name cannot be empty')
