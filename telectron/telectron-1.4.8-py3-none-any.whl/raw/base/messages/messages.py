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

Messages = Union[raw.types.messages.ChannelMessages, raw.types.messages.Messages, raw.types.messages.MessagesNotModified, raw.types.messages.MessagesSlice]


# noinspection PyRedeclaration
class Messages:  # type: ignore
    """This base type has 4 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`messages.ChannelMessages <telectron.raw.types.messages.ChannelMessages>`
            - :obj:`messages.Messages <telectron.raw.types.messages.Messages>`
            - :obj:`messages.MessagesNotModified <telectron.raw.types.messages.MessagesNotModified>`
            - :obj:`messages.MessagesSlice <telectron.raw.types.messages.MessagesSlice>`

    See Also:
        This object can be returned by 12 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetMessages <telectron.raw.functions.messages.GetMessages>`
            - :obj:`messages.GetHistory <telectron.raw.functions.messages.GetHistory>`
            - :obj:`messages.Search <telectron.raw.functions.messages.Search>`
            - :obj:`messages.SearchGlobal <telectron.raw.functions.messages.SearchGlobal>`
            - :obj:`messages.GetUnreadMentions <telectron.raw.functions.messages.GetUnreadMentions>`
            - :obj:`messages.GetRecentLocations <telectron.raw.functions.messages.GetRecentLocations>`
            - :obj:`messages.GetScheduledHistory <telectron.raw.functions.messages.GetScheduledHistory>`
            - :obj:`messages.GetScheduledMessages <telectron.raw.functions.messages.GetScheduledMessages>`
            - :obj:`messages.GetReplies <telectron.raw.functions.messages.GetReplies>`
            - :obj:`messages.GetUnreadReactions <telectron.raw.functions.messages.GetUnreadReactions>`
            - :obj:`channels.GetMessages <telectron.raw.functions.channels.GetMessages>`
            - :obj:`stats.GetMessagePublicForwards <telectron.raw.functions.stats.GetMessagePublicForwards>`
    """

    QUALNAME = "telectron.raw.base.messages.Messages"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.telectron.org/telegram/base/messages")
