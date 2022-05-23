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


class CreateGroupCall(TLObject):  # type: ignore
    """Telegram API method.

    Details:
        - Layer: ``138``
        - ID: ``0x48cdc6d8``

    Parameters:
        peer: :obj:`InputPeer <telectron.raw.base.InputPeer>`
        random_id: ``int`` ``32-bit``
        title (optional): ``str``
        schedule_date (optional): ``int`` ``32-bit``

    Returns:
        :obj:`Updates <telectron.raw.base.Updates>`
    """

    __slots__: List[str] = ["peer", "random_id", "title", "schedule_date"]

    ID = 0x48cdc6d8
    QUALNAME = "functions.phone.CreateGroupCall"

    def __init__(self, *, peer: "raw.base.InputPeer", random_id: int, title: Union[None, str] = None, schedule_date: Union[None, int] = None) -> None:
        self.peer = peer  # InputPeer
        self.random_id = random_id  # int
        self.title = title  # flags.0?string
        self.schedule_date = schedule_date  # flags.1?int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "CreateGroupCall":
        flags = Int.read(b)
        
        peer = TLObject.read(b)
        
        random_id = Int.read(b)
        
        title = String.read(b) if flags & (1 << 0) else None
        schedule_date = Int.read(b) if flags & (1 << 1) else None
        return CreateGroupCall(peer=peer, random_id=random_id, title=title, schedule_date=schedule_date)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.title is not None else 0
        flags |= (1 << 1) if self.schedule_date is not None else 0
        b.write(Int(flags))
        
        b.write(self.peer.write())
        
        b.write(Int(self.random_id))
        
        if self.title is not None:
            b.write(String(self.title))
        
        if self.schedule_date is not None:
            b.write(Int(self.schedule_date))
        
        return b.getvalue()
