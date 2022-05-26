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
from collections import OrderedDict
from typing import Optional

from PyQt5.QtWidgets import QApplication, QDialog, QWidget
from substrateinterface import Keypair, KeypairType

from tikka.domains.application import Application
from tikka.domains.entities.account import Account
from tikka.domains.entities.constants import (
    DATA_PATH,
    MNEMONIC_WORDS_LENGTH,
    WALLETS_PASSWORD_LENGTH,
)
from tikka.libs.secret import generate_alphabetic
from tikka.slots.pyqt.resources.gui.windows.account_create_rc import (
    Ui_AccountCreateDialog,
)


class AccountCreateWindow(QDialog, Ui_AccountCreateDialog):
    """
    AccountCreateWindow class
    """

    def __init__(self, application: Application, parent: Optional[QWidget] = None):
        """
        Init create account window

        :param application: Application instance
        :param parent: QWidget instance
        """
        super().__init__(parent=parent)
        self.setupUi(self)

        self.application = application
        self._ = self.application.translator.gettext

        # Mnemonic language selector translated
        mnemonic_language_selector = OrderedDict(
            [
                ("en", self._("English")),
                ("fr", self._("French")),
                ("zh-hans", self._("Chinese simplified")),
                ("zh-hant", self._("Chinese traditional")),
                ("it", self._("Italian")),
                ("ja", self._("Japanese")),
                ("ko", self._("Korean")),
                ("es", self._("Spanish")),
            ]
        )
        self.mnemonic_language_codes = list(mnemonic_language_selector.keys())
        for language_name in mnemonic_language_selector.values():
            self.mnemonicLanguageComboBox.addItem(self._(language_name))
        if self.application.config.get("language") == "fr_FR":
            self.mnemonicLanguageComboBox.setCurrentIndex(
                self.mnemonic_language_codes.index("fr")
            )
        elif self.application.config.get("language") == "en_US":
            self.mnemonicLanguageComboBox.setCurrentIndex(
                self.mnemonic_language_codes.index("en")
            )

        # events
        self.changeButton.clicked.connect(self._generate_mnemonic_and_address)
        self.mnemonicLanguageComboBox.currentIndexChanged.connect(
            self._generate_mnemonic_and_address
        )
        self.passwordChangeButton.clicked.connect(self._generate_wallet_password)
        self.buttonBox.accepted.connect(self.on_accepted_button)
        self.buttonBox.rejected.connect(self.close)

        # fill form
        self._generate_mnemonic_and_address()
        self._generate_wallet_password()

    def _generate_mnemonic_and_address(self):
        """
        Generate mnemonic passphrase and address

        :return:
        """
        language_code = self.mnemonic_language_codes[
            self.mnemonicLanguageComboBox.currentIndex()
        ]
        mnemonic = Keypair.generate_mnemonic(MNEMONIC_WORDS_LENGTH, language_code)
        address = Keypair.create_from_mnemonic(
            mnemonic,
            ss58_format=self.application.currencies.get_current().ss58_format,
            crypto_type=KeypairType.SR25519,
            language_code=language_code,
        ).ss58_address

        self.mnemonicLineEdit.setText(mnemonic)
        self.addressLineEdit.setText(address)

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
        address = self.addressLineEdit.text()
        mnemonic = self.mnemonicLineEdit.text()
        password = self.passwordLineEdit.text()
        language_code = self.mnemonic_language_codes[
            self.mnemonicLanguageComboBox.currentIndex()
        ]
        # create keypair from mnemonic to get seed as hexadecimal
        keypair = Keypair.create_from_mnemonic(
            mnemonic=mnemonic,
            language_code=language_code,
            crypto_type=KeypairType.SR25519,
            ss58_format=self.application.currencies.get_current().ss58_format,
        )

        # create and store Wallet instance
        wallet = self.application.wallets.create(keypair, password)
        self.application.wallets.add(wallet)

        # create and store Account instance
        account = Account(
            address,
            crypto_type=KeypairType.SR25519,
        )
        self.application.accounts.add(account)

        # close window
        self.close()


if __name__ == "__main__":
    qapp = QApplication(sys.argv)
    application_ = Application(DATA_PATH)
    AccountCreateWindow(application_).exec_()
