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
import uuid
from typing import Optional

from tikka.domains.entities.node import Node
from tikka.interfaces.adapters.network.nodes import NetworkNodesInterface


class NetworkNodes(NetworkNodesInterface):
    """
    NetworkNodes class
    """

    def get(self) -> Optional[Node]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NetworkNodesInterface.get.__doc__
        )
        if not self.connections.is_connected():
            return None
        if self.connections.rpc.client is None:
            return None

        try:
            peer_id = self.connections.rpc.client.rpc_request(
                "system_localPeerId", []
            ).get("result")
        except Exception as exception:
            logging.exception(exception)
            return None

        try:
            current_block = self.connections.rpc.client.rpc_request(
                "system_syncState", []
            ).get("result")["currentBlock"]
        except Exception as exception:
            logging.exception(exception)
            return None

        return Node(
            uuid.uuid4(),
            peer_id=peer_id,
            block=current_block,
            software=self.connections.rpc.client.name,
            software_version=self.connections.rpc.client.version,
        )
