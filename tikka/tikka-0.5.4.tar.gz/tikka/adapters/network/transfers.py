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
import logging
from typing import Optional

from substrateinterface import ExtrinsicReceipt
from substrateinterface.exceptions import SubstrateRequestException

from tikka.domains.entities.account import Account
from tikka.interfaces.adapters.network.transfers import NetworkTransfersInterface


class NetworkTransfers(NetworkTransfersInterface):
    """
    NetworkTransfers class
    """

    def send(
        self, sender_account: Account, recipient_address: str, amount: int
    ) -> Optional[ExtrinsicReceipt]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NetworkTransfersInterface.send.__doc__
        )
        if not self.connections.is_connected():
            return None
        if self.connections.rpc.client is None:
            return None
        if sender_account.keypair is None:
            logging.error("NetworkTransfers.send: sender_account.keypair is None!")
            return None

        params = {"dest": recipient_address, "value": amount}
        call = self.connections.rpc.client.compose_call(
            call_module="Balances",
            call_function="transfer",
            call_params=params,
        )

        # Get payment info
        payment_info = self.connections.rpc.client.get_payment_info(
            call=call, keypair=sender_account.keypair
        )

        print("Payment info: ", payment_info)

        extrinsic = self.connections.rpc.client.create_signed_extrinsic(
            call=call, keypair=sender_account.keypair
        )

        try:
            # fixme: code stuck infinitely if no blocks are created on blockchain
            #       should have a timeout option
            receipt = self.connections.rpc.client.submit_extrinsic(
                extrinsic, wait_for_inclusion=True
            )
            logging.debug(
                "Extrinsic '%s' sent and included in block '%s'",
                receipt.extrinsic_hash,
                receipt.block_hash,
            )
        except SubstrateRequestException as exception:
            logging.exception(exception)
            return None

        if receipt.is_success is False:
            logging.error(receipt.error_message)

        return receipt

    def fees(
        self, sender_account: Account, recipient_address: str, amount: int
    ) -> Optional[int]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NetworkTransfersInterface.send.__doc__
        )
        if not self.connections.is_connected():
            return None
        if self.connections.rpc.client is None:
            return None
        if sender_account.keypair is None:
            logging.error("NetworkTransfers.fees: sender_account.keypair is None!")
            return None

        params = {"dest": recipient_address, "value": amount}
        call = self.connections.rpc.client.compose_call(
            call_module="Balances",
            call_function="transfer",
            call_params=params,
        )

        try:
            # Get payment info
            payment_info = self.connections.rpc.client.get_payment_info(
                call=call, keypair=sender_account.keypair
            )
        except SubstrateRequestException as exception:
            logging.exception(exception)
            return None

        if payment_info is None:
            return None

        print("Payment info: ", payment_info)
        return payment_info["partialFee"]
