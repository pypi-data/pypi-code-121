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


class TranslateText(TLObject):  # type: ignore
    """Telegram API method.

    Details:
        - Layer: ``138``
        - ID: ``0x24ce6dee``

    Parameters:
        to_lang: ``str``
        peer (optional): :obj:`InputPeer <telectron.raw.base.InputPeer>`
        msg_id (optional): ``int`` ``32-bit``
        text (optional): ``str``
        from_lang (optional): ``str``

    Returns:
        :obj:`messages.TranslatedText <telectron.raw.base.messages.TranslatedText>`
    """

    __slots__: List[str] = ["to_lang", "peer", "msg_id", "text", "from_lang"]

    ID = 0x24ce6dee
    QUALNAME = "functions.messages.TranslateText"

    def __init__(self, *, to_lang: str, peer: "raw.base.InputPeer" = None, msg_id: Union[None, int] = None, text: Union[None, str] = None, from_lang: Union[None, str] = None) -> None:
        self.to_lang = to_lang  # string
        self.peer = peer  # flags.0?InputPeer
        self.msg_id = msg_id  # flags.0?int
        self.text = text  # flags.1?string
        self.from_lang = from_lang  # flags.2?string

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "TranslateText":
        flags = Int.read(b)
        
        peer = TLObject.read(b) if flags & (1 << 0) else None
        
        msg_id = Int.read(b) if flags & (1 << 0) else None
        text = String.read(b) if flags & (1 << 1) else None
        from_lang = String.read(b) if flags & (1 << 2) else None
        to_lang = String.read(b)
        
        return TranslateText(to_lang=to_lang, peer=peer, msg_id=msg_id, text=text, from_lang=from_lang)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.peer is not None else 0
        flags |= (1 << 0) if self.msg_id is not None else 0
        flags |= (1 << 1) if self.text is not None else 0
        flags |= (1 << 2) if self.from_lang is not None else 0
        b.write(Int(flags))
        
        if self.peer is not None:
            b.write(self.peer.write())
        
        if self.msg_id is not None:
            b.write(Int(self.msg_id))
        
        if self.text is not None:
            b.write(String(self.text))
        
        if self.from_lang is not None:
            b.write(String(self.from_lang))
        
        b.write(String(self.to_lang))
        
        return b.getvalue()
