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

Chat = Union[raw.types.Channel, raw.types.ChannelForbidden, raw.types.Chat, raw.types.ChatEmpty, raw.types.ChatForbidden]


# noinspection PyRedeclaration
class Chat:  # type: ignore
    """This base type has 5 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`Channel <telectron.raw.types.Channel>`
            - :obj:`ChannelForbidden <telectron.raw.types.ChannelForbidden>`
            - :obj:`Chat <telectron.raw.types.Chat>`
            - :obj:`ChatEmpty <telectron.raw.types.ChatEmpty>`
            - :obj:`ChatForbidden <telectron.raw.types.ChatForbidden>`
    """

    QUALNAME = "telectron.raw.base.Chat"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.telectron.org/telegram/base/chat")
