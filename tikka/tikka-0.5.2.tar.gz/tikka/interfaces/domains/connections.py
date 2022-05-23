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

from tikka.adapters.network.rpc.connection import RPCConnection
from tikka.domains.entities.entry_point import EntryPoint
from tikka.domains.events import EventDispatcher


class ConnectionsInterface(abc.ABC):
    """
    ConnectionsInterface class
    """

    def __init__(self, rpc: RPCConnection, event_dispatcher: EventDispatcher) -> None:
        """
        Init Connections instance with dependencies

        :param rpc: RPCConnection instance
        :param event_dispatcher: EventDispatcher instance
        """
        self.rpc = rpc
        self.event_dispatcher = event_dispatcher

    @abc.abstractmethod
    def connect(self, entry_point: EntryPoint) -> None:
        """
        Connect all connections

        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def disconnect(self):
        """
        Disconnect all connections

        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def is_connected(self) -> bool:
        """
        Return True if connection is active, False otherwise

        :return:
        """
        raise NotImplementedError
