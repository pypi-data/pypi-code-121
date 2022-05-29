import qtawesome as qta
from PySide6.QtWidgets import QWidget, QApplication, QFileDialog, QMessageBox
from github.Repository import Repository

from ui.widgets import Ui_Clone
from utils import USER_HOME_PATH, clone


class CloneTemplate(QWidget):
    def __init__(self, repository: Repository, user):
        """
        The clone window constructor

        Parameters
        ----------
        repository : Repository
            The repository to clone/obtain the url
        user : User
            The user instance
        """
        super(CloneTemplate, self).__init__()
        self.ui = Ui_Clone()
        self.ui.setupUi(self)

        self.repo: Repository = repository
        self.user = user

        self.config_ui()

        self.config()

        self.fill()

    def fill(self):
        """
        Fill the widget with the repository data
        """
        self.ui.cloneWidget.setText("Clone")
        self.ui.httpsUrlLineEdit.setText(self.repo.clone_url)
        self.ui.sshUrlLineEdit.setText(self.repo.ssh_url)
        self.ui.repoSavePathLineEdit.setText(str(USER_HOME_PATH))

    def config_ui(self):
        """
        Configure the UI
        """
        self.ui.cloneWidget.set_icon("fa5s.terminal")
        self.ui.httpsCopyButton.setIcon(qta.icon("fa5s.copy"))
        self.ui.sshCopyButton.setIcon(qta.icon("fa5s.copy"))

    def config(self):
        """
        Configure the buttons
        """
        self.ui.httpsCopyButton.clicked.connect(
            lambda: QApplication.clipboard().setText(self.ui.httpsUrlLineEdit.text()))
        self.ui.sshCopyButton.clicked.connect(lambda: QApplication.clipboard().setText(self.ui.sshUrlLineEdit.text()))
        self.ui.cloneButton.clicked.connect(self.clone_repo)
        self.ui.selectDirectoryButton.clicked.connect(self.save_path)

    def save_path(self):
        """
        Repository save path
        """
        new_route = QFileDialog.getExistingDirectory(self, "Select folder", str(USER_HOME_PATH))
        if new_route:
            self.ui.repoSavePathLineEdit.setText(new_route)

    def clone_repo(self):
        """
        Clone the repository
        """
        res = clone(self.repo.clone_url, self.ui.repoSavePathLineEdit.text(), self.user)
        self.res_dialog(res[0], res[1])

    def res_dialog(self, res, message):
        """
        Show the result of the clone

        Parameters
        ----------
        res : tuple
            The result of the clone
        message : str
            The message to show
        """
        message_box = QMessageBox()
        message_box.setIcon(QMessageBox.Information if res else QMessageBox.Critical)
        message_box.setText("Repository cloned successfully" if res else "Failed to clone repository")
        if not res:
            message_box.setInformativeText(message)
        message_box.setWindowTitle("Error" if not res else "Success")
        message_box.setStandardButtons(QMessageBox.Ok)
        message_box.exec()
