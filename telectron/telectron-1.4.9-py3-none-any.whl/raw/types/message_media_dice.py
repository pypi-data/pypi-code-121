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


class MessageMediaDice(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~telectron.raw.base.MessageMedia`.

    Details:
        - Layer: ``138``
        - ID: ``0x3f7ee58b``

    Parameters:
        value: ``int`` ``32-bit``
        emoticon: ``str``

    See Also:
        This object can be returned by 3 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetWebPagePreview <telectron.raw.functions.messages.GetWebPagePreview>`
            - :obj:`messages.UploadMedia <telectron.raw.functions.messages.UploadMedia>`
            - :obj:`messages.UploadImportedMedia <telectron.raw.functions.messages.UploadImportedMedia>`
    """

    __slots__: List[str] = ["value", "emoticon"]

    ID = 0x3f7ee58b
    QUALNAME = "types.MessageMediaDice"

    def __init__(self, *, value: int, emoticon: str) -> None:
        self.value = value  # int
        self.emoticon = emoticon  # string

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "MessageMediaDice":
        # No flags
        
        value = Int.read(b)
        
        emoticon = String.read(b)
        
        return MessageMediaDice(value=value, emoticon=emoticon)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Int(self.value))
        
        b.write(String(self.emoticon))
        
        return b.getvalue()
