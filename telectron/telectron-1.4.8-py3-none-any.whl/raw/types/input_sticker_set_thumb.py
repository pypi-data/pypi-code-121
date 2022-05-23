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


class InputStickerSetThumb(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~telectron.raw.base.InputFileLocation`.

    Details:
        - Layer: ``138``
        - ID: ``0x9d84f3db``

    Parameters:
        stickerset: :obj:`InputStickerSet <telectron.raw.base.InputStickerSet>`
        thumb_version: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["stickerset", "thumb_version"]

    ID = 0x9d84f3db
    QUALNAME = "types.InputStickerSetThumb"

    def __init__(self, *, stickerset: "raw.base.InputStickerSet", thumb_version: int) -> None:
        self.stickerset = stickerset  # InputStickerSet
        self.thumb_version = thumb_version  # int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "InputStickerSetThumb":
        # No flags
        
        stickerset = TLObject.read(b)
        
        thumb_version = Int.read(b)
        
        return InputStickerSetThumb(stickerset=stickerset, thumb_version=thumb_version)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.stickerset.write())
        
        b.write(Int(self.thumb_version))
        
        return b.getvalue()
