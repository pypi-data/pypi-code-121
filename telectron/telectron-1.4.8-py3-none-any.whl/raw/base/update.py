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

Update = Union[raw.types.UpdateBotCallbackQuery, raw.types.UpdateBotChatInviteRequester, raw.types.UpdateBotCommands, raw.types.UpdateBotInlineQuery, raw.types.UpdateBotInlineSend, raw.types.UpdateBotPrecheckoutQuery, raw.types.UpdateBotShippingQuery, raw.types.UpdateBotStopped, raw.types.UpdateBotWebhookJSON, raw.types.UpdateBotWebhookJSONQuery, raw.types.UpdateChannel, raw.types.UpdateChannelAvailableMessages, raw.types.UpdateChannelMessageForwards, raw.types.UpdateChannelMessageViews, raw.types.UpdateChannelParticipant, raw.types.UpdateChannelReadMessagesContents, raw.types.UpdateChannelTooLong, raw.types.UpdateChannelUserTyping, raw.types.UpdateChannelWebPage, raw.types.UpdateChat, raw.types.UpdateChatDefaultBannedRights, raw.types.UpdateChatParticipant, raw.types.UpdateChatParticipantAdd, raw.types.UpdateChatParticipantAdmin, raw.types.UpdateChatParticipantDelete, raw.types.UpdateChatParticipants, raw.types.UpdateChatUserTyping, raw.types.UpdateConfig, raw.types.UpdateContactsReset, raw.types.UpdateDcOptions, raw.types.UpdateDeleteChannelMessages, raw.types.UpdateDeleteMessages, raw.types.UpdateDeleteScheduledMessages, raw.types.UpdateDialogFilter, raw.types.UpdateDialogFilterOrder, raw.types.UpdateDialogFilters, raw.types.UpdateDialogPinned, raw.types.UpdateDialogUnreadMark, raw.types.UpdateDraftMessage, raw.types.UpdateEditChannelMessage, raw.types.UpdateEditMessage, raw.types.UpdateEncryptedChatTyping, raw.types.UpdateEncryptedMessagesRead, raw.types.UpdateEncryption, raw.types.UpdateFavedStickers, raw.types.UpdateFolderPeers, raw.types.UpdateGeoLiveViewed, raw.types.UpdateGroupCall, raw.types.UpdateGroupCallConnection, raw.types.UpdateGroupCallParticipants, raw.types.UpdateInlineBotCallbackQuery, raw.types.UpdateLangPack, raw.types.UpdateLangPackTooLong, raw.types.UpdateLoginToken, raw.types.UpdateMessageID, raw.types.UpdateMessagePoll, raw.types.UpdateMessagePollVote, raw.types.UpdateMessageReactions, raw.types.UpdateNewChannelMessage, raw.types.UpdateNewEncryptedMessage, raw.types.UpdateNewMessage, raw.types.UpdateNewScheduledMessage, raw.types.UpdateNewStickerSet, raw.types.UpdateNotifySettings, raw.types.UpdatePeerBlocked, raw.types.UpdatePeerHistoryTTL, raw.types.UpdatePeerLocated, raw.types.UpdatePeerSettings, raw.types.UpdatePendingJoinRequests, raw.types.UpdatePhoneCall, raw.types.UpdatePhoneCallSignalingData, raw.types.UpdatePinnedChannelMessages, raw.types.UpdatePinnedDialogs, raw.types.UpdatePinnedMessages, raw.types.UpdatePrivacy, raw.types.UpdatePtsChanged, raw.types.UpdateReadChannelDiscussionInbox, raw.types.UpdateReadChannelDiscussionOutbox, raw.types.UpdateReadChannelInbox, raw.types.UpdateReadChannelOutbox, raw.types.UpdateReadFeaturedStickers, raw.types.UpdateReadHistoryInbox, raw.types.UpdateReadHistoryOutbox, raw.types.UpdateReadMessagesContents, raw.types.UpdateRecentStickers, raw.types.UpdateSavedGifs, raw.types.UpdateServiceNotification, raw.types.UpdateStickerSets, raw.types.UpdateStickerSetsOrder, raw.types.UpdateTheme, raw.types.UpdateUserName, raw.types.UpdateUserPhone, raw.types.UpdateUserPhoto, raw.types.UpdateUserStatus, raw.types.UpdateUserTyping, raw.types.UpdateWebPage]


# noinspection PyRedeclaration
class Update:  # type: ignore
    """This base type has 96 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`UpdateBotCallbackQuery <telectron.raw.types.UpdateBotCallbackQuery>`
            - :obj:`UpdateBotChatInviteRequester <telectron.raw.types.UpdateBotChatInviteRequester>`
            - :obj:`UpdateBotCommands <telectron.raw.types.UpdateBotCommands>`
            - :obj:`UpdateBotInlineQuery <telectron.raw.types.UpdateBotInlineQuery>`
            - :obj:`UpdateBotInlineSend <telectron.raw.types.UpdateBotInlineSend>`
            - :obj:`UpdateBotPrecheckoutQuery <telectron.raw.types.UpdateBotPrecheckoutQuery>`
            - :obj:`UpdateBotShippingQuery <telectron.raw.types.UpdateBotShippingQuery>`
            - :obj:`UpdateBotStopped <telectron.raw.types.UpdateBotStopped>`
            - :obj:`UpdateBotWebhookJSON <telectron.raw.types.UpdateBotWebhookJSON>`
            - :obj:`UpdateBotWebhookJSONQuery <telectron.raw.types.UpdateBotWebhookJSONQuery>`
            - :obj:`UpdateChannel <telectron.raw.types.UpdateChannel>`
            - :obj:`UpdateChannelAvailableMessages <telectron.raw.types.UpdateChannelAvailableMessages>`
            - :obj:`UpdateChannelMessageForwards <telectron.raw.types.UpdateChannelMessageForwards>`
            - :obj:`UpdateChannelMessageViews <telectron.raw.types.UpdateChannelMessageViews>`
            - :obj:`UpdateChannelParticipant <telectron.raw.types.UpdateChannelParticipant>`
            - :obj:`UpdateChannelReadMessagesContents <telectron.raw.types.UpdateChannelReadMessagesContents>`
            - :obj:`UpdateChannelTooLong <telectron.raw.types.UpdateChannelTooLong>`
            - :obj:`UpdateChannelUserTyping <telectron.raw.types.UpdateChannelUserTyping>`
            - :obj:`UpdateChannelWebPage <telectron.raw.types.UpdateChannelWebPage>`
            - :obj:`UpdateChat <telectron.raw.types.UpdateChat>`
            - :obj:`UpdateChatDefaultBannedRights <telectron.raw.types.UpdateChatDefaultBannedRights>`
            - :obj:`UpdateChatParticipant <telectron.raw.types.UpdateChatParticipant>`
            - :obj:`UpdateChatParticipantAdd <telectron.raw.types.UpdateChatParticipantAdd>`
            - :obj:`UpdateChatParticipantAdmin <telectron.raw.types.UpdateChatParticipantAdmin>`
            - :obj:`UpdateChatParticipantDelete <telectron.raw.types.UpdateChatParticipantDelete>`
            - :obj:`UpdateChatParticipants <telectron.raw.types.UpdateChatParticipants>`
            - :obj:`UpdateChatUserTyping <telectron.raw.types.UpdateChatUserTyping>`
            - :obj:`UpdateConfig <telectron.raw.types.UpdateConfig>`
            - :obj:`UpdateContactsReset <telectron.raw.types.UpdateContactsReset>`
            - :obj:`UpdateDcOptions <telectron.raw.types.UpdateDcOptions>`
            - :obj:`UpdateDeleteChannelMessages <telectron.raw.types.UpdateDeleteChannelMessages>`
            - :obj:`UpdateDeleteMessages <telectron.raw.types.UpdateDeleteMessages>`
            - :obj:`UpdateDeleteScheduledMessages <telectron.raw.types.UpdateDeleteScheduledMessages>`
            - :obj:`UpdateDialogFilter <telectron.raw.types.UpdateDialogFilter>`
            - :obj:`UpdateDialogFilterOrder <telectron.raw.types.UpdateDialogFilterOrder>`
            - :obj:`UpdateDialogFilters <telectron.raw.types.UpdateDialogFilters>`
            - :obj:`UpdateDialogPinned <telectron.raw.types.UpdateDialogPinned>`
            - :obj:`UpdateDialogUnreadMark <telectron.raw.types.UpdateDialogUnreadMark>`
            - :obj:`UpdateDraftMessage <telectron.raw.types.UpdateDraftMessage>`
            - :obj:`UpdateEditChannelMessage <telectron.raw.types.UpdateEditChannelMessage>`
            - :obj:`UpdateEditMessage <telectron.raw.types.UpdateEditMessage>`
            - :obj:`UpdateEncryptedChatTyping <telectron.raw.types.UpdateEncryptedChatTyping>`
            - :obj:`UpdateEncryptedMessagesRead <telectron.raw.types.UpdateEncryptedMessagesRead>`
            - :obj:`UpdateEncryption <telectron.raw.types.UpdateEncryption>`
            - :obj:`UpdateFavedStickers <telectron.raw.types.UpdateFavedStickers>`
            - :obj:`UpdateFolderPeers <telectron.raw.types.UpdateFolderPeers>`
            - :obj:`UpdateGeoLiveViewed <telectron.raw.types.UpdateGeoLiveViewed>`
            - :obj:`UpdateGroupCall <telectron.raw.types.UpdateGroupCall>`
            - :obj:`UpdateGroupCallConnection <telectron.raw.types.UpdateGroupCallConnection>`
            - :obj:`UpdateGroupCallParticipants <telectron.raw.types.UpdateGroupCallParticipants>`
            - :obj:`UpdateInlineBotCallbackQuery <telectron.raw.types.UpdateInlineBotCallbackQuery>`
            - :obj:`UpdateLangPack <telectron.raw.types.UpdateLangPack>`
            - :obj:`UpdateLangPackTooLong <telectron.raw.types.UpdateLangPackTooLong>`
            - :obj:`UpdateLoginToken <telectron.raw.types.UpdateLoginToken>`
            - :obj:`UpdateMessageID <telectron.raw.types.UpdateMessageID>`
            - :obj:`UpdateMessagePoll <telectron.raw.types.UpdateMessagePoll>`
            - :obj:`UpdateMessagePollVote <telectron.raw.types.UpdateMessagePollVote>`
            - :obj:`UpdateMessageReactions <telectron.raw.types.UpdateMessageReactions>`
            - :obj:`UpdateNewChannelMessage <telectron.raw.types.UpdateNewChannelMessage>`
            - :obj:`UpdateNewEncryptedMessage <telectron.raw.types.UpdateNewEncryptedMessage>`
            - :obj:`UpdateNewMessage <telectron.raw.types.UpdateNewMessage>`
            - :obj:`UpdateNewScheduledMessage <telectron.raw.types.UpdateNewScheduledMessage>`
            - :obj:`UpdateNewStickerSet <telectron.raw.types.UpdateNewStickerSet>`
            - :obj:`UpdateNotifySettings <telectron.raw.types.UpdateNotifySettings>`
            - :obj:`UpdatePeerBlocked <telectron.raw.types.UpdatePeerBlocked>`
            - :obj:`UpdatePeerHistoryTTL <telectron.raw.types.UpdatePeerHistoryTTL>`
            - :obj:`UpdatePeerLocated <telectron.raw.types.UpdatePeerLocated>`
            - :obj:`UpdatePeerSettings <telectron.raw.types.UpdatePeerSettings>`
            - :obj:`UpdatePendingJoinRequests <telectron.raw.types.UpdatePendingJoinRequests>`
            - :obj:`UpdatePhoneCall <telectron.raw.types.UpdatePhoneCall>`
            - :obj:`UpdatePhoneCallSignalingData <telectron.raw.types.UpdatePhoneCallSignalingData>`
            - :obj:`UpdatePinnedChannelMessages <telectron.raw.types.UpdatePinnedChannelMessages>`
            - :obj:`UpdatePinnedDialogs <telectron.raw.types.UpdatePinnedDialogs>`
            - :obj:`UpdatePinnedMessages <telectron.raw.types.UpdatePinnedMessages>`
            - :obj:`UpdatePrivacy <telectron.raw.types.UpdatePrivacy>`
            - :obj:`UpdatePtsChanged <telectron.raw.types.UpdatePtsChanged>`
            - :obj:`UpdateReadChannelDiscussionInbox <telectron.raw.types.UpdateReadChannelDiscussionInbox>`
            - :obj:`UpdateReadChannelDiscussionOutbox <telectron.raw.types.UpdateReadChannelDiscussionOutbox>`
            - :obj:`UpdateReadChannelInbox <telectron.raw.types.UpdateReadChannelInbox>`
            - :obj:`UpdateReadChannelOutbox <telectron.raw.types.UpdateReadChannelOutbox>`
            - :obj:`UpdateReadFeaturedStickers <telectron.raw.types.UpdateReadFeaturedStickers>`
            - :obj:`UpdateReadHistoryInbox <telectron.raw.types.UpdateReadHistoryInbox>`
            - :obj:`UpdateReadHistoryOutbox <telectron.raw.types.UpdateReadHistoryOutbox>`
            - :obj:`UpdateReadMessagesContents <telectron.raw.types.UpdateReadMessagesContents>`
            - :obj:`UpdateRecentStickers <telectron.raw.types.UpdateRecentStickers>`
            - :obj:`UpdateSavedGifs <telectron.raw.types.UpdateSavedGifs>`
            - :obj:`UpdateServiceNotification <telectron.raw.types.UpdateServiceNotification>`
            - :obj:`UpdateStickerSets <telectron.raw.types.UpdateStickerSets>`
            - :obj:`UpdateStickerSetsOrder <telectron.raw.types.UpdateStickerSetsOrder>`
            - :obj:`UpdateTheme <telectron.raw.types.UpdateTheme>`
            - :obj:`UpdateUserName <telectron.raw.types.UpdateUserName>`
            - :obj:`UpdateUserPhone <telectron.raw.types.UpdateUserPhone>`
            - :obj:`UpdateUserPhoto <telectron.raw.types.UpdateUserPhoto>`
            - :obj:`UpdateUserStatus <telectron.raw.types.UpdateUserStatus>`
            - :obj:`UpdateUserTyping <telectron.raw.types.UpdateUserTyping>`
            - :obj:`UpdateWebPage <telectron.raw.types.UpdateWebPage>`
    """

    QUALNAME = "telectron.raw.base.Update"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.telectron.org/telegram/base/update")
