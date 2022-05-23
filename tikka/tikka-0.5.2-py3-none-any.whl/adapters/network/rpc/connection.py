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

from substrateinterface import SubstrateInterface

from tikka.domains.entities.entry_point import EntryPoint
from tikka.interfaces.adapters.network.connection import ConnectionInterface


class RPCConnection(ConnectionInterface):
    """
    RPCConnection class
    """

    def __init__(self) -> None:
        """
        Init RPCConnection instance

        RPC client is available in self.client after connect()
        """
        self.client: Optional[SubstrateInterface] = None

    def connect(self, entry_point: EntryPoint) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            ConnectionInterface.connect.__doc__
        )
        try:
            # fixme:    use type_registry_preset='default' to fix error on Type MultiAddress
            #           https://github.com/polkascan/py-substrate-interface/issues/110
            self.client = SubstrateInterface(
                url=entry_point.url, type_registry_preset="default"
            )
        except Exception as e:
            self.client = None
            logging.exception(e)

    def disconnect(self) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            ConnectionInterface.disconnect.__doc__
        )
        if self.client is not None:
            self.client.close()
            self.client = None

    def is_connected(self) -> bool:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            ConnectionInterface.is_connected.__doc__
        )
        return self.client is not None
