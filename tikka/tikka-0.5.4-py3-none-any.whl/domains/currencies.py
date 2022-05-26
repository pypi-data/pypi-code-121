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
from typing import List

from tikka.domains.entities.currency import Currency
from tikka.interfaces.adapters.network.currency import NetworkCurrencyInterface
from tikka.interfaces.adapters.repository.currencies import (
    CurrenciesRepositoryInterface,
)
from tikka.interfaces.adapters.repository.currency import CurrencyRepositoryInterface


class Currencies:
    """
    Currencies domain class
    """

    def __init__(
        self,
        repository: CurrenciesRepositoryInterface,
        currency_repository: CurrencyRepositoryInterface,
        network: NetworkCurrencyInterface,
        code_name: str,
    ):
        """
        Init Currencies instance

        :param repository: CurrenciesRepositoryInterface instance
        :param currency_repository: CurrencyRepositoryInterface instance
        :param network: NetworkCurrencyInterface instance
        :param code_name: Code name of current currency instance
        """
        self.repository = repository
        self.currency_repository = currency_repository
        self.network = network
        self._current = self._get(code_name)

    def _get(self, code_name: str) -> Currency:
        """
        Get Currency instance from code_name

        :param code_name: Currency code name
        :return:
        """
        currency = self.currency_repository.get(code_name)
        # if first connection on this currency...
        if currency is None:
            # get currency from currencies yaml file
            currency = self.repository.get(code_name)
            if currency is None:
                raise ValueError("code name is unknown")
            self.currency_repository.add(currency)

        return currency

    def get_current(self) -> Currency:
        """
        Return current Currency instance

        :return:
        """
        return self._current

    def set_current(self, code_name: str) -> None:
        """
        Set current Currency instance by code name

        :param code_name: Currency code name
        :return:
        """
        self._current = self._get(code_name)

    def code_names(self) -> list:
        """
        Return list of currency code names

        :return:
        """
        return self.repository.code_names()

    def names(self) -> list:
        """
        Return list of currency names

        :return:
        """
        return self.repository.names()

    def get_entry_point_urls(self) -> List[str]:
        """
        Return current currency entry point urls

        :return:
        """
        return self.repository.get_entry_point_urls(self.get_current().code_name)

    def fetch_currency_properties_from_network(self):
        """
        Fetch currency properties from network and update currency

        :return:
        """
        currency = self.get_current()
        updated = False

        # constants
        if currency.token_decimals is None:
            token_decimals = self.network.get_token_decimals()
            if token_decimals is not None:
                currency.token_decimals = token_decimals

        if currency.token_symbol is None:
            token_symbol = self.network.get_token_symbol()
            if token_symbol is not None:
                currency.token_symbol = token_symbol

        # mutable properties
        universal_dividend = self.network.get_universal_dividend()
        if universal_dividend is not None:
            currency.universal_dividend = universal_dividend
            updated = True

        monetary_mass = self.network.get_monetary_mass()
        if monetary_mass is not None:
            currency.monetary_mass = monetary_mass
            updated = True

        members_count = self.network.get_members_count()
        if members_count is not None:
            currency.members_count = members_count
            updated = True

        if updated is True:
            self.currency_repository.update(currency)
