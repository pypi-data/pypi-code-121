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

Updates = Union[raw.types.UpdateShort, raw.types.UpdateShortChatMessage, raw.types.UpdateShortMessage, raw.types.UpdateShortSentMessage, raw.types.Updates, raw.types.UpdatesCombined, raw.types.UpdatesTooLong]


# noinspection PyRedeclaration
class Updates:  # type: ignore
    """This base type has 7 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`UpdateShort <telectron.raw.types.UpdateShort>`
            - :obj:`UpdateShortChatMessage <telectron.raw.types.UpdateShortChatMessage>`
            - :obj:`UpdateShortMessage <telectron.raw.types.UpdateShortMessage>`
            - :obj:`UpdateShortSentMessage <telectron.raw.types.UpdateShortSentMessage>`
            - :obj:`Updates <telectron.raw.types.Updates>`
            - :obj:`UpdatesCombined <telectron.raw.types.UpdatesCombined>`
            - :obj:`UpdatesTooLong <telectron.raw.types.UpdatesTooLong>`

    See Also:
        This object can be returned by 69 methods:

        .. hlist::
            :columns: 2

            - :obj:`account.GetNotifyExceptions <telectron.raw.functions.account.GetNotifyExceptions>`
            - :obj:`contacts.DeleteContacts <telectron.raw.functions.contacts.DeleteContacts>`
            - :obj:`contacts.AddContact <telectron.raw.functions.contacts.AddContact>`
            - :obj:`contacts.AcceptContact <telectron.raw.functions.contacts.AcceptContact>`
            - :obj:`contacts.GetLocated <telectron.raw.functions.contacts.GetLocated>`
            - :obj:`contacts.BlockFromReplies <telectron.raw.functions.contacts.BlockFromReplies>`
            - :obj:`messages.SendMessage <telectron.raw.functions.messages.SendMessage>`
            - :obj:`messages.SendMedia <telectron.raw.functions.messages.SendMedia>`
            - :obj:`messages.ForwardMessages <telectron.raw.functions.messages.ForwardMessages>`
            - :obj:`messages.EditChatTitle <telectron.raw.functions.messages.EditChatTitle>`
            - :obj:`messages.EditChatPhoto <telectron.raw.functions.messages.EditChatPhoto>`
            - :obj:`messages.AddChatUser <telectron.raw.functions.messages.AddChatUser>`
            - :obj:`messages.DeleteChatUser <telectron.raw.functions.messages.DeleteChatUser>`
            - :obj:`messages.CreateChat <telectron.raw.functions.messages.CreateChat>`
            - :obj:`messages.ImportChatInvite <telectron.raw.functions.messages.ImportChatInvite>`
            - :obj:`messages.StartBot <telectron.raw.functions.messages.StartBot>`
            - :obj:`messages.MigrateChat <telectron.raw.functions.messages.MigrateChat>`
            - :obj:`messages.SendInlineBotResult <telectron.raw.functions.messages.SendInlineBotResult>`
            - :obj:`messages.EditMessage <telectron.raw.functions.messages.EditMessage>`
            - :obj:`messages.GetAllDrafts <telectron.raw.functions.messages.GetAllDrafts>`
            - :obj:`messages.SetGameScore <telectron.raw.functions.messages.SetGameScore>`
            - :obj:`messages.SendScreenshotNotification <telectron.raw.functions.messages.SendScreenshotNotification>`
            - :obj:`messages.SendMultiMedia <telectron.raw.functions.messages.SendMultiMedia>`
            - :obj:`messages.UpdatePinnedMessage <telectron.raw.functions.messages.UpdatePinnedMessage>`
            - :obj:`messages.SendVote <telectron.raw.functions.messages.SendVote>`
            - :obj:`messages.GetPollResults <telectron.raw.functions.messages.GetPollResults>`
            - :obj:`messages.EditChatDefaultBannedRights <telectron.raw.functions.messages.EditChatDefaultBannedRights>`
            - :obj:`messages.SendScheduledMessages <telectron.raw.functions.messages.SendScheduledMessages>`
            - :obj:`messages.DeleteScheduledMessages <telectron.raw.functions.messages.DeleteScheduledMessages>`
            - :obj:`messages.SetHistoryTTL <telectron.raw.functions.messages.SetHistoryTTL>`
            - :obj:`messages.SetChatTheme <telectron.raw.functions.messages.SetChatTheme>`
            - :obj:`messages.HideChatJoinRequest <telectron.raw.functions.messages.HideChatJoinRequest>`
            - :obj:`messages.HideAllChatJoinRequests <telectron.raw.functions.messages.HideAllChatJoinRequests>`
            - :obj:`messages.ToggleNoForwards <telectron.raw.functions.messages.ToggleNoForwards>`
            - :obj:`messages.SendReaction <telectron.raw.functions.messages.SendReaction>`
            - :obj:`messages.GetMessagesReactions <telectron.raw.functions.messages.GetMessagesReactions>`
            - :obj:`messages.SetChatAvailableReactions <telectron.raw.functions.messages.SetChatAvailableReactions>`
            - :obj:`help.GetAppChangelog <telectron.raw.functions.help.GetAppChangelog>`
            - :obj:`channels.CreateChannel <telectron.raw.functions.channels.CreateChannel>`
            - :obj:`channels.EditAdmin <telectron.raw.functions.channels.EditAdmin>`
            - :obj:`channels.EditTitle <telectron.raw.functions.channels.EditTitle>`
            - :obj:`channels.EditPhoto <telectron.raw.functions.channels.EditPhoto>`
            - :obj:`channels.JoinChannel <telectron.raw.functions.channels.JoinChannel>`
            - :obj:`channels.LeaveChannel <telectron.raw.functions.channels.LeaveChannel>`
            - :obj:`channels.InviteToChannel <telectron.raw.functions.channels.InviteToChannel>`
            - :obj:`channels.DeleteChannel <telectron.raw.functions.channels.DeleteChannel>`
            - :obj:`channels.ToggleSignatures <telectron.raw.functions.channels.ToggleSignatures>`
            - :obj:`channels.EditBanned <telectron.raw.functions.channels.EditBanned>`
            - :obj:`channels.TogglePreHistoryHidden <telectron.raw.functions.channels.TogglePreHistoryHidden>`
            - :obj:`channels.EditCreator <telectron.raw.functions.channels.EditCreator>`
            - :obj:`channels.ToggleSlowMode <telectron.raw.functions.channels.ToggleSlowMode>`
            - :obj:`channels.ConvertToGigagroup <telectron.raw.functions.channels.ConvertToGigagroup>`
            - :obj:`phone.DiscardCall <telectron.raw.functions.phone.DiscardCall>`
            - :obj:`phone.SetCallRating <telectron.raw.functions.phone.SetCallRating>`
            - :obj:`phone.CreateGroupCall <telectron.raw.functions.phone.CreateGroupCall>`
            - :obj:`phone.JoinGroupCall <telectron.raw.functions.phone.JoinGroupCall>`
            - :obj:`phone.LeaveGroupCall <telectron.raw.functions.phone.LeaveGroupCall>`
            - :obj:`phone.InviteToGroupCall <telectron.raw.functions.phone.InviteToGroupCall>`
            - :obj:`phone.DiscardGroupCall <telectron.raw.functions.phone.DiscardGroupCall>`
            - :obj:`phone.ToggleGroupCallSettings <telectron.raw.functions.phone.ToggleGroupCallSettings>`
            - :obj:`phone.ToggleGroupCallRecord <telectron.raw.functions.phone.ToggleGroupCallRecord>`
            - :obj:`phone.EditGroupCallParticipant <telectron.raw.functions.phone.EditGroupCallParticipant>`
            - :obj:`phone.EditGroupCallTitle <telectron.raw.functions.phone.EditGroupCallTitle>`
            - :obj:`phone.ToggleGroupCallStartSubscription <telectron.raw.functions.phone.ToggleGroupCallStartSubscription>`
            - :obj:`phone.StartScheduledGroupCall <telectron.raw.functions.phone.StartScheduledGroupCall>`
            - :obj:`phone.JoinGroupCallPresentation <telectron.raw.functions.phone.JoinGroupCallPresentation>`
            - :obj:`phone.LeaveGroupCallPresentation <telectron.raw.functions.phone.LeaveGroupCallPresentation>`
            - :obj:`folders.EditPeerFolders <telectron.raw.functions.folders.EditPeerFolders>`
            - :obj:`folders.DeleteFolder <telectron.raw.functions.folders.DeleteFolder>`
    """

    QUALNAME = "telectron.raw.base.Updates"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.telectron.org/telegram/base/updates")
