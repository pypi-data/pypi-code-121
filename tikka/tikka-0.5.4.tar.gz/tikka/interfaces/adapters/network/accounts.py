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

from tikka.interfaces.domains.connections import ConnectionsInterface


class NetworkAccountsInterface(abc.ABC):
    """
    NetworkAccountsInterface class
    """

    def __init__(self, connections: ConnectionsInterface) -> None:
        """
        Use connections to request account informations

        :param connections: ConnectionsInterface instance
        :return:
        """
        self.connections = connections

    @abc.abstractmethod
    def get_balance(self, address: str) -> Optional[int]:
        """
        Return the account balance for address

        :param address: Account address
        :return:
        """
        raise NotImplementedError
