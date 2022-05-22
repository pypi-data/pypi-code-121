from typing import List, Optional, Union, Dict

from telegram_types.types import User, Animation, Audio, Document, Photo, Video, Sticker, \
    Game, Voice, VideoNote, Contact, Location, Venue, WebPage, Poll, Dice, Reaction
from telegram_types.base import Base
from telegram_types.types.keyboard import InlineKeyboardMarkup, ReplyKeyboardMarkup, \
    ReplyKeyboardRemove, ForceReply


class ServiceMessage(Base):
    id: int
    chat: 'Chat'
    outgoing: Optional[bool]
    from_user: Optional[User]
    sender_chat: Optional['Chat']

    new_chat_members: Optional[List[User]]
    left_chat_member: Optional[User]
    new_chat_title: Optional[str]
    new_chat_photo: Optional[Photo]
    delete_chat_photo: Optional[bool]
    group_chat_created: Optional[bool]
    chat_created: Optional[bool]
    migrate_to_chat_id: Optional[int]
    migrate_from_chat_id: Optional[int]
    pinned_message: Optional['Message']
    game_high_score: Optional[Dict]
    voice_chat_scheduled: Optional[Dict]
    voice_chat_started: Optional[Dict]
    voice_chat_ended: Optional[Dict]
    voice_chat_members_invited: Optional[Dict]


class Message(Base):
    id: int
    chat: 'Chat'
    outgoing: Optional[bool]
    date: Optional[int]
    edit_date: Optional[int]
    from_user: Optional[User]
    sender_chat: Optional['Chat']
    views: Optional[int]
    via_bot: Optional[User]

    has_protected_content: Optional[bool]
    forward_from: Optional[User]
    forward_sender_name: Optional[str]
    forward_from_chat: Optional['Chat']
    forward_from_message_id: Optional[int]
    forward_signature: Optional[str]
    forward_date: Optional[int]
    reply_to_message: Optional[Union['Message', ServiceMessage]]
    media_group_id: Optional[int]
    author_signature: Optional[str]
    reply_markup: Optional[Dict]
    reply_markup: Optional[Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply]]
    reactions: Optional[List[Reaction]]

    text: Optional[str]
    audio: Optional[Audio]
    document: Optional[Document]
    photo: Optional[Photo]
    sticker: Optional[Sticker]
    animation: Optional[Animation]
    game: Optional[Game]
    video: Optional[Video]
    voice: Optional[Voice]
    video_note: Optional[VideoNote]
    contact: Optional[Contact]
    location: Optional[Location]
    venue: Optional[Venue]
    web_page: Optional[WebPage]
    poll: Optional[Poll]
    dice: Optional[Dice]

    @classmethod
    def from_telegram_type_dict(cls, obj) -> dict:
        cls_dict = super().from_telegram_type_dict(obj)
        cls_dict['text'] = obj.html_text
        return cls_dict


from telegram_types.types.chat import Chat

ServiceMessage.update_forward_refs()
Message.update_forward_refs()
