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
from typing import List

from tikka.domains.entities.tab import Tab


class TabRepositoryInterface(abc.ABC):
    """
    TabRepositoryInterface class
    """

    @abc.abstractmethod
    def add(self, tab: Tab) -> None:
        """
        Add a new tab in repository

        :param tab: Tab instance
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, id: str) -> None:  # pylint: disable=redefined-builtin
        """
        Delete tab in repository by ID

        :param id: Tab unique ID
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete_all(self) -> None:
        """
        Delete all tabs in repository

        :return:
        """
        raise NotImplementedError

    def list(self) -> List[Tab]:
        """
        Get tab list

        :return:
        """
        raise NotImplementedError
