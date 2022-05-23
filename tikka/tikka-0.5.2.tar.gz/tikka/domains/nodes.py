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
from typing import List, Optional
from uuid import UUID

from tikka.domains.entities.events import NodesEvent
from tikka.domains.entities.node import Node
from tikka.domains.events import EventDispatcher
from tikka.interfaces.adapters.network.nodes import NetworkNodesInterface
from tikka.interfaces.adapters.repository.nodes import NodesRepositoryInterface


class Nodes:
    """
    Nodes domain class
    """

    DEFAULT_LIST_OFFSET = 0
    DEFAULT_LIST_LIMIT = 1000

    SORT_ORDER_ASCENDING = NodesRepositoryInterface.SORT_ORDER_ASCENDING
    SORT_ORDER_DESCENDING = NodesRepositoryInterface.SORT_ORDER_DESCENDING

    PROPERTY_ID = NodesRepositoryInterface.COLUMN_ID
    PROPERTY_PEER_ID = NodesRepositoryInterface.COLUMN_PEER_ID
    PROPERTY_BLOCK = NodesRepositoryInterface.COLUMN_BLOCK
    PROPERTY_SOFTWARE = NodesRepositoryInterface.COLUMN_SOFTWARE
    PROPERTY_SOFTWARE_VERSION = NodesRepositoryInterface.COLUMN_SOFTWARE_VERSION

    def __init__(
        self,
        repository: NodesRepositoryInterface,
        network: NetworkNodesInterface,
        event_dispatcher: EventDispatcher,
    ):
        """
        Init Nodes domain

        :param repository: Database adapter instance
        :param network: Network adapter instance for handling nodes
        :param event_dispatcher: EventDispatcher instance
        """
        self.repository = repository
        self.network = network
        self.event_dispatcher = event_dispatcher

    def add(self, node: Node):
        """
        Add node

        :param node: Node instance
        :return:
        """
        # add account
        self.repository.add(node)

        self.event_dispatcher.dispatch_event(
            NodesEvent(NodesEvent.EVENT_TYPE_LIST_CHANGED)
        )

    def update(self, node: Node):
        """
        Update node

        :param node: Node instance
        :return:
        """
        # update only non hidden fields
        self.repository.update(node)

        self.event_dispatcher.dispatch_event(
            NodesEvent(NodesEvent.EVENT_TYPE_LIST_CHANGED)
        )

    def get(self, id: UUID) -> Optional[Node]:  # pylint: disable=redefined-builtin
        """
        Return Node instance from ID

        :param id: Node ID
        :return:
        """
        return self.repository.get(id)

    def list(
        self,
        offset: int = DEFAULT_LIST_OFFSET,
        limit: int = DEFAULT_LIST_LIMIT,
        sort_order: int = SORT_ORDER_ASCENDING,
        sort_property: str = PROPERTY_ID,
    ) -> List[Node]:
        """
        List nodes from repository

        :param offset: Offset index to get rows from
        :param limit: Number of rows to return
        :param sort_order: Sort order flag
        :param sort_property: Property flag to sort by
        :return:
        """
        return self.repository.list(
            offset,
            limit,
            sort_order,
            sort_property,
        )

    def delete(self, id: UUID) -> None:  # pylint: disable=redefined-builtin
        """
        Delete node by ID

        :param id: Node ID
        :return:
        """
        self.repository.delete(id)

        self.event_dispatcher.dispatch_event(
            NodesEvent(NodesEvent.EVENT_TYPE_LIST_CHANGED)
        )

    def count(self) -> int:
        """
        Return total node count

        :return:
        """
        return self.repository.count()

    def fetch_from_network(self) -> Optional[Node]:
        """
        Fetch Node from current EntryPoint connection

        :return:
        """
        return self.network.get()
