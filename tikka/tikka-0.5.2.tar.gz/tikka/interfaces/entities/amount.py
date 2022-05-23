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

import abc
from gettext import NullTranslations

from tikka.domains.currencies import Currencies
from tikka.domains.entities.currency import Currency


class AmountInterface(abc.ABC):

    currency: Currency

    def __init__(self, currencies: Currencies, translator: NullTranslations):
        """
        Init AmountInterface class with blockchain value (normally centimes)

        :param currencies: Currencies domain instance
        :param translator: NullTranslations instance (gettext)
        """
        self.currencies = currencies
        self.translator = translator

        self._ = self.translator.gettext

    @abc.abstractmethod
    def value(self, blockchain_value: int) -> float:
        """
        Return amount value expressed in class unit

        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def blockchain_value(self, value: float) -> int:
        """
        Return blockchain value from value in class unit

        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def symbol(self) -> str:
        """
        Return amount unit symbol

        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def name(self) -> str:
        """
        Return amount unit name

        :return:
        """
        raise NotImplementedError
