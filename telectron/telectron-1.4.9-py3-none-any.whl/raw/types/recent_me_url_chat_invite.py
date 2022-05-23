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


class RecentMeUrlChatInvite(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~telectron.raw.base.RecentMeUrl`.

    Details:
        - Layer: ``138``
        - ID: ``0xeb49081d``

    Parameters:
        url: ``str``
        chat_invite: :obj:`ChatInvite <telectron.raw.base.ChatInvite>`
    """

    __slots__: List[str] = ["url", "chat_invite"]

    ID = 0xeb49081d
    QUALNAME = "types.RecentMeUrlChatInvite"

    def __init__(self, *, url: str, chat_invite: "raw.base.ChatInvite") -> None:
        self.url = url  # string
        self.chat_invite = chat_invite  # ChatInvite

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "RecentMeUrlChatInvite":
        # No flags
        
        url = String.read(b)
        
        chat_invite = TLObject.read(b)
        
        return RecentMeUrlChatInvite(url=url, chat_invite=chat_invite)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(String(self.url))
        
        b.write(self.chat_invite.write())
        
        return b.getvalue()
