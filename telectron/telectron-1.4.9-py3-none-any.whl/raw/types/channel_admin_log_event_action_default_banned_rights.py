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


class ChannelAdminLogEventActionDefaultBannedRights(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~telectron.raw.base.ChannelAdminLogEventAction`.

    Details:
        - Layer: ``138``
        - ID: ``0x2df5fc0a``

    Parameters:
        prev_banned_rights: :obj:`ChatBannedRights <telectron.raw.base.ChatBannedRights>`
        new_banned_rights: :obj:`ChatBannedRights <telectron.raw.base.ChatBannedRights>`
    """

    __slots__: List[str] = ["prev_banned_rights", "new_banned_rights"]

    ID = 0x2df5fc0a
    QUALNAME = "types.ChannelAdminLogEventActionDefaultBannedRights"

    def __init__(self, *, prev_banned_rights: "raw.base.ChatBannedRights", new_banned_rights: "raw.base.ChatBannedRights") -> None:
        self.prev_banned_rights = prev_banned_rights  # ChatBannedRights
        self.new_banned_rights = new_banned_rights  # ChatBannedRights

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "ChannelAdminLogEventActionDefaultBannedRights":
        # No flags
        
        prev_banned_rights = TLObject.read(b)
        
        new_banned_rights = TLObject.read(b)
        
        return ChannelAdminLogEventActionDefaultBannedRights(prev_banned_rights=prev_banned_rights, new_banned_rights=new_banned_rights)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.prev_banned_rights.write())
        
        b.write(self.new_banned_rights.write())
        
        return b.getvalue()
