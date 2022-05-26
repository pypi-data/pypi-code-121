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

from PyQt5.QtWidgets import QApplication, QDialog, QWidget
from substrateinterface.utils.ss58 import is_valid_ss58_address

from tikka.domains.application import Application
from tikka.domains.entities.account import Account
from tikka.domains.entities.address import DisplayAddress
from tikka.domains.entities.constants import DATA_PATH
from tikka.slots.pyqt.resources.gui.windows.address_add_rc import Ui_AddressAddDialog

if TYPE_CHECKING:
    import _


class AddressAddWindow(QDialog, Ui_AddressAddDialog):
    """
    AccountAddWindow class
    """

    def __init__(self, application: Application, parent: Optional[QWidget] = None):
        """
        Init add account window

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
        self.buttonBox.accepted.connect(self.on_accepted_button)
        self.addressLineEdit.textChanged.connect(self.on_address_line_edit_changed)
        self.buttonBox.rejected.connect(self.close)

    def _normalize_address_field(self) -> Optional[DisplayAddress]:
        """
        Validate and convert address field to DisplayAddress instance

        :return:
        """
        address = self.addressLineEdit.text()
        if not is_valid_ss58_address(address):
            self.errorLabel.setText(self._("Account address is not valid!"))
            return None

        # create account instance
        account = Account(address)
        for existing_account in self.application.accounts.list:
            if account == existing_account:
                self.errorLabel.setText(self._("Account already exists!"))
                return None

        return DisplayAddress(address)

    def on_address_line_edit_changed(self) -> None:
        """
        Triggered when the address field is changed

        :return:
        """
        display_address = self._normalize_address_field()
        if display_address is not None:
            self.errorLabel.setText("")
            self.buttonBox.button(self.buttonBox.Ok).setEnabled(True)
        else:
            self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)

    def on_accepted_button(self) -> None:
        """
        Triggered when user click on ok button

        :return:
        """
        display_address = self._normalize_address_field()
        if display_address is not None:
            # create account instance
            account = Account(display_address.address)

            # add instance in application
            self.application.accounts.add(account)


if __name__ == "__main__":
    qapp = QApplication(sys.argv)
    application_ = Application(DATA_PATH)
    AddressAddWindow(application_).exec_()
