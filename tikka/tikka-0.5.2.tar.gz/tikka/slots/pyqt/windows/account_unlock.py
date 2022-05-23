# Copyright 2021 Vincent Texier <vit@free.fr>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import sys
from typing import TYPE_CHECKING, Optional

from PyQt5.QtWidgets import QApplication, QDialog, QLineEdit, QWidget

from tikka.domains.application import Application
from tikka.domains.entities.account import Account
from tikka.domains.entities.constants import DATA_PATH, WALLETS_PASSWORD_LENGTH
from tikka.slots.pyqt.resources.gui.windows.account_unlock_rc import Ui_UnlockDialog

if TYPE_CHECKING:
    import _


class AccountUnlockWindow(QDialog, Ui_UnlockDialog):
    """
    AccountUnlockWindow class
    """

    def __init__(
        self,
        application: Application,
        account: Account,
        parent: Optional[QWidget] = None,
    ):
        """
        Init unlock account window

        :param application: Application instance
        :param account: Account instance
        :param parent: QWidget instance
        """
        super().__init__(parent=parent)
        self.setupUi(self)

        self.application = application
        self.account = account
        self._ = self.application.translator.gettext

        # populate fields
        self.addressValueLabel.setText(self.account.address)
        # disable Ok button
        self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)

        # events
        self.showButton.clicked.connect(self.on_show_button_clicked)
        self.passwordLineEdit.textChanged.connect(
            self._on_password_line_edit_text_changed
        )
        self.buttonBox.rejected.connect(self.on_rejected_button)

    def _on_password_line_edit_text_changed(self):
        """
        Triggered when text is changed in the password field

        :return:
        """
        if len(self.passwordLineEdit.text()) == WALLETS_PASSWORD_LENGTH:
            self._unlock_account()

    def on_show_button_clicked(self):
        """
        Triggered when user click on show button

        :return:
        """
        if self.passwordLineEdit.echoMode() == QLineEdit.Password:
            self.passwordLineEdit.setEchoMode(QLineEdit.Normal)
            self.showButton.setText(self._("Hide"))
        else:
            self.passwordLineEdit.setEchoMode(QLineEdit.Password)
            self.showButton.setText(self._("Show"))

    def _unlock_account(self) -> None:
        """
        Validate fields and unlock account to enabled ok button

        :return:
        """
        password = self.passwordLineEdit.text().strip().upper()
        self.errorLabel.setText("")
        try:
            result = self.application.accounts.unlock(self.account, password)
        except Exception:
            self.errorLabel.setStyleSheet("color: red;")
            self.errorLabel.setText(self._("Password is not valid!"))
            self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)
            return None

        if not result:
            self.errorLabel.setStyleSheet("color: red;")
            self.errorLabel.setText(self._("Password is not valid!"))
            self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)
            return None

        self.errorLabel.setStyleSheet("color: green;")
        self.errorLabel.setText(self._("Account is unlocked"))
        self.buttonBox.button(self.buttonBox.Ok).setEnabled(True)
        self.buttonBox.button(self.buttonBox.Ok).click()
        return None

    def on_rejected_button(self) -> None:
        """
        Triggered when user click on cancel button

        :return:
        """
        self.application.accounts.lock(self.account)


if __name__ == "__main__":
    qapp = QApplication(sys.argv)
    application_ = Application(DATA_PATH)
    account_ = Account("CUYYUnh7N49WZhs5DULkmqw5Zu5fwsRBmE5LLrUFRpgw")
    AccountUnlockWindow(application_, account_).exec_()
