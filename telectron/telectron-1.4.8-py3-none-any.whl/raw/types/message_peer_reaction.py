#  telectron - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-2021 Dan <https://github.com/delivrance>
#
#  This file is part of telectron.
#
#  telectron is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  telectron is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with telectron.  If not, see <http://www.gnu.org/licenses/>.

from io import BytesIO

from telectron.raw.core.primitives import Int, Long, Int128, Int256, Bool, Bytes, String, Double, Vector
from telectron.raw.core import TLObject
from telectron import raw
from typing import List, Union, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


class MessagePeerReaction(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~telectron.raw.base.MessagePeerReaction`.

    Details:
        - Layer: ``138``
        - ID: ``0x51b67eff``

    Parameters:
        peer_id: :obj:`Peer <telectron.raw.base.Peer>`
        reaction: ``str``
        big (optional): ``bool``
        unread (optional): ``bool``
    """

    __slots__: List[str] = ["peer_id", "reaction", "big", "unread"]

    ID = 0x51b67eff
    QUALNAME = "types.MessagePeerReaction"

    def __init__(self, *, peer_id: "raw.base.Peer", reaction: str, big: Union[None, bool] = None, unread: Union[None, bool] = None) -> None:
        self.peer_id = peer_id  # Peer
        self.reaction = reaction  # string
        self.big = big  # flags.0?true
        self.unread = unread  # flags.1?true

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "MessagePeerReaction":
        flags = Int.read(b)
        
        big = True if flags & (1 << 0) else False
        unread = True if flags & (1 << 1) else False
        peer_id = TLObject.read(b)
        
        reaction = String.read(b)
        
        return MessagePeerReaction(peer_id=peer_id, reaction=reaction, big=big, unread=unread)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.big else 0
        flags |= (1 << 1) if self.unread else 0
        b.write(Int(flags))
        
        b.write(self.peer_id.write())
        
        b.write(String(self.reaction))
        
        return b.getvalue()
