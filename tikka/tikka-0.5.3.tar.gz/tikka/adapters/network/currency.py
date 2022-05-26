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
import logging
from typing import Optional

from tikka.interfaces.adapters.network.currency import NetworkCurrencyInterface


class NetworkCurrency(NetworkCurrencyInterface):
    """
    NetworkCurrency class
    """

    def get_token_decimals(self) -> Optional[int]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NetworkCurrencyInterface.get_token_decimals.__doc__
        )
        if not self.connections.is_connected():
            return None
        if self.connections.rpc.client is None:
            return None

        try:
            result = self.connections.rpc.client.rpc_request(
                "system_properties", []
            ).get("result")
        except Exception as exception:
            logging.exception(exception)
            return None

        return result["tokenDecimals"]

    def get_token_symbol(self) -> Optional[str]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NetworkCurrencyInterface.get_token_symbol.__doc__
        )
        if not self.connections.is_connected():
            return None
        if self.connections.rpc.client is None:
            return None

        try:
            result = self.connections.rpc.client.rpc_request(
                "system_properties", []
            ).get("result")
        except Exception as exception:
            logging.exception(exception)
            return None

        return result["tokenSymbol"]

    def get_universal_dividend(self) -> Optional[int]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NetworkCurrencyInterface.get_universal_dividend.__doc__
        )
        if not self.connections.is_connected():
            return None
        if self.connections.rpc.client is None:
            return None

        try:
            result = self.connections.rpc.client.query("UniversalDividend", "CurrentUd")
        except Exception as exception:
            logging.exception(exception)
            return None

        return result.value

    def get_monetary_mass(self) -> Optional[int]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NetworkCurrencyInterface.get_monetary_mass.__doc__
        )
        if not self.connections.is_connected():
            return None
        if self.connections.rpc.client is None:
            return None

        try:
            result = self.connections.rpc.client.query(
                "UniversalDividend", "MonetaryMass"
            )
        except Exception as exception:
            logging.exception(exception)
            return None

        return result.value

    def get_members_count(self) -> Optional[int]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NetworkCurrencyInterface.get_members_count.__doc__
        )
        if not self.connections.is_connected():
            return None
        if self.connections.rpc.client is None:
            return None

        try:
            result = self.connections.rpc.client.query(
                "UdAccountsStorage", "CounterForUdAccounts"
            )
        except Exception as exception:
            logging.exception(exception)
            return None

        return result.value
