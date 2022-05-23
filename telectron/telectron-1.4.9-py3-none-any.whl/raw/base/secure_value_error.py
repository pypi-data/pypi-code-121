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

SecureValueError = Union[raw.types.SecureValueError, raw.types.SecureValueErrorData, raw.types.SecureValueErrorFile, raw.types.SecureValueErrorFiles, raw.types.SecureValueErrorFrontSide, raw.types.SecureValueErrorReverseSide, raw.types.SecureValueErrorSelfie, raw.types.SecureValueErrorTranslationFile, raw.types.SecureValueErrorTranslationFiles]


# noinspection PyRedeclaration
class SecureValueError:  # type: ignore
    """This base type has 9 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`SecureValueError <telectron.raw.types.SecureValueError>`
            - :obj:`SecureValueErrorData <telectron.raw.types.SecureValueErrorData>`
            - :obj:`SecureValueErrorFile <telectron.raw.types.SecureValueErrorFile>`
            - :obj:`SecureValueErrorFiles <telectron.raw.types.SecureValueErrorFiles>`
            - :obj:`SecureValueErrorFrontSide <telectron.raw.types.SecureValueErrorFrontSide>`
            - :obj:`SecureValueErrorReverseSide <telectron.raw.types.SecureValueErrorReverseSide>`
            - :obj:`SecureValueErrorSelfie <telectron.raw.types.SecureValueErrorSelfie>`
            - :obj:`SecureValueErrorTranslationFile <telectron.raw.types.SecureValueErrorTranslationFile>`
            - :obj:`SecureValueErrorTranslationFiles <telectron.raw.types.SecureValueErrorTranslationFiles>`
    """

    QUALNAME = "telectron.raw.base.SecureValueError"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.telectron.org/telegram/base/secure-value-error")
