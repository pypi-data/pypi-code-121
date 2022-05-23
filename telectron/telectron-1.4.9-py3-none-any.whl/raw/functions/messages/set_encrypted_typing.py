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


class SetEncryptedTyping(TLObject):  # type: ignore
    """Telegram API method.

    Details:
        - Layer: ``138``
        - ID: ``0x791451ed``

    Parameters:
        peer: :obj:`InputEncryptedChat <telectron.raw.base.InputEncryptedChat>`
        typing: ``bool``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["peer", "typing"]

    ID = 0x791451ed
    QUALNAME = "functions.messages.SetEncryptedTyping"

    def __init__(self, *, peer: "raw.base.InputEncryptedChat", typing: bool) -> None:
        self.peer = peer  # InputEncryptedChat
        self.typing = typing  # Bool

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "SetEncryptedTyping":
        # No flags
        
        peer = TLObject.read(b)
        
        typing = Bool.read(b)
        
        return SetEncryptedTyping(peer=peer, typing=typing)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.peer.write())
        
        b.write(Bool(self.typing))
        
        return b.getvalue()
