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
from typing import List, Optional

from tikka.domains.entities.currency import Currency


class CurrenciesRepositoryInterface(abc.ABC):
    """
    CurrenciesRepositoryInterface class
    """

    @abc.abstractmethod
    def get(self, code_name: str) -> Optional[Currency]:
        """
        Return currency codename list

        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def code_names(self) -> list:
        """
        Return currency codename list

        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def names(self) -> list:
        """
        Return currency name list

        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_entry_point_urls(self, code_name: str) -> List[str]:
        """
        Return currency entry point urls

        :param code_name: Currency code name
        :return:
        """
        raise NotImplementedError
