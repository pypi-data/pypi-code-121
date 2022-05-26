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

from tikka.adapters.network.nodes import NetworkNodes
from tikka.adapters.network.rpc.connection import RPCConnection
from tikka.domains.config import Config
from tikka.domains.connections import Connections
from tikka.domains.currencies import Currencies
from tikka.domains.entities.entry_point import EntryPoint
from tikka.domains.entities.events import ConnectionsEvent
from tikka.domains.entities.node import Node
from tikka.domains.events import EventDispatcher
from tikka.domains.nodes import Nodes
from tikka.interfaces.adapters.repository.entry_points import (
    EntryPointsRepositoryInterface,
)
from tikka.interfaces.adapters.repository.preferences import (
    CURRENT_ENTRY_POINT_URL,
    PreferencesRepositoryInterface,
)


class EntryPoints:
    """
    EntryPoints domain class
    """

    DEFAULT_LIST_OFFSET = 0
    DEFAULT_LIST_LIMIT = 1000

    SORT_ORDER_ASCENDING = EntryPointsRepositoryInterface.SORT_ORDER_ASCENDING
    SORT_ORDER_DESCENDING = EntryPointsRepositoryInterface.SORT_ORDER_DESCENDING

    PROPERTY_URL = EntryPointsRepositoryInterface.COLUMN_URL
    PROPERTY_NODE_ID = EntryPointsRepositoryInterface.COLUMN_NODE_ID

    def __init__(
        self,
        repository: EntryPointsRepositoryInterface,
        preferences_repository: PreferencesRepositoryInterface,
        connections: Connections,
        nodes: Nodes,
        config: Config,
        currencies: Currencies,
        event_dispatcher: EventDispatcher,
    ):
        """
        Init EntryPoints domain instance

        :param repository: EntryPointsRepositoryInterface instance
        :param preferences_repository: PreferencesRepositoryInterface instance
        :param connections: Connections instance
        :param nodes: Nodes instance
        :param config: Config instance
        :param currencies: Currencies instance
        :param event_dispatcher: EventDispatcher instance
        """
        self.repository = repository
        self.preferences_repository = preferences_repository
        self.connections = connections
        self.nodes = nodes
        self.config = config
        self.currencies = currencies
        self.event_dispatcher = event_dispatcher
        self.current_url = self.currencies.get_entry_point_urls()[0]

        self.init_repository()

        # events
        self.event_dispatcher.add_event_listener(
            ConnectionsEvent.EVENT_TYPE_CONNECTED, self._on_connections_connected
        )

    def init_repository(self):
        """
        Init repository with default entry points from config

        :return:
        """
        # init repository with config default entry points
        if len(self.repository.list()) == 0:
            for url in self.currencies.get_entry_point_urls():
                self.repository.add(EntryPoint(url))

        self.current_url = self.repository.list(0, 1)[0].url

        current_url_in_preferences = self.preferences_repository.get(
            CURRENT_ENTRY_POINT_URL
        )
        if current_url_in_preferences is None:
            self.preferences_repository.set(CURRENT_ENTRY_POINT_URL, self.current_url)
        else:
            self.current_url = current_url_in_preferences

    def network_fetch_current_node(self) -> None:
        """
        Add or update node from current entry point

        :return:
        """
        node = self.nodes.fetch_from_network()
        if node is None:
            return None
        entry_point = self.get(self.get_current_url())
        if entry_point is None:
            return None
        if entry_point.node_id is None:
            self.nodes.add(node)
            entry_point.node_id = node.id
            self.repository.update(entry_point)
        else:
            node.id = entry_point.node_id
            self.nodes.update(node)

        return None

    @staticmethod
    def network_test_and_get_node(url: str) -> Optional[Node]:
        """
        Try to open connection on url and return node if successful

        Then close connection

        :param url: Entry point url
        :return:
        """
        node = None

        connections = Connections(RPCConnection(), EventDispatcher())
        connections.connect(EntryPoint(url))
        if connections.is_connected():
            network_nodes = NetworkNodes(connections)
            node = network_nodes.get()
        connections.disconnect()

        return node

    def add(self, entry_point: EntryPoint) -> None:
        """
        Add entry point to list

        :param entry_point: EntryPoint instance
        :return:
        """
        self.repository.add(entry_point)

    def get(self, url: str) -> Optional[EntryPoint]:
        """
        Get entry point instance by url

        :param url: Url
        :return:
        """
        return self.repository.get(url)

    def update(self, entry_point: EntryPoint) -> None:
        """
        Update entry point in list

        :param entry_point: EntryPoint instance
        :return:
        """
        self.repository.update(entry_point)

    def list(
        self,
        offset: int = DEFAULT_LIST_OFFSET,
        limit: int = DEFAULT_LIST_LIMIT,
        sort_order: int = SORT_ORDER_ASCENDING,
        sort_property: str = PROPERTY_URL,
        node_id: UUID = None,
    ) -> List[EntryPoint]:
        """
        List entry points from repository

        :param offset: Offset index to get rows from
        :param limit: Number of rows to return
        :param sort_order: Sort order flag
        :param sort_property: Property flag to sort by
        :param node_id: Filter by node ID
        :return:
        """
        return self.repository.list(offset, limit, sort_order, sort_property, node_id)

    def delete(self, url: str) -> None:
        """
        Delete entry point from list

        :param url: Url of entry point
        :return:
        """
        # do not delete default entry points from config
        if url not in self.currencies.get_entry_point_urls():
            self.repository.delete(url)
            # switch current entry point to first in list
            self.set_current_url(self.repository.list(0, 1)[0].url)
            # set new entry point in preferences
            self.preferences_repository.set(
                CURRENT_ENTRY_POINT_URL, self.get_current_url()
            )
            entry_point = self.get(url)
            if entry_point is not None and entry_point.node_id is not None:
                self.nodes.delete(entry_point.node_id)

    def get_current_url(self) -> str:
        """
        Return current entry point url

        :return:
        """
        return self.current_url

    def set_current_url(self, url: str) -> None:
        """
        Set current entry point url

        :return:
        """
        self.current_url = url
        # update preference
        self.preferences_repository.set(
            CURRENT_ENTRY_POINT_URL,
            self.current_url,
        )
        # switch current connection
        self.connections.disconnect()
        entry_point = self.get(self.current_url)
        if entry_point is not None:
            self.connections.connect(entry_point)
            self.network_fetch_current_node()

    def _on_connections_connected(self, _: ConnectionsEvent):
        """
        Triggered when the connection is established

        :param _:
        :return:
        """
        self.network_fetch_current_node()
