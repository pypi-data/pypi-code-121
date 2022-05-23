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


class ConfigSimple(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~telectron.raw.base.help.ConfigSimple`.

    Details:
        - Layer: ``138``
        - ID: ``0x5a592a6c``

    Parameters:
        date: ``int`` ``32-bit``
        expires: ``int`` ``32-bit``
        rules: List of :obj:`AccessPointRule <telectron.raw.base.AccessPointRule>`
    """

    __slots__: List[str] = ["date", "expires", "rules"]

    ID = 0x5a592a6c
    QUALNAME = "types.help.ConfigSimple"

    def __init__(self, *, date: int, expires: int, rules: List["raw.base.AccessPointRule"]) -> None:
        self.date = date  # int
        self.expires = expires  # int
        self.rules = rules  # vector<AccessPointRule>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "ConfigSimple":
        # No flags
        
        date = Int.read(b)
        
        expires = Int.read(b)
        
        rules = TLObject.read(b)
        
        return ConfigSimple(date=date, expires=expires, rules=rules)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Int(self.date))
        
        b.write(Int(self.expires))
        
        b.write(Vector(self.rules))
        
        return b.getvalue()
