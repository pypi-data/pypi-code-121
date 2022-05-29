from PySide6.QtWidgets import QListWidgetItem


class RepositoriesListWidgetItem(QListWidgetItem):
    def __init__(self, repo):
        """
        RepositoriesListWidgetItem class constructor.

        Parameters
        ----------
        repo
        """
        super().__init__()
        self.repo = repo
