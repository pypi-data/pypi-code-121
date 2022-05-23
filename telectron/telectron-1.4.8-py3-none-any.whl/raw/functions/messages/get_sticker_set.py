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


class GetStickerSet(TLObject):  # type: ignore
    """Telegram API method.

    Details:
        - Layer: ``138``
        - ID: ``0xc8a0ec74``

    Parameters:
        stickerset: :obj:`InputStickerSet <telectron.raw.base.InputStickerSet>`
        hash: ``int`` ``32-bit``

    Returns:
        :obj:`messages.StickerSet <telectron.raw.base.messages.StickerSet>`
    """

    __slots__: List[str] = ["stickerset", "hash"]

    ID = 0xc8a0ec74
    QUALNAME = "functions.messages.GetStickerSet"

    def __init__(self, *, stickerset: "raw.base.InputStickerSet", hash: int) -> None:
        self.stickerset = stickerset  # InputStickerSet
        self.hash = hash  # int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "GetStickerSet":
        # No flags
        
        stickerset = TLObject.read(b)
        
        hash = Int.read(b)
        
        return GetStickerSet(stickerset=stickerset, hash=hash)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.stickerset.write())
        
        b.write(Int(self.hash))
        
        return b.getvalue()
