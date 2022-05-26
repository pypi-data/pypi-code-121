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

from tikka.domains.entities.node import Node
from tikka.interfaces.domains.connections import ConnectionsInterface


class NetworkNodesInterface(abc.ABC):
    """
    NetworkNodesInterface class
    """

    def __init__(self, connections: ConnectionsInterface) -> None:
        """
        Init NetworkNodesInterface instance with ConnectionsInterface instance

        :param connections: ConnectionsInterface instance
        :return:
        """
        self.connections = connections

    @abc.abstractmethod
    def get(self) -> Optional[Node]:
        """
        Return the node instance from first suitable connection

        :return:
        """
        raise NotImplementedError
