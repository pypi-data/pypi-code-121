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


class UserInfo(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~telectron.raw.base.help.UserInfo`.

    Details:
        - Layer: ``138``
        - ID: ``0x1eb3758``

    Parameters:
        message: ``str``
        entities: List of :obj:`MessageEntity <telectron.raw.base.MessageEntity>`
        author: ``str``
        date: ``int`` ``32-bit``

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`help.GetUserInfo <telectron.raw.functions.help.GetUserInfo>`
            - :obj:`help.EditUserInfo <telectron.raw.functions.help.EditUserInfo>`
    """

    __slots__: List[str] = ["message", "entities", "author", "date"]

    ID = 0x1eb3758
    QUALNAME = "types.help.UserInfo"

    def __init__(self, *, message: str, entities: List["raw.base.MessageEntity"], author: str, date: int) -> None:
        self.message = message  # string
        self.entities = entities  # Vector<MessageEntity>
        self.author = author  # string
        self.date = date  # int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "UserInfo":
        # No flags
        
        message = String.read(b)
        
        entities = TLObject.read(b)
        
        author = String.read(b)
        
        date = Int.read(b)
        
        return UserInfo(message=message, entities=entities, author=author, date=date)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(String(self.message))
        
        b.write(Vector(self.entities))
        
        b.write(String(self.author))
        
        b.write(Int(self.date))
        
        return b.getvalue()
