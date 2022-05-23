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


class BotInlineMessageMediaInvoice(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~telectron.raw.base.BotInlineMessage`.

    Details:
        - Layer: ``138``
        - ID: ``0x354a9b09``

    Parameters:
        title: ``str``
        description: ``str``
        currency: ``str``
        total_amount: ``int`` ``64-bit``
        shipping_address_requested (optional): ``bool``
        test (optional): ``bool``
        photo (optional): :obj:`WebDocument <telectron.raw.base.WebDocument>`
        reply_markup (optional): :obj:`ReplyMarkup <telectron.raw.base.ReplyMarkup>`
    """

    __slots__: List[str] = ["title", "description", "currency", "total_amount", "shipping_address_requested", "test", "photo", "reply_markup"]

    ID = 0x354a9b09
    QUALNAME = "types.BotInlineMessageMediaInvoice"

    def __init__(self, *, title: str, description: str, currency: str, total_amount: int, shipping_address_requested: Union[None, bool] = None, test: Union[None, bool] = None, photo: "raw.base.WebDocument" = None, reply_markup: "raw.base.ReplyMarkup" = None) -> None:
        self.title = title  # string
        self.description = description  # string
        self.currency = currency  # string
        self.total_amount = total_amount  # long
        self.shipping_address_requested = shipping_address_requested  # flags.1?true
        self.test = test  # flags.3?true
        self.photo = photo  # flags.0?WebDocument
        self.reply_markup = reply_markup  # flags.2?ReplyMarkup

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "BotInlineMessageMediaInvoice":
        flags = Int.read(b)
        
        shipping_address_requested = True if flags & (1 << 1) else False
        test = True if flags & (1 << 3) else False
        title = String.read(b)
        
        description = String.read(b)
        
        photo = TLObject.read(b) if flags & (1 << 0) else None
        
        currency = String.read(b)
        
        total_amount = Long.read(b)
        
        reply_markup = TLObject.read(b) if flags & (1 << 2) else None
        
        return BotInlineMessageMediaInvoice(title=title, description=description, currency=currency, total_amount=total_amount, shipping_address_requested=shipping_address_requested, test=test, photo=photo, reply_markup=reply_markup)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 1) if self.shipping_address_requested else 0
        flags |= (1 << 3) if self.test else 0
        flags |= (1 << 0) if self.photo is not None else 0
        flags |= (1 << 2) if self.reply_markup is not None else 0
        b.write(Int(flags))
        
        b.write(String(self.title))
        
        b.write(String(self.description))
        
        if self.photo is not None:
            b.write(self.photo.write())
        
        b.write(String(self.currency))
        
        b.write(Long(self.total_amount))
        
        if self.reply_markup is not None:
            b.write(self.reply_markup.write())
        
        return b.getvalue()
