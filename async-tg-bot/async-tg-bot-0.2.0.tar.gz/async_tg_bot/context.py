from collections import defaultdict
from contextvars import ContextVar
from dataclasses import dataclass

from .types import *

UPDATE = ContextVar('UPDATE')


@dataclass
class Context:
    token: str = None
    parse_mode: str = None
    disable_web_page_preview: bool = None
    disable_notification: bool = None
    protect_content: bool = None

    storage = defaultdict(dict)

    def __setattr__(self, key, value):
        if key in __class__.__dict__:
            super().__setattr__(key, value)
        else:
            # TODO: what if chat_id or user_id is None
            main_key = (self.chat_id, self.user_id)
            self.storage[main_key][key] = value

    def __getattr__(self, item):
        main_key = (self.chat_id, self.user_id)
        return self.storage[main_key][item]

    @property
    def state(self) -> str | None:
        """User.state"""
        main_key = (self.chat_id, self.user_id)
        return self.storage[main_key].get('state')

    @state.setter
    def state(self, value: str):
        """User.state"""
        main_key = (self.chat_id, self.user_id)
        self.storage[main_key]['state'] = value

    @property
    def update(self) -> Update | None:
        """Update"""
        return UPDATE.get(None)

    @update.setter
    def update(self, value: Update):
        UPDATE.set(value)

    @property
    def callback_query(self) -> CallbackQuery | None:
        """CallbackQuery"""
        value = None

        if update := self.update:
            value = update.callback_query

        return value

    @property
    def callback_query_id(self) -> str | None:
        """CallbackQuery.id"""
        value = None

        if callback_query := self.callback_query:
            value = callback_query.id

        return value

    @property
    def message(self) -> Message | None:
        """Message | ChannelPost | CallbackQuery.message"""
        value = None

        if update := self.update:
            value = update.message or update.channel_post

            if value is None:
                if callback_query := self.callback_query:
                    value = callback_query.message

        return value

    @property
    def message_id(self) -> int | None:
        """Message.id | ChannelPost.id | CallbackQuery.message.id"""
        value = None

        if message := self.message:
            value = message.message_id

        return value

    @property
    def chat(self) -> Chat | None:
        """Message.chat | ChannelPost.chat | CallbackQuery.chat"""

        value = None

        if message := self.message:
            value = message.chat

        return value

    @property
    def chat_id(self) -> int | None:
        """Message.chat.id | ChannelPost.chat.id | CallbackQuery.chat.id"""
        value = None

        if chat := self.chat:
            value = chat.id

        return value

    @property
    def text(self) -> str | None:
        """Message.text | ChannelPost.text | CallbackQuery.message.text"""
        value = None

        if message := self.message:
            value = message.text

        return value

    @property
    def data(self) -> str | None:
        """CallbackQuery.data"""

        value = None

        if callback_query := self.callback_query:
            value = callback_query.data

        return value

    @property
    def user(self) -> User | None:
        """Message.user | CallbackQuery.user"""
        value = None

        if update := self.update:
            if message := update.message:
                value = message.from_user
            elif callback_query := update.callback_query:
                value = callback_query.from_user

        return value

    @property
    def user_id(self) -> int | None:
        """Message.user.id | CallbackQuery.user.id"""
        value = None

        if user := self.user:
            value = user.id

        return value
