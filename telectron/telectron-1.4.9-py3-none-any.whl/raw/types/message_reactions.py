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


class MessageReactions(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~telectron.raw.base.MessageReactions`.

    Details:
        - Layer: ``138``
        - ID: ``0x4f2b9479``

    Parameters:
        results: List of :obj:`ReactionCount <telectron.raw.base.ReactionCount>`
        min (optional): ``bool``
        can_see_list (optional): ``bool``
        recent_reactions (optional): List of :obj:`MessagePeerReaction <telectron.raw.base.MessagePeerReaction>`
    """

    __slots__: List[str] = ["results", "min", "can_see_list", "recent_reactions"]

    ID = 0x4f2b9479
    QUALNAME = "types.MessageReactions"

    def __init__(self, *, results: List["raw.base.ReactionCount"], min: Union[None, bool] = None, can_see_list: Union[None, bool] = None, recent_reactions: Union[None, List["raw.base.MessagePeerReaction"]] = None) -> None:
        self.results = results  # Vector<ReactionCount>
        self.min = min  # flags.0?true
        self.can_see_list = can_see_list  # flags.2?true
        self.recent_reactions = recent_reactions  # flags.1?Vector<MessagePeerReaction>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "MessageReactions":
        flags = Int.read(b)
        
        min = True if flags & (1 << 0) else False
        can_see_list = True if flags & (1 << 2) else False
        results = TLObject.read(b)
        
        recent_reactions = TLObject.read(b) if flags & (1 << 1) else []
        
        return MessageReactions(results=results, min=min, can_see_list=can_see_list, recent_reactions=recent_reactions)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.min else 0
        flags |= (1 << 2) if self.can_see_list else 0
        flags |= (1 << 1) if self.recent_reactions else 0
        b.write(Int(flags))
        
        b.write(Vector(self.results))
        
        if self.recent_reactions:
            b.write(Vector(self.recent_reactions))
        
        return b.getvalue()
