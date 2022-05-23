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

BotInlineMessage = Union[raw.types.BotInlineMessageMediaAuto, raw.types.BotInlineMessageMediaContact, raw.types.BotInlineMessageMediaGeo, raw.types.BotInlineMessageMediaInvoice, raw.types.BotInlineMessageMediaVenue, raw.types.BotInlineMessageText]


# noinspection PyRedeclaration
class BotInlineMessage:  # type: ignore
    """This base type has 6 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`BotInlineMessageMediaAuto <telectron.raw.types.BotInlineMessageMediaAuto>`
            - :obj:`BotInlineMessageMediaContact <telectron.raw.types.BotInlineMessageMediaContact>`
            - :obj:`BotInlineMessageMediaGeo <telectron.raw.types.BotInlineMessageMediaGeo>`
            - :obj:`BotInlineMessageMediaInvoice <telectron.raw.types.BotInlineMessageMediaInvoice>`
            - :obj:`BotInlineMessageMediaVenue <telectron.raw.types.BotInlineMessageMediaVenue>`
            - :obj:`BotInlineMessageText <telectron.raw.types.BotInlineMessageText>`
    """

    QUALNAME = "telectron.raw.base.BotInlineMessage"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.telectron.org/telegram/base/bot-inline-message")
