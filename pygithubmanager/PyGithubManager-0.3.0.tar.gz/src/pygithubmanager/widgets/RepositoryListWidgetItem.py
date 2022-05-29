from PySide6.QtWidgets import QListWidgetItem


class RepositoryListWidgetItem(QListWidgetItem):
    def __init__(self, name, is_directory, url, path="", contents=None):
        """
        RepositoryListWidgetItem constructor to store the name, is_directory, url, path and contents of a repository.

        Parameters
        ----------
        name : str
            The name of the repository.
        is_directory : bool
            Whether the repository is a directory or not.
        url : str
            The url of the repository.
        path : str
            The path of the repository.
        contents
            The contents of the repository.
        """
        super().__init__()
        self.name = name
        self.isDirectory = is_directory
        self.url = url
        self.contents = contents
        self.path = path
