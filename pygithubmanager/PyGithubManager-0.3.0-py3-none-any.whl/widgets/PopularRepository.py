from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget

from modules.repository import Repository
from ui.widgets import Ui_PopularRepositories


class PopularRepository(QWidget):
    def __init__(self, repository, user):
        """
        Popular repository constructor

        Parameters
        ----------
        repository : github.Repository.Repository
            The repository to display
        user
        """
        super(PopularRepository, self).__init__()
        self.ui = Ui_PopularRepositories()
        self.ui.setupUi(self)

        self.repo = repository
        self.user = user

        self.open_repo_window = None

        self.config()

        self.fill()

    def fill(self):
        """
        Fill the template with the data from the repo
        """
        self.ui.nameLabel.setText(self.repo.name)
        self.ui.visibilityLabel.setText('Private' if self.repo.private else 'Public')
        if self.repo.fork:
            self.ui.forkWidget.set_icon("fa.code-fork")
            self.ui.forkWidget.setText("Forked from " + self.repo.parent.full_name)
            self.ui.forkWidget.setStyleSheet("font-size: 9px;")
            self.ui.forkWidget.show()
        else:
            self.ui.forkWidget.hide()

        self.ui.descLabel.setText(self.repo.description)
        try:
            lang = list(self.repo.get_languages().keys())[0]
            self.ui.langWidget.setText(lang)
            try:
                self.ui.langWidget.set_icon("mdi.language-" + lang.lower())
            except Exception:
                if lang.lower() == "shell":
                    self.ui.langWidget.set_icon("msc.terminal-bash")
                else:
                    self.ui.langWidget.set_icon("fa.github-alt")
        except Exception:
            self.ui.langWidget.hide()

        if self.repo.stargazers_count > 0:
            self.ui.starsWidget.setText(str(self.repo.stargazers_count))
            self.ui.starsWidget.set_icon("fa.star")
        else:
            self.ui.starsWidget.hide()

    def config(self):
        """
        Configure the template
        """
        self.ui.visibilityLabel.setStyleSheet("border: 1px solid black; border-radius: 10px; padding: 1px;")
        self.ui.nameLabel.clicked.connect(self.open_repo)
        self.ui.nameLabel.setStyleSheet("color: blue;")
        self.ui.nameLabel.setCursor(Qt.PointingHandCursor)
        self.ui.frame.setStyleSheet(".QFrame{border: 1px solid black; border-radius: 10px;}")

    def open_repo(self):
        """
        Open the repository in a new window
        """
        self.open_repo_window = Repository(self.repo, self.user)
        self.open_repo_window.show()
