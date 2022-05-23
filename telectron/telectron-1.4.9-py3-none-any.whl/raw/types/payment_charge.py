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


class PaymentCharge(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~telectron.raw.base.PaymentCharge`.

    Details:
        - Layer: ``138``
        - ID: ``0xea02c27e``

    Parameters:
        id: ``str``
        provider_charge_id: ``str``
    """

    __slots__: List[str] = ["id", "provider_charge_id"]

    ID = 0xea02c27e
    QUALNAME = "types.PaymentCharge"

    def __init__(self, *, id: str, provider_charge_id: str) -> None:
        self.id = id  # string
        self.provider_charge_id = provider_charge_id  # string

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "PaymentCharge":
        # No flags
        
        id = String.read(b)
        
        provider_charge_id = String.read(b)
        
        return PaymentCharge(id=id, provider_charge_id=provider_charge_id)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(String(self.id))
        
        b.write(String(self.provider_charge_id))
        
        return b.getvalue()
