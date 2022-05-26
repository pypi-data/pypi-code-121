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

from tikka.domains.entities.node import Node


class NodesRepositoryInterface(abc.ABC):
    """
    NodesRepositoryInterface class
    """

    SORT_ORDER_ASCENDING = 0
    SORT_ORDER_DESCENDING = 1

    COLUMN_ID = "id"
    COLUMN_BLOCK = "block"
    COLUMN_SOFTWARE = "software"
    COLUMN_SOFTWARE_VERSION = "software_version"
    COLUMN_PEER_ID = "peer_id"

    DEFAULT_LIST_OFFSET = 0
    DEFAULT_LIST_LIMIT = 1000

    @abc.abstractmethod
    def add(self, node: Node) -> None:
        """
        Add a new node in repository

        :param node: Node instance
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, id: UUID) -> Optional[Node]:  # pylint: disable=redefined-builtin
        """
        Return Node by ID from repository

        :param id: Node ID
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, node: Node) -> None:
        """
        Update node in repository

        :param node: Node instance
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def list(
        self,
        offset: int = DEFAULT_LIST_OFFSET,
        limit: int = DEFAULT_LIST_LIMIT,
        sort_order: int = SORT_ORDER_ASCENDING,
        sort_column: str = COLUMN_ID,
    ) -> List[Node]:
        """
        List nodes from repository

        :param offset: Offset index to get rows from
        :param limit: Number of rows to return
        :param sort_order: Sort order
        :param sort_column: Sort column name
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, id: UUID) -> None:  # pylint: disable=redefined-builtin
        """
        Delete node by ID in repository

        :param id: ID of Node to delete
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete_all(self) -> None:
        """
        Delete all nodes in repository

        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def count(self) -> int:
        """
        Return number of nodes in repository

        :return:
        """
        raise NotImplementedError
