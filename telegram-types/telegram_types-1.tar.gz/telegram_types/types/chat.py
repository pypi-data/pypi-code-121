from typing import Optional, List
from enum import auto

from telegram_types.utils import AutoName
from telegram_types.types import Restriction, ChatPhoto
from telegram_types.base import Base


class Type(str, AutoName):
    private = auto()
    bot = auto()
    group = auto()
    supergroup = auto()
    channel = auto()


class ChatPermissions(Base):
    can_send_messages: Optional[bool]
    can_send_media_messages: Optional[bool]
    can_send_other_messages: Optional[bool]
    can_send_polls: Optional[bool]
    can_add_web_page_previews: Optional[bool]
    can_change_info: Optional[bool]
    can_invite_users: Optional[bool]
    can_pin_messages: Optional[bool]


class Chat(Base):
    id: int
    type: Type
    is_verified: Optional[bool]
    is_restricted: Optional[bool]
    is_creator: Optional[bool]
    is_scam: Optional[bool]
    is_fake: Optional[bool]
    is_support: Optional[bool]
    title: Optional[str]
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    photo: Optional[ChatPhoto]
    bio: Optional[str]
    description: Optional[str]
    dc_id: Optional[int]
    has_protected_content: Optional[bool]
    invite_link: Optional[str]
    pinned_message: Optional['Message']
    sticker_set_name: Optional[str]
    can_set_sticker_set: Optional[bool]
    members_count: Optional[int]
    restrictions: Optional[List[Restriction]]
    permissions: Optional[ChatPermissions]
    distance: Optional[int]
    linked_chat: Optional['Chat']
    send_as_chat: Optional['Chat']
    available_reactions: Optional[List[str]]


from telegram_types.types.message import Message

Chat.update_forward_refs()