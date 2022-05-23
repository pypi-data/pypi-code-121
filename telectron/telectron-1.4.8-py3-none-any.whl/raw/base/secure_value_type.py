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

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #

from typing import Union
from telectron import raw
from telectron.raw.core import TLObject

SecureValueType = Union[raw.types.SecureValueTypeAddress, raw.types.SecureValueTypeBankStatement, raw.types.SecureValueTypeDriverLicense, raw.types.SecureValueTypeEmail, raw.types.SecureValueTypeIdentityCard, raw.types.SecureValueTypeInternalPassport, raw.types.SecureValueTypePassport, raw.types.SecureValueTypePassportRegistration, raw.types.SecureValueTypePersonalDetails, raw.types.SecureValueTypePhone, raw.types.SecureValueTypeRentalAgreement, raw.types.SecureValueTypeTemporaryRegistration, raw.types.SecureValueTypeUtilityBill]


# noinspection PyRedeclaration
class SecureValueType:  # type: ignore
    """This base type has 13 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`SecureValueTypeAddress <telectron.raw.types.SecureValueTypeAddress>`
            - :obj:`SecureValueTypeBankStatement <telectron.raw.types.SecureValueTypeBankStatement>`
            - :obj:`SecureValueTypeDriverLicense <telectron.raw.types.SecureValueTypeDriverLicense>`
            - :obj:`SecureValueTypeEmail <telectron.raw.types.SecureValueTypeEmail>`
            - :obj:`SecureValueTypeIdentityCard <telectron.raw.types.SecureValueTypeIdentityCard>`
            - :obj:`SecureValueTypeInternalPassport <telectron.raw.types.SecureValueTypeInternalPassport>`
            - :obj:`SecureValueTypePassport <telectron.raw.types.SecureValueTypePassport>`
            - :obj:`SecureValueTypePassportRegistration <telectron.raw.types.SecureValueTypePassportRegistration>`
            - :obj:`SecureValueTypePersonalDetails <telectron.raw.types.SecureValueTypePersonalDetails>`
            - :obj:`SecureValueTypePhone <telectron.raw.types.SecureValueTypePhone>`
            - :obj:`SecureValueTypeRentalAgreement <telectron.raw.types.SecureValueTypeRentalAgreement>`
            - :obj:`SecureValueTypeTemporaryRegistration <telectron.raw.types.SecureValueTypeTemporaryRegistration>`
            - :obj:`SecureValueTypeUtilityBill <telectron.raw.types.SecureValueTypeUtilityBill>`
    """

    QUALNAME = "telectron.raw.base.SecureValueType"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.telectron.org/telegram/base/secure-value-type")
