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


class ChatAdminsWithInvites(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~telectron.raw.base.messages.ChatAdminsWithInvites`.

    Details:
        - Layer: ``138``
        - ID: ``0xb69b72d7``

    Parameters:
        admins: List of :obj:`ChatAdminWithInvites <telectron.raw.base.ChatAdminWithInvites>`
        users: List of :obj:`User <telectron.raw.base.User>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetAdminsWithInvites <telectron.raw.functions.messages.GetAdminsWithInvites>`
    """

    __slots__: List[str] = ["admins", "users"]

    ID = 0xb69b72d7
    QUALNAME = "types.messages.ChatAdminsWithInvites"

    def __init__(self, *, admins: List["raw.base.ChatAdminWithInvites"], users: List["raw.base.User"]) -> None:
        self.admins = admins  # Vector<ChatAdminWithInvites>
        self.users = users  # Vector<User>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "ChatAdminsWithInvites":
        # No flags
        
        admins = TLObject.read(b)
        
        users = TLObject.read(b)
        
        return ChatAdminsWithInvites(admins=admins, users=users)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Vector(self.admins))
        
        b.write(Vector(self.users))
        
        return b.getvalue()
