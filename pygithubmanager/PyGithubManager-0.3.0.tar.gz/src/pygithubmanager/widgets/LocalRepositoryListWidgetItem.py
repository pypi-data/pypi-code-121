from PySide6.QtWidgets import QListWidgetItem


class LocalRepositoryListWidgetItem(QListWidgetItem):
    def __init__(self, name, path):
        """
        QListWidgetItem to store the name and path of a local repository.
        Parameters
        ----------
        name : str
            Name of the repository.
        path : str
            Path of the repository.
        """
        super().__init__()
        self.name = name
        self.path = path
