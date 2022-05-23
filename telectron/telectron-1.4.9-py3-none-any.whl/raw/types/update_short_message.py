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

from io import BytesIO

from telectron.raw.core.primitives import Int, Long, Int128, Int256, Bool, Bytes, String, Double, Vector
from telectron.raw.core import TLObject
from telectron import raw
from typing import List, Union, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


class UpdateShortMessage(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~telectron.raw.base.Updates`.

    Details:
        - Layer: ``138``
        - ID: ``0x313bc7f8``

    Parameters:
        id: ``int`` ``32-bit``
        user_id: ``int`` ``64-bit``
        message: ``str``
        pts: ``int`` ``32-bit``
        pts_count: ``int`` ``32-bit``
        date: ``int`` ``32-bit``
        out (optional): ``bool``
        mentioned (optional): ``bool``
        media_unread (optional): ``bool``
        silent (optional): ``bool``
        fwd_from (optional): :obj:`MessageFwdHeader <telectron.raw.base.MessageFwdHeader>`
        via_bot_id (optional): ``int`` ``64-bit``
        reply_to (optional): :obj:`MessageReplyHeader <telectron.raw.base.MessageReplyHeader>`
        entities (optional): List of :obj:`MessageEntity <telectron.raw.base.MessageEntity>`
        ttl_period (optional): ``int`` ``32-bit``

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

    __slots__: List[str] = ["id", "user_id", "message", "pts", "pts_count", "date", "out", "mentioned", "media_unread", "silent", "fwd_from", "via_bot_id", "reply_to", "entities", "ttl_period"]

    ID = 0x313bc7f8
    QUALNAME = "types.UpdateShortMessage"

    def __init__(self, *, id: int, user_id: int, message: str, pts: int, pts_count: int, date: int, out: Union[None, bool] = None, mentioned: Union[None, bool] = None, media_unread: Union[None, bool] = None, silent: Union[None, bool] = None, fwd_from: "raw.base.MessageFwdHeader" = None, via_bot_id: Union[None, int] = None, reply_to: "raw.base.MessageReplyHeader" = None, entities: Union[None, List["raw.base.MessageEntity"]] = None, ttl_period: Union[None, int] = None) -> None:
        self.id = id  # int
        self.user_id = user_id  # long
        self.message = message  # string
        self.pts = pts  # int
        self.pts_count = pts_count  # int
        self.date = date  # int
        self.out = out  # flags.1?true
        self.mentioned = mentioned  # flags.4?true
        self.media_unread = media_unread  # flags.5?true
        self.silent = silent  # flags.13?true
        self.fwd_from = fwd_from  # flags.2?MessageFwdHeader
        self.via_bot_id = via_bot_id  # flags.11?long
        self.reply_to = reply_to  # flags.3?MessageReplyHeader
        self.entities = entities  # flags.7?Vector<MessageEntity>
        self.ttl_period = ttl_period  # flags.25?int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "UpdateShortMessage":
        flags = Int.read(b)
        
        out = True if flags & (1 << 1) else False
        mentioned = True if flags & (1 << 4) else False
        media_unread = True if flags & (1 << 5) else False
        silent = True if flags & (1 << 13) else False
        id = Int.read(b)
        
        user_id = Long.read(b)
        
        message = String.read(b)
        
        pts = Int.read(b)
        
        pts_count = Int.read(b)
        
        date = Int.read(b)
        
        fwd_from = TLObject.read(b) if flags & (1 << 2) else None
        
        via_bot_id = Long.read(b) if flags & (1 << 11) else None
        reply_to = TLObject.read(b) if flags & (1 << 3) else None
        
        entities = TLObject.read(b) if flags & (1 << 7) else []
        
        ttl_period = Int.read(b) if flags & (1 << 25) else None
        return UpdateShortMessage(id=id, user_id=user_id, message=message, pts=pts, pts_count=pts_count, date=date, out=out, mentioned=mentioned, media_unread=media_unread, silent=silent, fwd_from=fwd_from, via_bot_id=via_bot_id, reply_to=reply_to, entities=entities, ttl_period=ttl_period)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 1) if self.out else 0
        flags |= (1 << 4) if self.mentioned else 0
        flags |= (1 << 5) if self.media_unread else 0
        flags |= (1 << 13) if self.silent else 0
        flags |= (1 << 2) if self.fwd_from is not None else 0
        flags |= (1 << 11) if self.via_bot_id is not None else 0
        flags |= (1 << 3) if self.reply_to is not None else 0
        flags |= (1 << 7) if self.entities else 0
        flags |= (1 << 25) if self.ttl_period is not None else 0
        b.write(Int(flags))
        
        b.write(Int(self.id))
        
        b.write(Long(self.user_id))
        
        b.write(String(self.message))
        
        b.write(Int(self.pts))
        
        b.write(Int(self.pts_count))
        
        b.write(Int(self.date))
        
        if self.fwd_from is not None:
            b.write(self.fwd_from.write())
        
        if self.via_bot_id is not None:
            b.write(Long(self.via_bot_id))
        
        if self.reply_to is not None:
            b.write(self.reply_to.write())
        
        if self.entities:
            b.write(Vector(self.entities))
        
        if self.ttl_period is not None:
            b.write(Int(self.ttl_period))
        
        return b.getvalue()
