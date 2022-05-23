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
from typing import Optional

from substrateinterface import ExtrinsicReceipt

from tikka.domains.entities.account import Account
from tikka.domains.entities.events import TransferEvent
from tikka.domains.events import EventDispatcher
from tikka.interfaces.adapters.network.transfers import NetworkTransfersInterface


class Transfers:
    """
    Transfers domain class
    """

    def __init__(
        self,
        network: NetworkTransfersInterface,
        event_dispatcher: EventDispatcher,
    ):
        """
        Init Transfers domain

        :param network: NetworkTransfersInterface adapter instance
        :param event_dispatcher: EventDispatcher instance
        """
        self.network = network
        self.event_dispatcher = event_dispatcher

    def fees(
        self, sender_account: Account, recipient_address: str, amount: int
    ) -> Optional[int]:
        """
        Fetch transfer fees from network and return it if request is successful

        :param sender_account: Sender Account instance
        :param recipient_address: Recipient address
        :param amount: Amount in blockchain unit
        :return:
        """
        return self.network.fees(sender_account, recipient_address, amount)

    def send(
        self, sender_account: Account, recipient_address: str, amount: int
    ) -> Optional[ExtrinsicReceipt]:
        """
        Send transfer to network and return ExtrinsicReceipt if request is successful

        :param sender_account: Sender Account instance
        :param recipient_address: Recipient address
        :param amount: Amount in blockchain unit
        :return:
        """
        receipt = self.network.send(sender_account, recipient_address, amount)

        if receipt is not None and receipt.is_success is True:
            # dispatch event
            event = TransferEvent(
                TransferEvent.EVENT_TYPE_SENT,
            )
            self.event_dispatcher.dispatch_event(event)

        return receipt
