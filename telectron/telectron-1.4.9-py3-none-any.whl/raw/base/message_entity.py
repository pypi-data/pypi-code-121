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

MessageEntity = Union[raw.types.InputMessageEntityMentionName, raw.types.MessageEntityBankCard, raw.types.MessageEntityBlockquote, raw.types.MessageEntityBold, raw.types.MessageEntityBotCommand, raw.types.MessageEntityCashtag, raw.types.MessageEntityCode, raw.types.MessageEntityEmail, raw.types.MessageEntityHashtag, raw.types.MessageEntityItalic, raw.types.MessageEntityMention, raw.types.MessageEntityMentionName, raw.types.MessageEntityPhone, raw.types.MessageEntityPre, raw.types.MessageEntitySpoiler, raw.types.MessageEntityStrike, raw.types.MessageEntityTextUrl, raw.types.MessageEntityUnderline, raw.types.MessageEntityUnknown, raw.types.MessageEntityUrl]


# noinspection PyRedeclaration
class MessageEntity:  # type: ignore
    """This base type has 20 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputMessageEntityMentionName <telectron.raw.types.InputMessageEntityMentionName>`
            - :obj:`MessageEntityBankCard <telectron.raw.types.MessageEntityBankCard>`
            - :obj:`MessageEntityBlockquote <telectron.raw.types.MessageEntityBlockquote>`
            - :obj:`MessageEntityBold <telectron.raw.types.MessageEntityBold>`
            - :obj:`MessageEntityBotCommand <telectron.raw.types.MessageEntityBotCommand>`
            - :obj:`MessageEntityCashtag <telectron.raw.types.MessageEntityCashtag>`
            - :obj:`MessageEntityCode <telectron.raw.types.MessageEntityCode>`
            - :obj:`MessageEntityEmail <telectron.raw.types.MessageEntityEmail>`
            - :obj:`MessageEntityHashtag <telectron.raw.types.MessageEntityHashtag>`
            - :obj:`MessageEntityItalic <telectron.raw.types.MessageEntityItalic>`
            - :obj:`MessageEntityMention <telectron.raw.types.MessageEntityMention>`
            - :obj:`MessageEntityMentionName <telectron.raw.types.MessageEntityMentionName>`
            - :obj:`MessageEntityPhone <telectron.raw.types.MessageEntityPhone>`
            - :obj:`MessageEntityPre <telectron.raw.types.MessageEntityPre>`
            - :obj:`MessageEntitySpoiler <telectron.raw.types.MessageEntitySpoiler>`
            - :obj:`MessageEntityStrike <telectron.raw.types.MessageEntityStrike>`
            - :obj:`MessageEntityTextUrl <telectron.raw.types.MessageEntityTextUrl>`
            - :obj:`MessageEntityUnderline <telectron.raw.types.MessageEntityUnderline>`
            - :obj:`MessageEntityUnknown <telectron.raw.types.MessageEntityUnknown>`
            - :obj:`MessageEntityUrl <telectron.raw.types.MessageEntityUrl>`
    """

    QUALNAME = "telectron.raw.base.MessageEntity"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.telectron.org/telegram/base/message-entity")
