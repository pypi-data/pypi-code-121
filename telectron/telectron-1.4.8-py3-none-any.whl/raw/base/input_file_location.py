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

InputFileLocation = Union[raw.types.InputDocumentFileLocation, raw.types.InputEncryptedFileLocation, raw.types.InputFileLocation, raw.types.InputGroupCallStream, raw.types.InputPeerPhotoFileLocation, raw.types.InputPhotoFileLocation, raw.types.InputPhotoLegacyFileLocation, raw.types.InputSecureFileLocation, raw.types.InputStickerSetThumb, raw.types.InputTakeoutFileLocation]


# noinspection PyRedeclaration
class InputFileLocation:  # type: ignore
    """This base type has 10 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputDocumentFileLocation <telectron.raw.types.InputDocumentFileLocation>`
            - :obj:`InputEncryptedFileLocation <telectron.raw.types.InputEncryptedFileLocation>`
            - :obj:`InputFileLocation <telectron.raw.types.InputFileLocation>`
            - :obj:`InputGroupCallStream <telectron.raw.types.InputGroupCallStream>`
            - :obj:`InputPeerPhotoFileLocation <telectron.raw.types.InputPeerPhotoFileLocation>`
            - :obj:`InputPhotoFileLocation <telectron.raw.types.InputPhotoFileLocation>`
            - :obj:`InputPhotoLegacyFileLocation <telectron.raw.types.InputPhotoLegacyFileLocation>`
            - :obj:`InputSecureFileLocation <telectron.raw.types.InputSecureFileLocation>`
            - :obj:`InputStickerSetThumb <telectron.raw.types.InputStickerSetThumb>`
            - :obj:`InputTakeoutFileLocation <telectron.raw.types.InputTakeoutFileLocation>`
    """

    QUALNAME = "telectron.raw.base.InputFileLocation"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.telectron.org/telegram/base/input-file-location")
