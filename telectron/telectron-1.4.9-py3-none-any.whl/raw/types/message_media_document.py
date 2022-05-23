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


class MessageMediaDocument(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~telectron.raw.base.MessageMedia`.

    Details:
        - Layer: ``138``
        - ID: ``0x9cb070d7``

    Parameters:
        document (optional): :obj:`Document <telectron.raw.base.Document>`
        ttl_seconds (optional): ``int`` ``32-bit``

    See Also:
        This object can be returned by 3 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetWebPagePreview <telectron.raw.functions.messages.GetWebPagePreview>`
            - :obj:`messages.UploadMedia <telectron.raw.functions.messages.UploadMedia>`
            - :obj:`messages.UploadImportedMedia <telectron.raw.functions.messages.UploadImportedMedia>`
    """

    __slots__: List[str] = ["document", "ttl_seconds"]

    ID = 0x9cb070d7
    QUALNAME = "types.MessageMediaDocument"

    def __init__(self, *, document: "raw.base.Document" = None, ttl_seconds: Union[None, int] = None) -> None:
        self.document = document  # flags.0?Document
        self.ttl_seconds = ttl_seconds  # flags.2?int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "MessageMediaDocument":
        flags = Int.read(b)
        
        document = TLObject.read(b) if flags & (1 << 0) else None
        
        ttl_seconds = Int.read(b) if flags & (1 << 2) else None
        return MessageMediaDocument(document=document, ttl_seconds=ttl_seconds)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.document is not None else 0
        flags |= (1 << 2) if self.ttl_seconds is not None else 0
        b.write(Int(flags))
        
        if self.document is not None:
            b.write(self.document.write())
        
        if self.ttl_seconds is not None:
            b.write(Int(self.ttl_seconds))
        
        return b.getvalue()
