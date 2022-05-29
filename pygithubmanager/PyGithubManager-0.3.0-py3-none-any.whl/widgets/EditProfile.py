import qtawesome as qta
from PySide6.QtWidgets import QWidget
from github import GithubException
from github.AuthenticatedUser import AuthenticatedUser

from ui.widgets import Ui_EditProfile
from utils import message


class EditProfile(QWidget):
    def __init__(self, user):
        """
        EditProfile constructor

        Parameters
        ----------
        user : User
            User instance
        """
        super(EditProfile, self).__init__()

        self.ui = Ui_EditProfile()
        self.ui.setupUi(self)

        self.user: AuthenticatedUser = user.get_data()

        self.fill()
        self.config()

    def fill(self):
        """
        Fill the widgets with the data
        """
        self.ui.nameLineEdit.setText(self.user.name)
        self.ui.bioTextEdit.setText(self.user.bio)
        self.ui.companyLineEdit.setText(self.user.company)
        self.ui.locationLineEdit.setText(self.user.location)
        self.ui.companyLabel.setPixmap(qta.icon('fa5s.building').pixmap(16, 16))
        self.ui.locationLabel.setPixmap(qta.icon('fa5s.map-marker').pixmap(16, 16))

    def config(self):
        """
        Configure the widgets
        """
        self.ui.saveButton.clicked.connect(self.save)
        self.ui.cancelButton.clicked.connect(self.close)

    def save(self):
        """
        Save the data

        Raises
        ------
        Exception
            If there is an error updating the user
        """
        try:
            self.user.edit(self.ui.nameLineEdit.text(), bio=self.ui.bioTextEdit.toPlainText(),
                           company=self.ui.companyLineEdit.text(), location=self.ui.locationLineEdit.text())
            message('success', 'Profile updated successfully')
            self.close()
        except GithubException as e:
            message('error', e.data['message'])
