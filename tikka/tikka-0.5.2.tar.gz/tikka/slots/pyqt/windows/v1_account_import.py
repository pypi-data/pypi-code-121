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
import logging
import sys
from typing import Optional

from duniterpy.key import SigningKey
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox, QWidget
from substrateinterface import Keypair, KeypairType

from tikka.domains.application import Application
from tikka.domains.entities.account import Account
from tikka.domains.entities.constants import DATA_PATH, WALLETS_PASSWORD_LENGTH
from tikka.libs.secret import generate_alphabetic
from tikka.slots.pyqt.resources.gui.windows.v1_account_import_rc import (
    Ui_V1AccountImportDialog,
)


class V1AccountImportWindow(QDialog, Ui_V1AccountImportDialog):
    """
    V1AccountImportWindow class
    """

    def __init__(self, application: Application, parent: Optional[QWidget] = None):
        """
        Init import V1 account window

        :param application: Application instance
        :param parent: QWidget instance
        """
        super().__init__(parent=parent)
        self.setupUi(self)

        self.application = application
        self._ = self.application.translator.gettext

        # buttons
        self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)

        # events
        self.secretIDLineEdit.keyPressEvent = (
            self._on_secret_id_line_edit_keypress_event
        )
        self.passwordIDLineEdit.keyPressEvent = (
            self._on_password_id_line_edit_keypress_event
        )
        self.passwordChangeButton.clicked.connect(self._generate_wallet_password)
        self.buttonBox.accepted.connect(self.on_accepted_button)
        self.buttonBox.rejected.connect(self.close)

        # fill form
        self._generate_wallet_password()

    def _on_secret_id_line_edit_keypress_event(self, event: QKeyEvent):
        """
        Triggered when a key is pressed in the secret ID field

        :return:
        """
        if event.key() == QtCore.Qt.Key_Return:
            self._generate_address()
        else:
            QtWidgets.QLineEdit.keyPressEvent(self.secretIDLineEdit, event)
            # if the key is not return, handle normally

    def _on_password_id_line_edit_keypress_event(self, event: QKeyEvent):
        """
        Triggered when a key is pressed in the password ID field

        :return:
        """
        if event.key() == QtCore.Qt.Key_Return:
            self._generate_address()
        else:
            QtWidgets.QLineEdit.keyPressEvent(self.passwordIDLineEdit, event)
            # if the key is not return, handle normally

    def _generate_address(self) -> bool:
        """
        Generate address from ID

        :return:
        """
        self.v1AddressValueLabel.setText("")
        self.addressValueLabel.setText("")
        self.errorLabel.setText("")
        self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)

        secret_id = self.secretIDLineEdit.text().strip()
        password_id = self.passwordIDLineEdit.text().strip()
        if secret_id == "" or password_id == "":
            return False

        signing_key = SigningKey.from_credentials(secret_id, password_id)
        try:
            address = Keypair.create_from_seed(
                seed_hex=signing_key.seed.hex(),
                ss58_format=self.application.currencies.get_current().ss58_format,
                crypto_type=KeypairType.ED25519,
            ).ss58_address
        except Exception as exception:
            logging.exception(exception)
            self.errorLabel.setText(self._("Error generating account wallet!"))
            return False

        self.addressValueLabel.setText(address)
        self.v1AddressValueLabel.setText(signing_key.pubkey)
        self.buttonBox.button(self.buttonBox.Ok).setEnabled(True)
        return True

    def _generate_wallet_password(self):
        """
        Generate new password for wallet encryption in UI

        :return:
        """
        self.passwordLineEdit.setText(generate_alphabetic(WALLETS_PASSWORD_LENGTH))

    def on_accepted_button(self):
        """
        Triggered when user click on ok button

        :return:
        """
        secret_id = self.secretIDLineEdit.text().strip()
        password_id = self.passwordIDLineEdit.text().strip()
        password = self.passwordLineEdit.text()
        signing_key = SigningKey.from_credentials(secret_id, password_id)

        keypair = Keypair.create_from_seed(
            seed_hex=signing_key.seed.hex(),
            ss58_format=self.application.currencies.get_current().ss58_format,
            crypto_type=KeypairType.ED25519,
        )
        address = keypair.ss58_address

        wallet = self.application.wallets.get(address)
        if wallet is None:
            # create and store Wallet instance
            wallet = self.application.wallets.create(keypair, password)
            self.application.wallets.add(wallet)
        else:
            # display confirm dialog and get response
            button = QMessageBox.question(
                self,
                self._("Change wallet password?"),
                self._(
                    "A wallet already exists for this account. Change password for {address} wallet?"
                ).format(address=wallet.address),
            )
            if button == QMessageBox.Yes:
                # create and store Wallet instance
                new_wallet = self.application.wallets.create(keypair, password)
                self.application.wallets.update(new_wallet)

        account = self.application.accounts.get_by_address(address)
        if account is None:
            # create and store Account instance
            account = Account(
                address,
                crypto_type=KeypairType.ED25519,
                _keypair=keypair,
            )
            self.application.accounts.add(account)
        else:
            self.application.accounts.unlock(account, password)
            self.application.accounts.update(account)


if __name__ == "__main__":
    qapp = QApplication(sys.argv)
    application_ = Application(DATA_PATH)
    V1AccountImportWindow(application_).exec_()
