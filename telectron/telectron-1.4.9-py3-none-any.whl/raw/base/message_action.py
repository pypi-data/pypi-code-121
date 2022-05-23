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

MessageAction = Union[raw.types.MessageActionBotAllowed, raw.types.MessageActionChannelCreate, raw.types.MessageActionChannelMigrateFrom, raw.types.MessageActionChatAddUser, raw.types.MessageActionChatCreate, raw.types.MessageActionChatDeletePhoto, raw.types.MessageActionChatDeleteUser, raw.types.MessageActionChatEditPhoto, raw.types.MessageActionChatEditTitle, raw.types.MessageActionChatJoinedByLink, raw.types.MessageActionChatJoinedByRequest, raw.types.MessageActionChatMigrateTo, raw.types.MessageActionContactSignUp, raw.types.MessageActionCustomAction, raw.types.MessageActionEmpty, raw.types.MessageActionGameScore, raw.types.MessageActionGeoProximityReached, raw.types.MessageActionGroupCall, raw.types.MessageActionGroupCallScheduled, raw.types.MessageActionHistoryClear, raw.types.MessageActionInviteToGroupCall, raw.types.MessageActionPaymentSent, raw.types.MessageActionPaymentSentMe, raw.types.MessageActionPhoneCall, raw.types.MessageActionPinMessage, raw.types.MessageActionScreenshotTaken, raw.types.MessageActionSecureValuesSent, raw.types.MessageActionSecureValuesSentMe, raw.types.MessageActionSetChatTheme, raw.types.MessageActionSetMessagesTTL]


# noinspection PyRedeclaration
class MessageAction:  # type: ignore
    """This base type has 30 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`MessageActionBotAllowed <telectron.raw.types.MessageActionBotAllowed>`
            - :obj:`MessageActionChannelCreate <telectron.raw.types.MessageActionChannelCreate>`
            - :obj:`MessageActionChannelMigrateFrom <telectron.raw.types.MessageActionChannelMigrateFrom>`
            - :obj:`MessageActionChatAddUser <telectron.raw.types.MessageActionChatAddUser>`
            - :obj:`MessageActionChatCreate <telectron.raw.types.MessageActionChatCreate>`
            - :obj:`MessageActionChatDeletePhoto <telectron.raw.types.MessageActionChatDeletePhoto>`
            - :obj:`MessageActionChatDeleteUser <telectron.raw.types.MessageActionChatDeleteUser>`
            - :obj:`MessageActionChatEditPhoto <telectron.raw.types.MessageActionChatEditPhoto>`
            - :obj:`MessageActionChatEditTitle <telectron.raw.types.MessageActionChatEditTitle>`
            - :obj:`MessageActionChatJoinedByLink <telectron.raw.types.MessageActionChatJoinedByLink>`
            - :obj:`MessageActionChatJoinedByRequest <telectron.raw.types.MessageActionChatJoinedByRequest>`
            - :obj:`MessageActionChatMigrateTo <telectron.raw.types.MessageActionChatMigrateTo>`
            - :obj:`MessageActionContactSignUp <telectron.raw.types.MessageActionContactSignUp>`
            - :obj:`MessageActionCustomAction <telectron.raw.types.MessageActionCustomAction>`
            - :obj:`MessageActionEmpty <telectron.raw.types.MessageActionEmpty>`
            - :obj:`MessageActionGameScore <telectron.raw.types.MessageActionGameScore>`
            - :obj:`MessageActionGeoProximityReached <telectron.raw.types.MessageActionGeoProximityReached>`
            - :obj:`MessageActionGroupCall <telectron.raw.types.MessageActionGroupCall>`
            - :obj:`MessageActionGroupCallScheduled <telectron.raw.types.MessageActionGroupCallScheduled>`
            - :obj:`MessageActionHistoryClear <telectron.raw.types.MessageActionHistoryClear>`
            - :obj:`MessageActionInviteToGroupCall <telectron.raw.types.MessageActionInviteToGroupCall>`
            - :obj:`MessageActionPaymentSent <telectron.raw.types.MessageActionPaymentSent>`
            - :obj:`MessageActionPaymentSentMe <telectron.raw.types.MessageActionPaymentSentMe>`
            - :obj:`MessageActionPhoneCall <telectron.raw.types.MessageActionPhoneCall>`
            - :obj:`MessageActionPinMessage <telectron.raw.types.MessageActionPinMessage>`
            - :obj:`MessageActionScreenshotTaken <telectron.raw.types.MessageActionScreenshotTaken>`
            - :obj:`MessageActionSecureValuesSent <telectron.raw.types.MessageActionSecureValuesSent>`
            - :obj:`MessageActionSecureValuesSentMe <telectron.raw.types.MessageActionSecureValuesSentMe>`
            - :obj:`MessageActionSetChatTheme <telectron.raw.types.MessageActionSetChatTheme>`
            - :obj:`MessageActionSetMessagesTTL <telectron.raw.types.MessageActionSetMessagesTTL>`
    """

    QUALNAME = "telectron.raw.base.MessageAction"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.telectron.org/telegram/base/message-action")
