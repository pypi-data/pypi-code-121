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
from typing import TYPE_CHECKING, Any, List, Optional

from PyQt5 import QtGui
from PyQt5.QtCore import QMutex
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QMainWindow,
    QTableWidgetItem,
    QWidget,
)

from tikka import __version__
from tikka.domains.application import Application
from tikka.domains.entities.account import Account
from tikka.domains.entities.address import DisplayAddress
from tikka.domains.entities.constants import DATA_PATH
from tikka.domains.entities.events import AccountEvent, CurrencyEvent, UnitEvent
from tikka.domains.entities.tab import Tab
from tikka.interfaces.adapters.repository.preferences import (
    SELECTED_TAB_PAGE_KEY,
    SELECTED_UNIT,
)
from tikka.slots.pyqt.entities.constants import (
    ICON_ACCOUNT_LOCKED,
    ICON_ACCOUNT_UNLOCKED,
)
from tikka.slots.pyqt.resources.gui.windows.main_window_rc import Ui_MainWindow
from tikka.slots.pyqt.widgets.account import AccountWidget
from tikka.slots.pyqt.widgets.account_list import AccountListWidget
from tikka.slots.pyqt.widgets.currency import CurrencyWidget
from tikka.slots.pyqt.widgets.licence import LicenceWidget
from tikka.slots.pyqt.widgets.nodes import NodesWidget
from tikka.slots.pyqt.windows.about import AboutWindow
from tikka.slots.pyqt.windows.account_create import AccountCreateWindow
from tikka.slots.pyqt.windows.account_import import AccountImportWindow
from tikka.slots.pyqt.windows.address_add import AddressAddWindow
from tikka.slots.pyqt.windows.configuration import ConfigurationWindow
from tikka.slots.pyqt.windows.entry_point_add import EntryPointAddWindow
from tikka.slots.pyqt.windows.v1_account_import import V1AccountImportWindow
from tikka.slots.pyqt.windows.v1_wallet_import import V1WalletImportWindow

if TYPE_CHECKING:
    pass


class MainWindow(QMainWindow, Ui_MainWindow):
    """
    MainWindow class
    """

    def __init__(self, application: Application, parent: Optional[QWidget] = None):
        """
        Init main window

        :param application: Application instance
        :param parent: QWidget instance
        """
        super().__init__(parent=parent)
        self.setupUi(self)

        self.application = application
        self._ = self.application.translator.gettext

        self.update_title()

        # tab widgets
        self.account_list_widget: Optional[AccountListWidget] = None

        # signals
        self.tabWidget.tabCloseRequested.connect(self.close_tab)

        # connect functions to menu actions
        # accounts menu
        self.actionQuit.triggered.connect(self.close)
        self.actionAccount_list.triggered.connect(self.add_account_list_tab)
        self.actionAdd_an_address.triggered.connect(self.open_add_address_window)
        self.actionImport_account.triggered.connect(self.open_import_account_window)
        self.actionCreate_account.triggered.connect(self.open_create_account_window)

        # V1 accounts menu
        self.actionV1Import_account.triggered.connect(
            self.open_v1_import_account_window
        )
        self.actionV1Import_a_Wallet.triggered.connect(
            self.open_v1_import_wallet_window
        )

        # network menu
        self.actionNodes.triggered.connect(self.add_nodes_tab)
        self.actionAdd_entry_point.triggered.connect(self.open_add_entry_point_window)

        # help menu
        self.actionCurrency.triggered.connect(self.add_currency_tab)
        self.actionG1_licence.triggered.connect(self.add_licence_tab)
        self.actionConfiguration.triggered.connect(self.open_configuration_window)
        self.actionAbout.triggered.connect(self.open_about_window)

        # status bar
        self.unit_combo_box = QComboBox()
        self.statusbar.addPermanentWidget(self.unit_combo_box)
        self.init_units()

        # events
        self.unit_combo_box.activated.connect(self._on_unit_changed)

        # application events
        self.application.event_dispatcher.add_event_listener(
            CurrencyEvent.EVENT_TYPE_PRE_CHANGE, self.on_currency_event
        )
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

        # Qmutex global instance for Qthread locks
        self.mutex = QMutex()

        # open saved tabs
        self.init_tabs()

    def closeEvent(
        self, event: QtGui.QCloseEvent  # pylint: disable=unused-argument
    ) -> None:
        """
        Override close event

        :param event:
        :return:
        """
        # save tabs in repository
        self.save_tabs()

        # save tab selection in preferences
        self.application.preferences_repository.set(
            SELECTED_TAB_PAGE_KEY, self.tabWidget.currentIndex()
        )

        self.application.close()

    def init_units(self) -> None:
        """
        Init units combobox in status bar

        :return:
        """
        self.unit_combo_box.clear()

        self.unit_combo_box.addItems(self.application.amounts.get_register_names())
        preferences_selected_unit = self.application.preferences_repository.get(
            SELECTED_UNIT
        )
        if preferences_selected_unit is None:
            # set first unit in preferences
            self.application.preferences_repository.set(
                SELECTED_UNIT, self.application.amounts.get_register_keys()[0]
            )
            preferences_selected_unit = self.application.preferences_repository.get(
                SELECTED_UNIT
            )

        self.unit_combo_box.setCurrentIndex(
            self.application.amounts.get_register_keys().index(
                preferences_selected_unit
            )
        )

    def init_tabs(self):
        """
        Init tabs from repository

        :return:
        """
        # close all tabs
        self.tabWidget.clear()

        # fetch tabs from repository
        for tab in self.application.tab_repository.list():
            # if account tab...
            if tab.panel_class == AccountWidget.__name__:
                # get account from list
                for account in self.application.accounts.list:
                    if account.address == tab.id:
                        self.add_account_tab(account)
            elif tab.panel_class == CurrencyWidget.__name__:
                self.add_currency_tab()
            elif tab.panel_class == LicenceWidget.__name__:
                self.add_licence_tab()
            elif tab.panel_class == AccountListWidget.__name__:
                self.add_account_list_tab()
            elif tab.panel_class == NodesWidget.__name__:
                self.add_nodes_tab()

        # get preferences
        preferences_selected_page = self.application.preferences_repository.get(
            SELECTED_TAB_PAGE_KEY
        )
        if preferences_selected_page is not None:
            self.tabWidget.setCurrentIndex(int(preferences_selected_page))

    def save_tabs(self):
        """
        Save tabs in tab repository

        :return:
        """
        # clear table
        self.application.tab_repository.delete_all()
        # save tabwidget tabs in repository
        for index in range(0, self.tabWidget.count()):
            widget = self.tabWidget.widget(index)
            if isinstance(widget, AccountWidget):
                # save account tab in repository
                tab = Tab(widget.account.address, str(widget.__class__.__name__))
            else:
                tab = Tab(
                    str(widget.__class__.__name__), str(widget.__class__.__name__)
                )

            self.application.tab_repository.add(tab)

    def close_tab(self, index: int):
        """
        Close tab on signal

        :param index: Index of tab requested to close
        :return:
        """
        self.tabWidget.removeTab(index)

    def add_account_list_tab(self) -> None:
        """
        Open account list tab

        :return:
        """
        # select account list tab if exists
        for widget in self.get_tab_widgets_by_class(AccountListWidget):
            self.tabWidget.setCurrentIndex(self.get_tab_index_from_widget(widget))
            return

        # create tab
        account_list_widget = AccountListWidget(
            self.application, self.mutex, self.tabWidget
        )
        self.tabWidget.addTab(account_list_widget, self._("Account list"))
        # catch account list double click signal
        account_list_widget.tableWidget.itemDoubleClicked.connect(
            self.on_account_list_double_click
        )
        self.tabWidget.setCurrentIndex(self.tabWidget.count() - 1)

    def add_account_tab(self, account: Account):
        """
        Open account list tab

        :return:
        """
        if (
            len(
                [
                    widget
                    for widget in self.get_tab_widgets_by_class(AccountWidget)
                    if isinstance(widget, AccountWidget)
                    and widget.account.address == account.address
                ]
            )
            == 0
        ):
            icon = QIcon()
            if self.application.wallets.exists(account.address):
                if account.keypair is not None:
                    icon = QIcon(ICON_ACCOUNT_UNLOCKED)
                else:
                    icon = QIcon(ICON_ACCOUNT_LOCKED)

            self.tabWidget.addTab(
                AccountWidget(self.application, account, self.mutex, self.tabWidget),
                icon,
                DisplayAddress(account.address).shorten,
            )
            self.tabWidget.setCurrentIndex(self.tabWidget.count() - 1)

    def add_currency_tab(self):
        """
        Open currency tab

        :return:
        """
        # select currency tab if exists
        for widget in self.get_tab_widgets_by_class(CurrencyWidget):
            self.tabWidget.setCurrentIndex(self.get_tab_index_from_widget(widget))
            return

        # create tab
        self.tabWidget.addTab(
            CurrencyWidget(self.application, self.mutex, self.tabWidget),
            self._("Currency"),
        )
        self.tabWidget.setCurrentIndex(self.tabWidget.count() - 1)

    def add_licence_tab(self):
        """
        Open licence tab

        :return:
        """
        # select currency tab if exists
        for widget in self.get_tab_widgets_by_class(LicenceWidget):
            self.tabWidget.setCurrentIndex(self.get_tab_index_from_widget(widget))
            return

        # create tab
        self.tabWidget.addTab(
            LicenceWidget(self.application, self.tabWidget), self._("Ğ1 licence")
        )
        self.tabWidget.setCurrentIndex(self.tabWidget.count() - 1)

    def add_nodes_tab(self):
        """
        Open network nodes tab

        :return:
        """
        # select currency tab if exists
        for widget in self.get_tab_widgets_by_class(NodesWidget):
            self.tabWidget.setCurrentIndex(self.get_tab_index_from_widget(widget))
            return

        # create tab
        self.tabWidget.addTab(
            NodesWidget(self.application, self.mutex, self.tabWidget),
            self._("Network nodes"),
        )
        self.tabWidget.setCurrentIndex(self.tabWidget.count() - 1)

    def update_title(self):
        """
        Update window title with version and currency

        :return:
        """
        self.setWindowTitle(
            "Tikka {version} - {currency}".format(  # pylint: disable=consider-using-f-string
                version=__version__,
                currency=self.application.currencies.get_current().name,
            )
        )

    def open_add_address_window(self) -> None:
        """
        Open add address window

        :return:
        """
        AddressAddWindow(self.application, self).exec_()

    def open_import_account_window(self) -> None:
        """
        Open import account window

        :return:
        """
        AccountImportWindow(self.application, self).exec_()

    def open_create_account_window(self) -> None:
        """
        Open create account window

        :return:
        """
        AccountCreateWindow(self.application, self).exec_()

    def open_v1_import_account_window(self) -> None:
        """
        Open V1 import account window

        :return:
        """
        V1AccountImportWindow(self.application, self).exec_()

    def open_v1_import_wallet_window(self) -> None:
        """
        Open V1 import wallet window

        :return:
        """
        V1WalletImportWindow(self.application, self).exec_()

    def open_configuration_window(self) -> None:
        """
        Open configuration window

        :return:
        """
        ConfigurationWindow(self.application, self).exec_()

    def open_about_window(self) -> None:
        """
        Open about window

        :return:
        """
        AboutWindow(self).exec_()

    def open_add_entry_point_window(self) -> None:
        """
        Open add entry point window

        :return:
        """
        EntryPointAddWindow(self.application, self).exec_()

    def on_currency_event(self, event: CurrencyEvent):
        """
        When a currency event is triggered

        :return:
        """
        if event.type == CurrencyEvent.EVENT_TYPE_PRE_CHANGE:
            self.save_tabs()
        else:
            self.update_title()
            self.init_tabs()

    def on_account_list_double_click(self, item: QTableWidgetItem):
        """
        When an account is double clicked in account list

        :param item: QTableWidgetItem instance
        :return:
        """
        account = self.application.accounts.list[item.row()]
        self.add_account_tab(account)

    def on_add_account_event(self, event: AccountEvent) -> None:
        """
        Triggered when an account is created

        :param event: AccountEvent instance
        :return:
        """
        self.add_account_tab(event.account)

    def on_update_account_event(self, event: AccountEvent) -> None:
        """
        Triggered when an account is updated

        :param event: AccountEvent instance
        :return:
        """
        index = 0
        for index in range(0, self.tabWidget.count()):
            widget = self.tabWidget.widget(index)
            if (
                isinstance(widget, AccountWidget)
                and widget.account.address == event.account.address
            ):
                break
        icon = QIcon()
        if self.application.wallets.exists(event.account.address):
            if event.account.keypair is not None:
                icon = QIcon(ICON_ACCOUNT_UNLOCKED)
            else:
                icon = QIcon(ICON_ACCOUNT_LOCKED)

        self.tabWidget.setTabIcon(index, icon)
        self.tabWidget.setCurrentIndex(index)

    def on_delete_account_event(self, event: AccountEvent) -> None:
        """
        Triggered when an account is deleted

        :param event: AccountEvent instance
        :return:
        """
        for widget in self.get_tab_widgets_by_class(AccountWidget):
            if (
                isinstance(widget, AccountWidget)
                and widget.account.address == event.account.address
            ):
                self.tabWidget.removeTab(self.tabWidget.indexOf(widget))

    def _on_unit_changed(self) -> None:
        """
        Triggered when unit_combo_box selection changed

        :return:
        """
        unit_key = list(self.application.amounts.register.keys())[
            self.unit_combo_box.currentIndex()
        ]
        self.application.preferences_repository.set(SELECTED_UNIT, unit_key)
        self.application.event_dispatcher.dispatch_event(
            UnitEvent(UnitEvent.EVENT_TYPE_CHANGED)
        )

    def get_tab_widgets_by_class(self, widget_class: Any) -> List[QWidget]:
        """
        Return a list of widget which are instance of widget_class

        :param widget_class: Widget class
        :return:
        """
        widgets = []
        for index in range(0, self.tabWidget.count()):
            widget = self.tabWidget.widget(index)
            if isinstance(widget, widget_class):
                widgets.append(widget)

        return widgets

    def get_tab_index_from_widget(self, widget: QWidget) -> Optional[int]:
        """
        Return tab index of widget, or None if no tab with this widget

        :param widget: QWidget inherited instance
        :return:
        """
        for index in range(0, self.tabWidget.count()):
            if widget == self.tabWidget.widget(index):
                return index

        return None


if __name__ == "__main__":
    qapp = QApplication(sys.argv)
    application_ = Application(DATA_PATH)
    MainWindow(application_).show()
    sys.exit(qapp.exec_())
