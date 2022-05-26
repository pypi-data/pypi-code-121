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
import collections
from gettext import NullTranslations
from typing import Dict

from tikka.domains.currencies import Currencies
from tikka.domains.entities.amounts import UnitAmount, UniversalDividendAmount
from tikka.domains.entities.constants import AMOUNT_UNIT_KEY
from tikka.interfaces.entities.amount import AmountInterface


class Amounts:
    """
    Amounts domain class
    """

    def __init__(self, currencies: Currencies, translator: NullTranslations):
        """
        Init Amounts domain instance

        :param currencies: Currencies domain instance
        :param translator: Gnu gettext NullTranslations instance
        """
        self.currencies = currencies
        self.translator = translator
        self.register: Dict[str, AmountInterface] = collections.OrderedDict()

        self.add_amount(AMOUNT_UNIT_KEY, UnitAmount(self.currencies, self.translator))
        self.add_amount("ud", UniversalDividendAmount(self.currencies, self.translator))

    def add_amount(self, name: str, amount: AmountInterface) -> None:
        """
        Add AmountInterface instance in the register with referential name as key

        :param name: Name of amount referential
        :param amount: AmountInterface instance
        :return:
        """
        self.register[name] = amount

    def get_amount(
        self,
        type_: str,
    ) -> AmountInterface:
        """
        Get AmountInterface instance  from register by type name

        :param type_: Name of amount type
        :param blockchain_value: Value from blockchain
        :return:
        """
        return self.register[type_]

    def get_register_keys(self) -> list:
        """
        Return register keys as list

        :return:
        """
        return list(self.register.keys())

    def get_register_names(self) -> list:
        """
        Return register unit names as list

        :return:
        """
        return [amount.name() for amount in self.register.values()]
