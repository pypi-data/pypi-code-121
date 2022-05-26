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

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QMutex, QPoint, QSize
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QTableWidgetItem,
    QWidget,
)

from tikka.domains.application import Application
from tikka.domains.entities.account import Account
from tikka.domains.entities.constants import DATA_PATH
from tikka.domains.entities.events import AccountEvent, CurrencyEvent
from tikka.slots.pyqt.entities.constants import (
    ICON_ACCOUNT_LOCKED,
    ICON_ACCOUNT_UNLOCKED,
)
from tikka.slots.pyqt.resources.gui.widgets.account_list_rc import Ui_AccountListWidget
from tikka.slots.pyqt.widgets.account_menu import AccountPopupMenu


class CenteredIconWidget(QWidget):
    """
    CenteredIconWidget class
    """

    def __init__(self, icon_path: str):
        """
        Init a widget with the icon centered

        :param icon_path: Path of the icon in resource index
        """
        super().__init__()
        # create a label with the icon as bitmap
        label = QLabel()
        label.setPixmap(QtGui.QPixmap(icon_path))
        label.setScaledContents(True)
        icon_size = QSize(16, 16)
        label.setMaximumSize(icon_size)

        # create a layout to center icon
        layout = QHBoxLayout(self)
        layout.addWidget(label, 0, QtCore.Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)


class AccountListWidget(QWidget, Ui_AccountListWidget):
    """
    AccountListWidget class
    """

    def __init__(
        self,
        application: Application,
        mutex: QMutex,
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        Init AccountListWidget instance

        :param application: Application instance
        :param mutex: QMutex instance
        :param parent: QWidget instance
        """
        super().__init__(parent=parent)
        self.setupUi(self)

        self.application = application
        self.mutex = mutex

        # set the table rows
        self.init_table_rows()

        # table events
        self.tableWidget.customContextMenuRequested.connect(self.on_context_menu)

        self.application.event_dispatcher.add_event_listener(
            CurrencyEvent.EVENT_TYPE_CHANGED, self.on_currency_event
        )
        self.application.event_dispatcher.add_event_listener(
            AccountEvent.EVENT_TYPE_ADD, self.on_add_account_event
        )
        self.application.event_dispatcher.add_event_listener(
            AccountEvent.EVENT_TYPE_DELETE, self.on_delete_account_event
        )
        self.application.event_dispatcher.add_event_listener(
            AccountEvent.EVENT_TYPE_UPDATE, self.on_update_account_event
        )

    def init_table_rows(self):
        """
        Init table rows with values

        :return:
        """
        # remove all rows
        for _ in range(0, self.tableWidget.rowCount()):
            self.tableWidget.removeRow(0)

        for account in self.application.accounts.list:
            self._add_row(account)

    def _add_row(self, account: Account) -> None:
        """
        Add a row in list for account

        :param account: Account instance

        :return:
        """
        index = self.tableWidget.rowCount()
        self.tableWidget.insertRow(index)
        self._set_row(index, account)

    def _set_row(self, index: int, account: Account):
        """
        Populate row from account data

        :param account: Account instance
        :return:
        """
        if self.application.wallets.exists(account.address):
            if account.keypair is None:
                widget = CenteredIconWidget(ICON_ACCOUNT_LOCKED)
                self.tableWidget.setCellWidget(index, 0, widget)
            else:
                widget = CenteredIconWidget(ICON_ACCOUNT_UNLOCKED)
                self.tableWidget.setCellWidget(index, 0, widget)
        else:
            self.tableWidget.removeCellWidget(index, 0)

        self.tableWidget.setItem(
            index,
            1,
            QTableWidgetItem(account.address),
        )

    def on_currency_event(self, _):
        """
        When a currency event is triggered

        :return:
        """
        self.init_table_rows()

    def on_add_account_event(self, event: AccountEvent):
        """
        Add account row when account is created

        :param event: AccountEvent instance
        :return:
        """
        self._add_row(event.account)

    def on_delete_account_event(self, event: AccountEvent):
        """
        Remove account row when account is deleted

        :param event: AccountEvent instance
        :return:
        """
        for index in range(0, self.tableWidget.rowCount()):
            if (
                self.tableWidget.item(index, 1) is not None
                and self.tableWidget.item(index, 1).text() == event.account.address
            ):
                self.tableWidget.removeRow(index)

    def on_update_account_event(self, event: AccountEvent):
        """
        Update account row when account is updated

        :param event: AccountEvent instance
        :return:
        """
        for index in range(0, self.tableWidget.rowCount()):
            if self.tableWidget.item(index, 1).text() == event.account.address:
                self._set_row(index, event.account)

    def on_context_menu(self, position: QPoint):
        """
        When right button on table widget

        :param position: QPoint instance
        :return:
        """
        # get selected account
        account = self.application.accounts.get_by_index(self.tableWidget.currentRow())
        # display popup menu at click position
        AccountPopupMenu(self.application, account, self.mutex, self).exec_(
            self.tableWidget.mapToGlobal(position)
        )


if __name__ == "__main__":
    qapp = QApplication(sys.argv)

    application_ = Application(DATA_PATH)

    main_window = QMainWindow()
    main_window.show()

    main_window.setCentralWidget(AccountListWidget(application_, QMutex(), main_window))

    sys.exit(qapp.exec_())
