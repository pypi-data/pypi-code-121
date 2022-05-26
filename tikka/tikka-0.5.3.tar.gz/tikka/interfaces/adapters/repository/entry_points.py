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
from uuid import UUID

from tikka.domains.entities.entry_point import EntryPoint


class EntryPointsRepositoryInterface(abc.ABC):
    """
    EntryPointsRepositoryInterface class
    """

    SORT_ORDER_ASCENDING = 0
    SORT_ORDER_DESCENDING = 1

    COLUMN_URL = "url"
    COLUMN_NODE_ID = "node_id"

    DEFAULT_LIST_OFFSET = 0
    DEFAULT_LIST_LIMIT = 1000

    @abc.abstractmethod
    def add(self, entry_point: EntryPoint) -> None:
        """
        Add a new entry point in repository

        :param entry_point: EntryPoint instance
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, url: str) -> Optional[EntryPoint]:
        """
        Get entry point by url from repository

        :param url: EntryPoint instance
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, entry_point: EntryPoint) -> None:
        """
        Update entry point in repository

        :param entry_point: EntryPoint instance
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def list(
        self,
        offset: int = DEFAULT_LIST_OFFSET,
        limit: int = DEFAULT_LIST_LIMIT,
        sort_order: int = SORT_ORDER_ASCENDING,
        sort_column: str = COLUMN_URL,
        node_id: Optional[UUID] = None,
    ) -> List[EntryPoint]:
        """
        List entry points from repository

        :param offset: Offset index to get rows from
        :param limit: Number of rows to return
        :param sort_order: Sort order
        :param sort_column: Sort column name
        :param node_id: Filter by node ID
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, url: str) -> None:
        """
        Delete entry point in repository

        :param url: Url of EntryPoint to delete
        :return:
        """
        raise NotImplementedError
