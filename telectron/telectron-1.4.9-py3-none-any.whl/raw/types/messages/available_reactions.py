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


class AvailableReactions(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~telectron.raw.base.messages.AvailableReactions`.

    Details:
        - Layer: ``138``
        - ID: ``0x768e3aad``

    Parameters:
        hash: ``int`` ``32-bit``
        reactions: List of :obj:`AvailableReaction <telectron.raw.base.AvailableReaction>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetAvailableReactions <telectron.raw.functions.messages.GetAvailableReactions>`
    """

    __slots__: List[str] = ["hash", "reactions"]

    ID = 0x768e3aad
    QUALNAME = "types.messages.AvailableReactions"

    def __init__(self, *, hash: int, reactions: List["raw.base.AvailableReaction"]) -> None:
        self.hash = hash  # int
        self.reactions = reactions  # Vector<AvailableReaction>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "AvailableReactions":
        # No flags
        
        hash = Int.read(b)
        
        reactions = TLObject.read(b)
        
        return AvailableReactions(hash=hash, reactions=reactions)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Int(self.hash))
        
        b.write(Vector(self.reactions))
        
        return b.getvalue()
