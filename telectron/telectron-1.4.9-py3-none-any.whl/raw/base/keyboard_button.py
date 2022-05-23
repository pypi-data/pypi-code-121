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

KeyboardButton = Union[raw.types.InputKeyboardButtonUrlAuth, raw.types.InputKeyboardButtonUserProfile, raw.types.KeyboardButton, raw.types.KeyboardButtonBuy, raw.types.KeyboardButtonCallback, raw.types.KeyboardButtonGame, raw.types.KeyboardButtonRequestGeoLocation, raw.types.KeyboardButtonRequestPhone, raw.types.KeyboardButtonRequestPoll, raw.types.KeyboardButtonSwitchInline, raw.types.KeyboardButtonUrl, raw.types.KeyboardButtonUrlAuth, raw.types.KeyboardButtonUserProfile]


# noinspection PyRedeclaration
class KeyboardButton:  # type: ignore
    """This base type has 13 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputKeyboardButtonUrlAuth <telectron.raw.types.InputKeyboardButtonUrlAuth>`
            - :obj:`InputKeyboardButtonUserProfile <telectron.raw.types.InputKeyboardButtonUserProfile>`
            - :obj:`KeyboardButton <telectron.raw.types.KeyboardButton>`
            - :obj:`KeyboardButtonBuy <telectron.raw.types.KeyboardButtonBuy>`
            - :obj:`KeyboardButtonCallback <telectron.raw.types.KeyboardButtonCallback>`
            - :obj:`KeyboardButtonGame <telectron.raw.types.KeyboardButtonGame>`
            - :obj:`KeyboardButtonRequestGeoLocation <telectron.raw.types.KeyboardButtonRequestGeoLocation>`
            - :obj:`KeyboardButtonRequestPhone <telectron.raw.types.KeyboardButtonRequestPhone>`
            - :obj:`KeyboardButtonRequestPoll <telectron.raw.types.KeyboardButtonRequestPoll>`
            - :obj:`KeyboardButtonSwitchInline <telectron.raw.types.KeyboardButtonSwitchInline>`
            - :obj:`KeyboardButtonUrl <telectron.raw.types.KeyboardButtonUrl>`
            - :obj:`KeyboardButtonUrlAuth <telectron.raw.types.KeyboardButtonUrlAuth>`
            - :obj:`KeyboardButtonUserProfile <telectron.raw.types.KeyboardButtonUserProfile>`
    """

    QUALNAME = "telectron.raw.base.KeyboardButton"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.telectron.org/telegram/base/keyboard-button")
