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

from tikka.interfaces.entities.amount import AmountInterface


class UnitAmount(AmountInterface):
    """
    UnitAmount class
    """

    def value(self, blockchain_value: int) -> float:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            AmountInterface.value.__doc__
        )
        decimals = (
            2
            if self.currencies.get_current().token_decimals is None
            else self.currencies.get_current().token_decimals
        )
        return blockchain_value / pow(10, decimals)  # type: ignore

    def blockchain_value(self, value: float) -> int:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            AmountInterface.blockchain_value.__doc__
        )
        decimals = (
            2
            if self.currencies.get_current().token_decimals is None
            else self.currencies.get_current().token_decimals
        )
        return round(value * pow(10, decimals))  # type: ignore

    def symbol(self) -> str:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            AmountInterface.symbol.__doc__
        )
        symbol = (
            self.currencies.get_current().name
            if self.currencies.get_current().token_symbol is None
            else self.currencies.get_current().token_symbol
        )
        return symbol  # type: ignore

    def name(self) -> str:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            AmountInterface.name.__doc__
        )
        return self._("Units")


class UniversalDividendAmount(AmountInterface):
    """
    UniversalDividendAmount class
    """

    def value(self, blockchain_value: int) -> float:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            AmountInterface.value.__doc__
        )
        if self.currencies.get_current().universal_dividend is None:
            return 0
        return blockchain_value / self.currencies.get_current().universal_dividend  # type: ignore

    def blockchain_value(self, value: float) -> int:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            AmountInterface.blockchain_value.__doc__
        )
        if self.currencies.get_current().universal_dividend is None:
            return 0
        return round(value * self.currencies.get_current().universal_dividend)  # type: ignore

    def symbol(self) -> str:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            AmountInterface.symbol.__doc__
        )
        symbol = (
            self.currencies.get_current().name
            if self.currencies.get_current().token_symbol is None
            else self.currencies.get_current().token_symbol
        )
        return self._("UD {symbol}").format(symbol=symbol)

    def name(self) -> str:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            AmountInterface.name.__doc__
        )
        return self._("Universal Dividend")
