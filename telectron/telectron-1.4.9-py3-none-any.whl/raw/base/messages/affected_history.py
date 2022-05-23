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

AffectedHistory = Union[raw.types.messages.AffectedHistory]


# noinspection PyRedeclaration
class AffectedHistory:  # type: ignore
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`messages.AffectedHistory <telectron.raw.types.messages.AffectedHistory>`

    See Also:
        This object can be returned by 5 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.DeleteHistory <telectron.raw.functions.messages.DeleteHistory>`
            - :obj:`messages.ReadMentions <telectron.raw.functions.messages.ReadMentions>`
            - :obj:`messages.UnpinAllMessages <telectron.raw.functions.messages.UnpinAllMessages>`
            - :obj:`messages.ReadReactions <telectron.raw.functions.messages.ReadReactions>`
            - :obj:`channels.DeleteParticipantHistory <telectron.raw.functions.channels.DeleteParticipantHistory>`
    """

    QUALNAME = "telectron.raw.base.messages.AffectedHistory"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.telectron.org/telegram/base/affected-history")
