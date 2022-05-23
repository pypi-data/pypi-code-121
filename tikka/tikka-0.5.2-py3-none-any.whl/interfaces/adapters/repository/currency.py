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
from typing import Optional

from tikka.domains.entities.currency import Currency


class CurrencyRepositoryInterface(abc.ABC):
    """
    CurrencyRepositoryInterface class
    """

    @abc.abstractmethod
    def add(self, currency: Currency) -> None:
        """
        Add currency in repository

        :param currency: Currency instance
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, code_name: str) -> Optional[Currency]:
        """
        Get Currency instance from repository

        :param code_name: Currency code name
        :return:
        """
        raise NotImplementedError

    def update(self, currency: Currency) -> None:
        """
        Update currency in repository

        :param currency: Currency instance
        :return:
        """
        raise NotImplementedError
