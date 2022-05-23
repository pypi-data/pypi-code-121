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


class MessagesSlice(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~telectron.raw.base.messages.Messages`.

    Details:
        - Layer: ``138``
        - ID: ``0x3a54685e``

    Parameters:
        count: ``int`` ``32-bit``
        messages: List of :obj:`Message <telectron.raw.base.Message>`
        chats: List of :obj:`Chat <telectron.raw.base.Chat>`
        users: List of :obj:`User <telectron.raw.base.User>`
        inexact (optional): ``bool``
        next_rate (optional): ``int`` ``32-bit``
        offset_id_offset (optional): ``int`` ``32-bit``

    See Also:
        This object can be returned by 12 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetMessages <telectron.raw.functions.messages.GetMessages>`
            - :obj:`messages.GetHistory <telectron.raw.functions.messages.GetHistory>`
            - :obj:`messages.Search <telectron.raw.functions.messages.Search>`
            - :obj:`messages.SearchGlobal <telectron.raw.functions.messages.SearchGlobal>`
            - :obj:`messages.GetUnreadMentions <telectron.raw.functions.messages.GetUnreadMentions>`
            - :obj:`messages.GetRecentLocations <telectron.raw.functions.messages.GetRecentLocations>`
            - :obj:`messages.GetScheduledHistory <telectron.raw.functions.messages.GetScheduledHistory>`
            - :obj:`messages.GetScheduledMessages <telectron.raw.functions.messages.GetScheduledMessages>`
            - :obj:`messages.GetReplies <telectron.raw.functions.messages.GetReplies>`
            - :obj:`messages.GetUnreadReactions <telectron.raw.functions.messages.GetUnreadReactions>`
            - :obj:`channels.GetMessages <telectron.raw.functions.channels.GetMessages>`
            - :obj:`stats.GetMessagePublicForwards <telectron.raw.functions.stats.GetMessagePublicForwards>`
    """

    __slots__: List[str] = ["count", "messages", "chats", "users", "inexact", "next_rate", "offset_id_offset"]

    ID = 0x3a54685e
    QUALNAME = "types.messages.MessagesSlice"

    def __init__(self, *, count: int, messages: List["raw.base.Message"], chats: List["raw.base.Chat"], users: List["raw.base.User"], inexact: Union[None, bool] = None, next_rate: Union[None, int] = None, offset_id_offset: Union[None, int] = None) -> None:
        self.count = count  # int
        self.messages = messages  # Vector<Message>
        self.chats = chats  # Vector<Chat>
        self.users = users  # Vector<User>
        self.inexact = inexact  # flags.1?true
        self.next_rate = next_rate  # flags.0?int
        self.offset_id_offset = offset_id_offset  # flags.2?int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "MessagesSlice":
        flags = Int.read(b)
        
        inexact = True if flags & (1 << 1) else False
        count = Int.read(b)
        
        next_rate = Int.read(b) if flags & (1 << 0) else None
        offset_id_offset = Int.read(b) if flags & (1 << 2) else None
        messages = TLObject.read(b)
        
        chats = TLObject.read(b)
        
        users = TLObject.read(b)
        
        return MessagesSlice(count=count, messages=messages, chats=chats, users=users, inexact=inexact, next_rate=next_rate, offset_id_offset=offset_id_offset)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 1) if self.inexact else 0
        flags |= (1 << 0) if self.next_rate is not None else 0
        flags |= (1 << 2) if self.offset_id_offset is not None else 0
        b.write(Int(flags))
        
        b.write(Int(self.count))
        
        if self.next_rate is not None:
            b.write(Int(self.next_rate))
        
        if self.offset_id_offset is not None:
            b.write(Int(self.offset_id_offset))
        
        b.write(Vector(self.messages))
        
        b.write(Vector(self.chats))
        
        b.write(Vector(self.users))
        
        return b.getvalue()
