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

MessageMedia = Union[raw.types.MessageMediaContact, raw.types.MessageMediaDice, raw.types.MessageMediaDocument, raw.types.MessageMediaEmpty, raw.types.MessageMediaGame, raw.types.MessageMediaGeo, raw.types.MessageMediaGeoLive, raw.types.MessageMediaInvoice, raw.types.MessageMediaPhoto, raw.types.MessageMediaPoll, raw.types.MessageMediaUnsupported, raw.types.MessageMediaVenue, raw.types.MessageMediaWebPage]


# noinspection PyRedeclaration
class MessageMedia:  # type: ignore
    """This base type has 13 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`MessageMediaContact <telectron.raw.types.MessageMediaContact>`
            - :obj:`MessageMediaDice <telectron.raw.types.MessageMediaDice>`
            - :obj:`MessageMediaDocument <telectron.raw.types.MessageMediaDocument>`
            - :obj:`MessageMediaEmpty <telectron.raw.types.MessageMediaEmpty>`
            - :obj:`MessageMediaGame <telectron.raw.types.MessageMediaGame>`
            - :obj:`MessageMediaGeo <telectron.raw.types.MessageMediaGeo>`
            - :obj:`MessageMediaGeoLive <telectron.raw.types.MessageMediaGeoLive>`
            - :obj:`MessageMediaInvoice <telectron.raw.types.MessageMediaInvoice>`
            - :obj:`MessageMediaPhoto <telectron.raw.types.MessageMediaPhoto>`
            - :obj:`MessageMediaPoll <telectron.raw.types.MessageMediaPoll>`
            - :obj:`MessageMediaUnsupported <telectron.raw.types.MessageMediaUnsupported>`
            - :obj:`MessageMediaVenue <telectron.raw.types.MessageMediaVenue>`
            - :obj:`MessageMediaWebPage <telectron.raw.types.MessageMediaWebPage>`

    See Also:
        This object can be returned by 3 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetWebPagePreview <telectron.raw.functions.messages.GetWebPagePreview>`
            - :obj:`messages.UploadMedia <telectron.raw.functions.messages.UploadMedia>`
            - :obj:`messages.UploadImportedMedia <telectron.raw.functions.messages.UploadImportedMedia>`
    """

    QUALNAME = "telectron.raw.base.MessageMedia"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.telectron.org/telegram/base/message-media")
