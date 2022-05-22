from typing import List, Optional

from telegram_types.base import Base


class InlineKeyboardButton(Base):
    text: str
    callback_data: Optional[str]
    url: Optional[str]


class InlineKeyboardMarkup(Base):
    inline_keyboard: List[List[InlineKeyboardButton]]


class KeyboardButton(Base):
    text: str
    request_contact: Optional[bool]
    request_location: Optional[bool]


class ReplyKeyboardMarkup(Base):
    keyboard: List[List[KeyboardButton]]
    resize_keyboard: Optional[bool]
    one_time_keyboard: Optional[bool]
    selective: Optional[bool]
    placeholder: Optional[str]


class ReplyKeyboardRemove(Base):
    selective: Optional[bool]


class ForceReply(Base):
    selective: Optional[bool]
    placeholder: Optional[str]
