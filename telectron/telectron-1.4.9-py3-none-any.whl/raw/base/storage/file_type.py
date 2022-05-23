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

FileType = Union[raw.types.storage.FileGif, raw.types.storage.FileJpeg, raw.types.storage.FileMov, raw.types.storage.FileMp3, raw.types.storage.FileMp4, raw.types.storage.FilePartial, raw.types.storage.FilePdf, raw.types.storage.FilePng, raw.types.storage.FileUnknown, raw.types.storage.FileWebp]


# noinspection PyRedeclaration
class FileType:  # type: ignore
    """This base type has 10 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`storage.FileGif <telectron.raw.types.storage.FileGif>`
            - :obj:`storage.FileJpeg <telectron.raw.types.storage.FileJpeg>`
            - :obj:`storage.FileMov <telectron.raw.types.storage.FileMov>`
            - :obj:`storage.FileMp3 <telectron.raw.types.storage.FileMp3>`
            - :obj:`storage.FileMp4 <telectron.raw.types.storage.FileMp4>`
            - :obj:`storage.FilePartial <telectron.raw.types.storage.FilePartial>`
            - :obj:`storage.FilePdf <telectron.raw.types.storage.FilePdf>`
            - :obj:`storage.FilePng <telectron.raw.types.storage.FilePng>`
            - :obj:`storage.FileUnknown <telectron.raw.types.storage.FileUnknown>`
            - :obj:`storage.FileWebp <telectron.raw.types.storage.FileWebp>`
    """

    QUALNAME = "telectron.raw.base.storage.FileType"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.telectron.org/telegram/base/file-type")
