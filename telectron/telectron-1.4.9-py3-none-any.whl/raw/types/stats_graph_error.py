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


class StatsGraphError(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~telectron.raw.base.StatsGraph`.

    Details:
        - Layer: ``138``
        - ID: ``0xbedc9822``

    Parameters:
        error: ``str``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`stats.LoadAsyncGraph <telectron.raw.functions.stats.LoadAsyncGraph>`
    """

    __slots__: List[str] = ["error"]

    ID = 0xbedc9822
    QUALNAME = "types.StatsGraphError"

    def __init__(self, *, error: str) -> None:
        self.error = error  # string

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "StatsGraphError":
        # No flags
        
        error = String.read(b)
        
        return StatsGraphError(error=error)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(String(self.error))
        
        return b.getvalue()
