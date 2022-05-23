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


class InputMessagesFilterPhoneCalls(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~telectron.raw.base.MessagesFilter`.

    Details:
        - Layer: ``138``
        - ID: ``0x80c99768``

    Parameters:
        missed (optional): ``bool``
    """

    __slots__: List[str] = ["missed"]

    ID = 0x80c99768
    QUALNAME = "types.InputMessagesFilterPhoneCalls"

    def __init__(self, *, missed: Union[None, bool] = None) -> None:
        self.missed = missed  # flags.0?true

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "InputMessagesFilterPhoneCalls":
        flags = Int.read(b)
        
        missed = True if flags & (1 << 0) else False
        return InputMessagesFilterPhoneCalls(missed=missed)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.missed else 0
        b.write(Int(flags))
        
        return b.getvalue()
