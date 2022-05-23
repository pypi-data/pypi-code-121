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


class GetArchivedStickers(TLObject):  # type: ignore
    """Telegram API method.

    Details:
        - Layer: ``138``
        - ID: ``0x57f17692``

    Parameters:
        offset_id: ``int`` ``64-bit``
        limit: ``int`` ``32-bit``
        masks (optional): ``bool``

    Returns:
        :obj:`messages.ArchivedStickers <telectron.raw.base.messages.ArchivedStickers>`
    """

    __slots__: List[str] = ["offset_id", "limit", "masks"]

    ID = 0x57f17692
    QUALNAME = "functions.messages.GetArchivedStickers"

    def __init__(self, *, offset_id: int, limit: int, masks: Union[None, bool] = None) -> None:
        self.offset_id = offset_id  # long
        self.limit = limit  # int
        self.masks = masks  # flags.0?true

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "GetArchivedStickers":
        flags = Int.read(b)
        
        masks = True if flags & (1 << 0) else False
        offset_id = Long.read(b)
        
        limit = Int.read(b)
        
        return GetArchivedStickers(offset_id=offset_id, limit=limit, masks=masks)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.masks else 0
        b.write(Int(flags))
        
        b.write(Long(self.offset_id))
        
        b.write(Int(self.limit))
        
        return b.getvalue()
