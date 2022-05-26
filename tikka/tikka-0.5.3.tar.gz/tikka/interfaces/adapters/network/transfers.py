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

from substrateinterface import ExtrinsicReceipt

from tikka.domains.entities.account import Account
from tikka.interfaces.domains.connections import ConnectionsInterface


class NetworkTransfersInterface(abc.ABC):
    """
    NetworkTransfersInterface class
    """

    def __init__(self, connections: ConnectionsInterface) -> None:
        """
        Use connections to make transfers

        :param connections: ConnectionsInterface instance
        :return:
        """
        self.connections = connections

    @abc.abstractmethod
    def fees(
        self, sender_account: Account, recipient_address: str, amount: int
    ) -> Optional[int]:
        """
        Fetch transfer fees and return it

        :param sender_account: Sender account
        :param recipient_address: Recipient address
        :param amount: Amount in blockchain units
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def send(
        self, sender_account: Account, recipient_address: str, amount: int
    ) -> Optional[ExtrinsicReceipt]:
        """
        Send amount (blockchain unit) from sender_account to recipient_address
        wait for extrinsic finalization and return ExtrinsicReceipt

        :param sender_account: Sender account
        :param recipient_address: Recipient address
        :param amount: Amount in blockchain units
        :return:
        """
        raise NotImplementedError
