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
from typing import Optional

from PyQt5.QtCore import QMutex
from PyQt5.QtWidgets import QApplication, QMenu, QMessageBox, QWidget
from substrateinterface import KeypairType

from tikka.domains.application import Application
from tikka.domains.entities.account import Account
from tikka.domains.entities.constants import DATA_PATH
from tikka.slots.pyqt.windows.account_import import AccountImportWindow
from tikka.slots.pyqt.windows.account_unlock import AccountUnlockWindow
from tikka.slots.pyqt.windows.transfer import TransferWindow
from tikka.slots.pyqt.windows.v1_account_import import V1AccountImportWindow
from tikka.slots.pyqt.windows.wallet_password_change import WalletPasswordChangeWindow


class AccountPopupMenu(QMenu):
    """
    AccountPopupMenu class
    """

    def __init__(
        self,
        application: Application,
        account: Account,
        mutex: QMutex,
        parent: Optional[QWidget] = None,
    ):
        """
        Init AccountPopupMenu instance

        :param application: Application instance
        :param account: Account instance
        :param mutex: QMutex instance
        :param parent: QWidget instance
        """
        super().__init__(parent=parent)

        self.application = application
        self.account = account
        self.mutex = mutex
        self._ = self.application.translator.gettext

        # menu actions
        copy_address_to_clipboard_action = self.addAction(
            self._("Copy address to clipboard")
        )
        copy_address_to_clipboard_action.triggered.connect(
            self.copy_address_to_clipboard
        )
        if self.application.wallets.exists(account.address):
            if account.keypair is None:
                unlock_account_action = self.addAction(self._("Unlock account access"))
                unlock_account_action.triggered.connect(self.unlock_account)
            else:
                transfer_action = self.addAction(self._("Make a transfer"))
                transfer_action.triggered.connect(self.transfer)

                lock_account_action = self.addAction(self._("Lock account access"))
                lock_account_action.triggered.connect(self.lock_account)

            wallet_change_password_action = self.addAction(
                self._("Change wallet password")
            )
            wallet_change_password_action.triggered.connect(self.change_wallet_password)
            wallet_password_forgotten_action = self.addAction(
                self._("Wallet password forgotten")
            )
            wallet_password_forgotten_action.triggered.connect(
                self.wallet_password_forgotten
            )

        forget_account_action = self.addAction(self._("Forget account"))
        forget_account_action.triggered.connect(self.confirm_forget_account)

    def copy_address_to_clipboard(self):
        """
        Copy address of selected row to clipboard

        :return:
        """
        clipboard = QApplication.clipboard()
        clipboard.setText(self.account.address)

    def unlock_account(self):
        """
        Open account unlock window

        :return:
        """
        AccountUnlockWindow(self.application, self.account, self).exec_()

    def transfer(self):
        """
        Open transfer window

        :return:
        """
        TransferWindow(self.application, self.account, self.mutex, self).exec_()

    def lock_account(self):
        """
        Lock account

        :return:
        """
        self.application.accounts.lock(self.account)

    def change_wallet_password(self):
        """
        Open change wallet password window

        :return:
        """
        WalletPasswordChangeWindow(self.application, self.account, self).exec_()

    def wallet_password_forgotten(self):
        """
        Open add account with credentials to reset wallet password

        :return:
        """
        # if wallet type is V2...
        if self.account.crypto_type == KeypairType.SR25519:
            AccountImportWindow(self.application).exec_()
        # wallet V1
        else:
            V1AccountImportWindow(self.application).exec_()

    def confirm_forget_account(self):
        """
        Display confirm dialog then forget account if confirmed

        :return:
        """
        # display confirm dialog and get response
        button = QMessageBox.question(
            self,
            self._("Forget account"),
            self._("Forget account {address}?").format(address=self.account.address),
        )
        if button == QMessageBox.Yes:
            self.application.accounts.delete(self.account)


if __name__ == "__main__":
    qapp = QApplication(sys.argv)

    application_ = Application(DATA_PATH)
    account_ = Account("732SSfuwjB7jkt9th1zerGhphs6nknaCBCTozxUcPWPU")

    menu = AccountPopupMenu(application_, account_, QMutex())
    menu.exec_()

    sys.exit(qapp.exec_())
