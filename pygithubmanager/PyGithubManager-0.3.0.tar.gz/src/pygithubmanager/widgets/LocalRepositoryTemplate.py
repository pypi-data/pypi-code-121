import qtawesome as qta
from PySide6.QtCore import QUrl
from PySide6.QtGui import QIcon, QDesktopServices
from PySide6.QtWidgets import QWidget

from ui.widgets import Ui_LocalRepositoryTemplate
from utils import get_repo_info


class LocalRepositoryTemplate(QWidget):
    def __init__(self, repo_path, user):
        """
        Template for a local repository

        Parameters
        ----------
        repo_path : str
            Path to the repository
        user : User
            User instance
        """
        super(LocalRepositoryTemplate, self).__init__()
        self.ui = Ui_LocalRepositoryTemplate()
        self.ui.setupUi(self)

        self.repo_path = repo_path
        self.user = user

        self.repo_user, self.repo_name, self.full_repo_name = None, None, None

        self.config_ui()

        self.fill()

    def fill(self):
        """
        Fill the template with the information of the repository
        """
        self.repo_user, self.repo_name, self.full_repo_name = get_repo_info(self.repo_path)
        self.ui.repoNameLabel.setText(self.repo_name)
        self.ui.pathLineEdit.setText(self.repo_path)

        try:
            repo = self.user.github.get_repo(self.full_repo_name)
            self.ui.githubButton.setIcon(QIcon(qta.icon('msc.github', color='green')))
            self.ui.githubButton.setToolTip('Open in Browser')
            self.ui.githubButton.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(repo.html_url)))
        except Exception:
            self.ui.githubButton.setIcon(QIcon(qta.icon('msc.github', color='red')))
            self.ui.githubButton.setToolTip('Repository not found in GitHub')

    def config_ui(self):
        """
        Configure the UI
        """
        self.ui.pathLineEdit.setDisabled(True)
