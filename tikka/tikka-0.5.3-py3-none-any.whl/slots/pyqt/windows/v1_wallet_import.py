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
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QLineEdit,
    QMessageBox,
    QWidget,
)
from substrateinterface import Keypair, KeypairType

from tikka.domains.application import Application
from tikka.domains.entities.account import Account
from tikka.domains.entities.constants import DATA_PATH, WALLETS_PASSWORD_LENGTH
from tikka.domains.entities.wallet import V1FileWallet
from tikka.interfaces.adapters.repository.preferences import (
    WALLET_LOAD_DEFAULT_DIRECTORY,
)
from tikka.libs.secret import generate_alphabetic
from tikka.slots.pyqt.resources.gui.windows.v1_wallet_import_rc import (
    Ui_V1WalletImportDialog,
)

if TYPE_CHECKING:
    pass


class V1WalletImportWindow(QDialog, Ui_V1WalletImportDialog):
    """
    V1WalletImportWindow class
    """

    def __init__(
        self,
        application: Application,
        parent: Optional[QWidget] = None,
    ):
        """
        Init V1 import wallet window

        :param application: Application instance
        :param parent: QWidget instance
        """
        super().__init__(parent=parent)
        self.setupUi(self)

        self.application = application
        self.v1_wallet: Optional[V1FileWallet] = None
        self._ = self.application.translator.gettext

        # events
        self.showButton.clicked.connect(self._on_show_button_clicked)
        self.browseFilesButton.clicked.connect(self._on_browse_files_button_clicked)
        self.filePasswordLineEdit.keyPressEvent = (
            self._on_password_line_edit_keypress_event
        )
        self.buttonBox.rejected.connect(self.close)
        self.buttonBox.accepted.connect(self._on_accepted_button)
        self.changeButton.clicked.connect(self._generate_wallet_password)

        self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)
        self._generate_wallet_password()

    def _generate_wallet_password(self):
        """
        Generate new password for wallet encryption in UI

        :return:
        """
        self.passwordLineEdit.setText(generate_alphabetic(WALLETS_PASSWORD_LENGTH))

    def _on_show_button_clicked(self):
        """
        Triggered when user click on show button

        :return:
        """
        if self.filePasswordLineEdit.echoMode() == QLineEdit.Password:
            self.filePasswordLineEdit.setEchoMode(QLineEdit.Normal)
            self.showButton.setText(self._("Hide"))
        else:
            self.filePasswordLineEdit.setEchoMode(QLineEdit.Password)
            self.showButton.setText(self._("Show"))

    def _on_browse_files_button_clicked(self):
        """
        Triggered when user click on browse files button

        :return:
        """
        # clear path
        self.pathValueLabel.setText("")

        # open file dialog
        filepath = self.open_file_dialog()
        if filepath is not None:
            # update default dir preference
            self.application.preferences_repository.set(
                WALLET_LOAD_DEFAULT_DIRECTORY,
                str(Path(filepath).expanduser().absolute().parent),
            )
            self.pathValueLabel.setText(filepath)
            self._load_wallet()

    def _load_wallet(self):
        """
        Load wallet file

        :return:
        """
        password = self.filePasswordLineEdit.text().strip()
        try:
            self.v1_wallet = self.application.file_wallets_repository.load(
                self.pathValueLabel.text(), password
            )
        except Exception:
            self.errorLabel.setText(self._("Unable to decrypt file!"))
            self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)
            return

        if not self.v1_wallet.signing_key:
            self.errorLabel.setText(self._("File password is not valid!"))
            self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)
            return

        # wallet decrypted
        self.v1AddressValueLabel.setText(self.v1_wallet.signing_key.pubkey)
        keypair = Keypair.create_from_seed(
            seed_hex=self.v1_wallet.signing_key.seed.hex(),
            ss58_format=self.application.currencies.get_current().ss58_format,
            crypto_type=KeypairType.ED25519,
        )
        self.addressValueLabel.setText(keypair.ss58_address)
        if self.application.accounts.get_by_address(keypair.ss58_address) is not None:
            self.errorLabel.setText(self._("Account already exists!"))
            self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)
        else:
            self.errorLabel.setText("")
            self.buttonBox.button(self.buttonBox.Ok).setEnabled(True)

    def open_file_dialog(self) -> Optional[str]:
        """
        Open file dialog and return the selected filepath or None

        :return:
        """
        default_dir = self.application.preferences_repository.get(
            WALLET_LOAD_DEFAULT_DIRECTORY
        )
        if default_dir is not None:
            default_dir = str(Path(default_dir).expanduser().absolute())
        else:
            default_dir = ""

        result = QFileDialog.getOpenFileName(
            self, self._("Choose wallet file"), default_dir, "EWIF Files (*.dunikey)"
        )
        if result[0] == "":
            return None

        return result[0]

    def _on_password_line_edit_keypress_event(self, event: QKeyEvent):
        """
        Triggered when a key is pressed in the password field

        :return:
        """
        if event.key() == QtCore.Qt.Key_Return:
            self._load_wallet()
        else:
            QtWidgets.QLineEdit.keyPressEvent(self.filePasswordLineEdit, event)
            # if the key is not return, handle normally

    def _on_accepted_button(self):
        """
        Triggered when user click on cancel button

        :return:
        """
        if self.v1_wallet is not None:
            password = self.passwordLineEdit.text()
            keypair = Keypair.create_from_seed(
                seed_hex=self.v1_wallet.signing_key.seed.hex(),
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
    V1WalletImportWindow(
        application_,
    ).exec_()
