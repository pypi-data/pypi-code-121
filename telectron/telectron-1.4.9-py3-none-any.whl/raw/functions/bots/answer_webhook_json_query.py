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


class AnswerWebhookJSONQuery(TLObject):  # type: ignore
    """Telegram API method.

    Details:
        - Layer: ``138``
        - ID: ``0xe6213f4d``

    Parameters:
        query_id: ``int`` ``64-bit``
        data: :obj:`DataJSON <telectron.raw.base.DataJSON>`

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["query_id", "data"]

    ID = 0xe6213f4d
    QUALNAME = "functions.bots.AnswerWebhookJSONQuery"

    def __init__(self, *, query_id: int, data: "raw.base.DataJSON") -> None:
        self.query_id = query_id  # long
        self.data = data  # DataJSON

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "AnswerWebhookJSONQuery":
        # No flags
        
        query_id = Long.read(b)
        
        data = TLObject.read(b)
        
        return AnswerWebhookJSONQuery(query_id=query_id, data=data)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Long(self.query_id))
        
        b.write(self.data.write())
        
        return b.getvalue()
