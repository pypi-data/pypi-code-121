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


class Messages(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~telectron.raw.base.messages.Messages`.

    Details:
        - Layer: ``138``
        - ID: ``0x8c718e87``

    Parameters:
        messages: List of :obj:`Message <telectron.raw.base.Message>`
        chats: List of :obj:`Chat <telectron.raw.base.Chat>`
        users: List of :obj:`User <telectron.raw.base.User>`

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

    __slots__: List[str] = ["messages", "chats", "users"]

    ID = 0x8c718e87
    QUALNAME = "types.messages.Messages"

    def __init__(self, *, messages: List["raw.base.Message"], chats: List["raw.base.Chat"], users: List["raw.base.User"]) -> None:
        self.messages = messages  # Vector<Message>
        self.chats = chats  # Vector<Chat>
        self.users = users  # Vector<User>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "Messages":
        # No flags
        
        messages = TLObject.read(b)
        
        chats = TLObject.read(b)
        
        users = TLObject.read(b)
        
        return Messages(messages=messages, chats=chats, users=users)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Vector(self.messages))
        
        b.write(Vector(self.chats))
        
        b.write(Vector(self.users))
        
        return b.getvalue()
