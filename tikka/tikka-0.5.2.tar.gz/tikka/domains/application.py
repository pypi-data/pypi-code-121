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

import gettext
import logging
from pathlib import Path
from time import sleep
from typing import Any

from tikka.adapters.network.accounts import NetworkAccounts
from tikka.adapters.network.currency import NetworkCurrency
from tikka.adapters.network.nodes import NetworkNodes
from tikka.adapters.network.rpc.connection import RPCConnection
from tikka.adapters.network.transfers import NetworkTransfers
from tikka.adapters.repository.accounts import Sqlite3AccountsRepository
from tikka.adapters.repository.config import FileConfigRepository
from tikka.adapters.repository.currencies import FileCurrenciesRepository
from tikka.adapters.repository.currency import Sqlite3CurrencyRepository
from tikka.adapters.repository.entry_points import Sqlite3EntryPointsRepository
from tikka.adapters.repository.file_wallets import V1FileWalletsRepository
from tikka.adapters.repository.nodes import Sqlite3NodesRepository
from tikka.adapters.repository.preferences import Sqlite3PreferencesRepository
from tikka.adapters.repository.sqlite3 import Sqlite3Client
from tikka.adapters.repository.tabs import Sqlite3TabRepository
from tikka.adapters.repository.wallets import Sqlite3WalletsRepository
from tikka.domains.accounts import Accounts
from tikka.domains.amounts import Amounts
from tikka.domains.config import Config
from tikka.domains.connections import Connections
from tikka.domains.currencies import Currencies
from tikka.domains.entities.constants import LOCALES_PATH
from tikka.domains.entities.events import CurrencyEvent
from tikka.domains.entry_points import EntryPoints
from tikka.domains.events import EventDispatcher
from tikka.domains.nodes import Nodes
from tikka.domains.transfers import Transfers
from tikka.domains.wallets import Wallets


class Application:
    """
    Application class
    """

    def __init__(self, data_path: Path):
        """
        Init application

        :param data_path: Path instance of application data folder
        """

        # data
        self.data_path = data_path
        # dependency injection
        # init event dispatcher
        self.event_dispatcher = EventDispatcher()
        # init config domain
        config_repository = FileConfigRepository(self.data_path)
        self.config = Config(config_repository)

        # init wallets adapter
        self.file_wallets_repository = V1FileWalletsRepository()
        # database adapter
        self.sqlite3_client = Sqlite3Client(
            self.config.get(Config.CURRENCY_KEY), self.data_path
        )
        # init SQL repositories
        accounts_repository = Sqlite3AccountsRepository(self.sqlite3_client)
        wallets_repository = Sqlite3WalletsRepository(self.sqlite3_client)
        entry_points_repository = Sqlite3EntryPointsRepository(self.sqlite3_client)
        nodes_repository = Sqlite3NodesRepository(self.sqlite3_client)
        currency_repository = Sqlite3CurrencyRepository(self.sqlite3_client)
        self.tab_repository = Sqlite3TabRepository(self.sqlite3_client)
        self.preferences_repository = Sqlite3PreferencesRepository(self.sqlite3_client)

        # init translation
        self.translator = self.init_i18n()

        # init domains
        self.connections = Connections(RPCConnection(), self.event_dispatcher)
        currencies_repository = FileCurrenciesRepository()
        self.currencies = Currencies(
            currencies_repository,
            currency_repository,
            NetworkCurrency(self.connections),
            self.config.get(Config.CURRENCY_KEY),
        )
        self.wallets = Wallets(wallets_repository, self.currencies)
        self.accounts = Accounts(
            accounts_repository,
            NetworkAccounts(self.connections),
            self.wallets,
            self.file_wallets_repository,
            self.event_dispatcher,
        )
        self.amounts = Amounts(self.currencies, self.translator)
        self.transfers = Transfers(
            NetworkTransfers(self.connections), self.event_dispatcher
        )
        self.nodes = Nodes(
            nodes_repository,
            NetworkNodes(self.connections),
            self.event_dispatcher,
        )
        self.entry_points = EntryPoints(
            entry_points_repository,
            self.preferences_repository,
            self.connections,
            self.nodes,
            self.config,
            self.currencies,
            self.event_dispatcher,
        )

        # init network connections
        current_entry_point = self.entry_points.get(self.entry_points.current_url)
        if current_entry_point is not None:
            # connect to RPC API via websocket
            self.connections.connect(current_entry_point)

        # if currency properties required for amount display not populated...
        if self.currencies.get_current().members_count is None:
            # fetch currency properties from network
            self.currencies.fetch_currency_properties_from_network()

    def init_i18n(self) -> Any:
        """
        Init translator from configured language

        :return:
        """
        # define translator for configurated language
        translator = gettext.translation(
            "application",
            str(LOCALES_PATH),
            languages=[self.config.get(Config.LANGUAGE_KEY)],
        )
        # init translator
        translator.install()

        return translator

    def select_currency(self, code_name: str):
        """
        Change currency

        :return:
        """
        if self.config is None:
            raise NoConfigError

        # dispatch event EVENT_TYPE_CHANGED
        event = CurrencyEvent(CurrencyEvent.EVENT_TYPE_PRE_CHANGE, code_name)
        self.event_dispatcher.dispatch_event(event)

        self.config.set(Config.CURRENCY_KEY, code_name)

        if self.sqlite3_client is not None:
            self.sqlite3_client.close()

        while self.sqlite3_client.is_alive():
            sleep(1)
            logging.debug("wait sqlite3 thread to end...")

        # init database connection
        self.sqlite3_client = Sqlite3Client(code_name, self.data_path)

        while not self.sqlite3_client.is_alive():
            sleep(1)
            logging.debug("wait sqlite3 thread to start...")

        # create new repository adapters on the new database
        self.accounts.repository.set_client(self.sqlite3_client)  # type: ignore
        self.wallets.repository.set_client(self.sqlite3_client)  # type: ignore
        self.tab_repository.set_client(self.sqlite3_client)
        self.preferences_repository.set_client(self.sqlite3_client)
        self.entry_points.repository.set_client(self.sqlite3_client)  # type: ignore
        self.nodes.repository.set_client(self.sqlite3_client)  # type: ignore
        self.currencies.currency_repository.set_client(self.sqlite3_client)  # type: ignore
        # fixme: domains should only access others domains, not repositories of other domains
        #        we should create a preferences domain (and tabs domain too)

        self.currencies.set_current(code_name)

        # init domains with new repository adapter
        self.accounts.init_list()
        self.entry_points.init_repository()

        # get current entry point for new network connection
        current_entry_point = self.entry_points.get(self.entry_points.current_url)
        if current_entry_point is not None:
            # disconnect previous currency connection
            self.connections.disconnect()
            # connect to RPC API via websocket
            self.connections.connect(current_entry_point)

        self.currencies.fetch_currency_properties_from_network()

        # dispatch event EVENT_TYPE_CHANGED
        event = CurrencyEvent(
            CurrencyEvent.EVENT_TYPE_CHANGED, self.currencies.get_current().code_name
        )
        self.event_dispatcher.dispatch_event(event)

    def select_language(self, language: str):
        """
        Select GUI language

        :param language: Code of language (ex: "en_US", "fr_FR")
        :return:
        """
        if self.config is None:
            raise NoConfigError

        self.config.set(Config.LANGUAGE_KEY, language)
        self.translator = self.init_i18n()

    def close(self):
        """
        Quit application and close what needs to be closed

        :return:
        """
        # disconnect all connections
        self.connections.disconnect()
        # close Sqlite3 client thread
        self.sqlite3_client.close()


class NoDatabaseError(Exception):
    pass


class NoConfigError(Exception):
    pass
