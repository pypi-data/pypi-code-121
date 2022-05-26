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
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget

from tikka.domains.application import Application
from tikka.domains.entities.constants import AMOUNT_UNIT_KEY, DATA_PATH
from tikka.domains.entities.events import UnitEvent
from tikka.interfaces.adapters.repository.preferences import SELECTED_UNIT
from tikka.slots.pyqt.entities.worker import AsyncQWorker
from tikka.slots.pyqt.resources.gui.widgets.currency_rc import Ui_currencyWidget


class CurrencyWidget(QWidget, Ui_currencyWidget):
    """
    CurrencyWidget class
    """

    def __init__(
        self,
        application: Application,
        mutex: QMutex,
        parent: Optional[QWidget] = None,
    ):
        """
        Init currency widget

        :param application: Application instance
        :param mutex: QMutex instance
        :param parent: QWidget instance
        """
        super().__init__(parent=parent)
        self.setupUi(self)

        self.application = application
        self.mutex = mutex
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

        # application events
        self.application.event_dispatcher.add_event_listener(
            UnitEvent.EVENT_TYPE_CHANGED, lambda e: self._update_ui()
        )

        self.fetch_from_network_async_qworker.start()

    def fetch_from_network(self):
        """
        Fetch last currency data from the network

        :return:
        """
        self.refreshButton.setEnabled(False)
        self.application.currencies.fetch_currency_properties_from_network()

    def _on_finished_fetch_from_network(self):
        """
        Triggered when async request fetch_from_network is finished

        :return:
        """
        self.refreshButton.setEnabled(True)
        self._update_ui()

    def _update_ui(self):
        """
        Update UI values

        :return:
        """
        unit_amount = self.application.amounts.get_amount(AMOUNT_UNIT_KEY)
        selected_amount = self.application.amounts.get_amount(
            self.application.preferences_repository.get(SELECTED_UNIT)
        )

        currency = self.application.currencies.get_current()
        self.nameValueLabel.setText(currency.name)
        self.symbolValueLabel.setText(currency.token_symbol)

        self.universalDividendValueLabel.setText(
            ""
            if currency.universal_dividend is None
            else self.locale().toCurrencyString(
                unit_amount.value(currency.universal_dividend), unit_amount.symbol()
            )
        )
        self.monetaryMassValueLabel.setText(
            ""
            if currency.monetary_mass is None
            else self.locale().toCurrencyString(
                selected_amount.value(currency.monetary_mass), selected_amount.symbol()
            )
        )
        self.membersValueLabel.setText(
            ""
            if currency.members_count is None
            else self.locale().toString(currency.members_count)
        )

    def _on_refresh_button_clicked_event(self):
        """
        Triggered when user click on refresh button

        :return:
        """
        # Disable button
        self.refreshButton.setEnabled(False)
        # Start the thread
        self.fetch_from_network_async_qworker.start()


if __name__ == "__main__":
    qapp = QApplication(sys.argv)

    application_ = Application(DATA_PATH)

    main_window = QMainWindow()
    main_window.show()

    main_window.setCentralWidget(CurrencyWidget(application_, QMutex(), main_window))

    sys.exit(qapp.exec_())
