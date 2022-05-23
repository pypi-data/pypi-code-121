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

MessagesFilter = Union[raw.types.InputMessagesFilterChatPhotos, raw.types.InputMessagesFilterContacts, raw.types.InputMessagesFilterDocument, raw.types.InputMessagesFilterEmpty, raw.types.InputMessagesFilterGeo, raw.types.InputMessagesFilterGif, raw.types.InputMessagesFilterMusic, raw.types.InputMessagesFilterMyMentions, raw.types.InputMessagesFilterPhoneCalls, raw.types.InputMessagesFilterPhotoVideo, raw.types.InputMessagesFilterPhotos, raw.types.InputMessagesFilterPinned, raw.types.InputMessagesFilterRoundVideo, raw.types.InputMessagesFilterRoundVoice, raw.types.InputMessagesFilterUrl, raw.types.InputMessagesFilterVideo, raw.types.InputMessagesFilterVoice]


# noinspection PyRedeclaration
class MessagesFilter:  # type: ignore
    """This base type has 17 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputMessagesFilterChatPhotos <telectron.raw.types.InputMessagesFilterChatPhotos>`
            - :obj:`InputMessagesFilterContacts <telectron.raw.types.InputMessagesFilterContacts>`
            - :obj:`InputMessagesFilterDocument <telectron.raw.types.InputMessagesFilterDocument>`
            - :obj:`InputMessagesFilterEmpty <telectron.raw.types.InputMessagesFilterEmpty>`
            - :obj:`InputMessagesFilterGeo <telectron.raw.types.InputMessagesFilterGeo>`
            - :obj:`InputMessagesFilterGif <telectron.raw.types.InputMessagesFilterGif>`
            - :obj:`InputMessagesFilterMusic <telectron.raw.types.InputMessagesFilterMusic>`
            - :obj:`InputMessagesFilterMyMentions <telectron.raw.types.InputMessagesFilterMyMentions>`
            - :obj:`InputMessagesFilterPhoneCalls <telectron.raw.types.InputMessagesFilterPhoneCalls>`
            - :obj:`InputMessagesFilterPhotoVideo <telectron.raw.types.InputMessagesFilterPhotoVideo>`
            - :obj:`InputMessagesFilterPhotos <telectron.raw.types.InputMessagesFilterPhotos>`
            - :obj:`InputMessagesFilterPinned <telectron.raw.types.InputMessagesFilterPinned>`
            - :obj:`InputMessagesFilterRoundVideo <telectron.raw.types.InputMessagesFilterRoundVideo>`
            - :obj:`InputMessagesFilterRoundVoice <telectron.raw.types.InputMessagesFilterRoundVoice>`
            - :obj:`InputMessagesFilterUrl <telectron.raw.types.InputMessagesFilterUrl>`
            - :obj:`InputMessagesFilterVideo <telectron.raw.types.InputMessagesFilterVideo>`
            - :obj:`InputMessagesFilterVoice <telectron.raw.types.InputMessagesFilterVoice>`
    """

    QUALNAME = "telectron.raw.base.MessagesFilter"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.telectron.org/telegram/base/messages-filter")
