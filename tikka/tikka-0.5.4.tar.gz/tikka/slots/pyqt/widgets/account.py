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

from PyQt5.QtCore import QMutex, QPoint
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget

from tikka.domains.application import Application
from tikka.domains.entities.account import Account
from tikka.domains.entities.constants import DATA_PATH
from tikka.domains.entities.events import AccountEvent, TransferEvent, UnitEvent
from tikka.interfaces.adapters.repository.preferences import SELECTED_UNIT
from tikka.slots.pyqt.entities.constants import (
    ICON_ACCOUNT_LOCKED,
    ICON_ACCOUNT_UNLOCKED,
)
from tikka.slots.pyqt.entities.worker import AsyncQWorker
from tikka.slots.pyqt.resources.gui.widgets.account_rc import Ui_AccountWidget
from tikka.slots.pyqt.widgets.account_menu import AccountPopupMenu
from tikka.slots.pyqt.windows.account_unlock import AccountUnlockWindow
from tikka.slots.pyqt.windows.transfer import TransferWindow


class AccountWidget(QWidget, Ui_AccountWidget):
    """
    AccountWidget class
    """

    def __init__(
        self,
        application: Application,
        account: Account,
        mutex: QMutex,
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        Init AccountWidget instance

        :param application: Application instance
        :param account: Account instance
        :param mutex: QMutex instance
        :param parent: QWidget instance
        """
        super().__init__(parent=parent)
        self.setupUi(self)

        self.application = application
        self.account = account
        self.mutex = mutex

        self.addressLabel.setText(self.account.address)

        self._update_ui()

        ##############################
        # ASYNC METHODS
        ##############################
        # Create a QWorker object
        self.fetch_from_network_async_qworker = AsyncQWorker(
            self.fetch_from_network, self.mutex
        )
        self.fetch_from_network_async_qworker.finished.connect(
            self._on_finished_fetch_from_network
        )

        # events
        self.refreshButton.clicked.connect(self.fetch_from_network_async_qworker.start)
        self.transferButton.clicked.connect(self.transfer)
        self.customContextMenuRequested.connect(self.on_context_menu)

        # application events
        self.application.event_dispatcher.add_event_listener(
            AccountEvent.EVENT_TYPE_UPDATE, lambda e: self._update_ui()
        )
        self.application.event_dispatcher.add_event_listener(
            UnitEvent.EVENT_TYPE_CHANGED, lambda e: self._update_ui()
        )
        self.application.event_dispatcher.add_event_listener(
            TransferEvent.EVENT_TYPE_SENT, lambda e: self._on_transfer_sent()
        )

        self.fetch_from_network_async_qworker.start()

    def transfer(self):
        """
        When user click on transfer button

        :return:
        """
        # account is locked ?
        if self.account.keypair is None:
            # open unlock account window
            AccountUnlockWindow(self.application, self.account, self.parent()).exec_()

        if self.account.keypair is not None:
            parent = self.parent()
            TransferWindow(self.application, self.account, self.mutex, parent).exec_()

    def _on_transfer_sent(self):
        """
        Triggered after a successful transfer event

        :return:
        """
        # update account balance from network
        self.fetch_from_network_async_qworker.start()

    def fetch_from_network(self):
        """
        Fetch last account data from the network

        :return:
        """
        self.refreshButton.setEnabled(False)
        self.application.accounts.fetch_balance_from_network(self.account)

    def _on_finished_fetch_from_network(self):
        """
        Triggered when async request fetch_from_network is finished

        :return:
        """
        self.application.accounts.update(self.account)
        self.refreshButton.setEnabled(True)
        self._update_ui()

    def _update_ui(self):
        """
        Update UI from self.account

        :return:
        """
        amount = self.application.amounts.get_amount(
            self.application.preferences_repository.get(SELECTED_UNIT)
        )
        if self.account.balance is None:
            self.balanceLabel.setText("?")
        else:
            self.balanceLabel.setText(
                self.locale().toCurrencyString(
                    amount.value(self.account.balance), amount.symbol()
                )
            )

        if self.application.wallets.exists(self.account.address):
            if self.account.keypair is None:
                self.lockStatusIcon.setPixmap(QPixmap(ICON_ACCOUNT_LOCKED))
            else:
                self.lockStatusIcon.setPixmap(QPixmap(ICON_ACCOUNT_UNLOCKED))
            self.lockStatusIcon.show()
        else:
            self.lockStatusIcon.hide()

    def on_context_menu(self, position: QPoint):
        """
        When right button on account tab

        :return:
        """
        # display popup menu at click position
        menu = AccountPopupMenu(self.application, self.account, self.mutex, self)
        menu.exec_(self.mapToGlobal(position))


if __name__ == "__main__":
    qapp = QApplication(sys.argv)

    application_ = Application(DATA_PATH)
    account_ = Account("5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY")

    main_window = QMainWindow()
    main_window.show()

    main_window.setCentralWidget(
        AccountWidget(application_, account_, QMutex(), main_window)
    )

    sys.exit(qapp.exec_())
