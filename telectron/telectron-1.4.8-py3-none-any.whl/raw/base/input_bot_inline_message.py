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

InputBotInlineMessage = Union[raw.types.InputBotInlineMessageGame, raw.types.InputBotInlineMessageMediaAuto, raw.types.InputBotInlineMessageMediaContact, raw.types.InputBotInlineMessageMediaGeo, raw.types.InputBotInlineMessageMediaInvoice, raw.types.InputBotInlineMessageMediaVenue, raw.types.InputBotInlineMessageText]


# noinspection PyRedeclaration
class InputBotInlineMessage:  # type: ignore
    """This base type has 7 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputBotInlineMessageGame <telectron.raw.types.InputBotInlineMessageGame>`
            - :obj:`InputBotInlineMessageMediaAuto <telectron.raw.types.InputBotInlineMessageMediaAuto>`
            - :obj:`InputBotInlineMessageMediaContact <telectron.raw.types.InputBotInlineMessageMediaContact>`
            - :obj:`InputBotInlineMessageMediaGeo <telectron.raw.types.InputBotInlineMessageMediaGeo>`
            - :obj:`InputBotInlineMessageMediaInvoice <telectron.raw.types.InputBotInlineMessageMediaInvoice>`
            - :obj:`InputBotInlineMessageMediaVenue <telectron.raw.types.InputBotInlineMessageMediaVenue>`
            - :obj:`InputBotInlineMessageText <telectron.raw.types.InputBotInlineMessageText>`
    """

    QUALNAME = "telectron.raw.base.InputBotInlineMessage"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.telectron.org/telegram/base/input-bot-inline-message")
