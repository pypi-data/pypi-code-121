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

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QApplication, QDialog, QLineEdit, QWidget

from tikka.domains.application import Application
from tikka.domains.entities.account import Account
from tikka.domains.entities.constants import DATA_PATH, WALLETS_PASSWORD_LENGTH
from tikka.libs.secret import generate_alphabetic
from tikka.slots.pyqt.resources.gui.windows.wallet_password_change_rc import (
    Ui_PasswordChangeDialog,
)

if TYPE_CHECKING:
    import _


class WalletPasswordChangeWindow(QDialog, Ui_PasswordChangeDialog):
    """
    WalletPasswordChangeWindow class
    """

    def __init__(
        self,
        application: Application,
        account: Account,
        parent: Optional[QWidget] = None,
    ):
        """
        Init password change window

        :param application: Application instance
        :param account: Account instance
        :param parent: QWidget instance
        """
        super().__init__(parent=parent)
        self.setupUi(self)

        self.application = application
        self.account = account
        self.keypair = None
        self._ = self.application.translator.gettext

        # populate fields
        self.addressValueLabel.setText(self.account.address)

        # if account is already unlocked...
        if self.account.keypair is not None:
            # get keypair
            self.keypair = self.account.keypair
            # hide useless password fields
            self.passwordLabel.hide()
            self.passwordLineEdit.hide()
            self.showButton.hide()
        else:
            # disable Ok button
            self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)

        # events
        self.showButton.clicked.connect(self.on_show_button_clicked)
        self.passwordLineEdit.keyPressEvent = self._on_password_line_edit_keypress_event
        self.changeButton.clicked.connect(self._generate_wallet_password)
        self.buttonBox.accepted.connect(self.on_accepted_button)
        self.buttonBox.rejected.connect(self.on_rejected_button)

        self._generate_wallet_password()

    def _generate_wallet_password(self):
        """
        Generate new password for wallet encryption in UI

        :return:
        """
        self.newPasswordLineEdit.setText(generate_alphabetic(WALLETS_PASSWORD_LENGTH))

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

    def _on_password_line_edit_keypress_event(self, event: QKeyEvent):
        """
        Triggered when a key is pressed in the password field

        :return:
        """
        if event.key() == QtCore.Qt.Key_Return:
            self._get_keypair()
        else:
            QtWidgets.QLineEdit.keyPressEvent(self.passwordLineEdit, event)
            # if the key is not return, handle normally

    def _get_keypair(self) -> None:
        """
        Validate fields and get wallet keypair to enabled ok button

        :return:
        """
        password = self.passwordLineEdit.text().strip().upper()
        try:
            self.keypair = self.application.wallets.get_keypair(
                self.account.address, password
            )
        except Exception:
            self.errorLabel.setText(self._("Password is not valid!"))
            self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)
            return None

        if not self.keypair:
            self.errorLabel.setText(self._("Password is not valid!"))
            self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)
            return None

        self.buttonBox.button(self.buttonBox.Ok).setEnabled(True)
        self.errorLabel.setText("")
        return None

    def on_rejected_button(self) -> None:
        """
        Triggered when user click on cancel button

        :return:
        """
        self.application.accounts.lock(self.account)

    def on_accepted_button(self):
        """
        Triggered when user click on ok button

        :return:
        """
        new_password = self.newPasswordLineEdit.text().strip()

        # create new Wallet instance and update repository
        wallet = self.application.wallets.create(self.keypair, new_password)
        self.application.wallets.update(wallet)

        # close window
        del self.keypair
        self.close()


if __name__ == "__main__":
    qapp = QApplication(sys.argv)
    application_ = Application(DATA_PATH)
    account_ = Account("CUYYUnh7N49WZhs5DULkmqw5Zu5fwsRBmE5LLrUFRpgw")
    WalletPasswordChangeWindow(application_, account_).exec_()
