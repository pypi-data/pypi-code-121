from contextlib import suppress
from dataclasses import dataclass

from . import utils
from .types import Update


@dataclass
class Filter:
    pass

    def check(self, update: Update) -> bool:
        return bool(update)


@dataclass
class Message(Filter):

    def check(self, update: Update):
        return bool(update.message)


@dataclass
class Text(Filter):
    value: str

    def check(self, update: Update):
        try:
            return update.message.text == self.value
        except AttributeError:
            return False


@dataclass
class Command(Filter):
    value: str

    def check(self, update: Update):
        try:
            return update.message.text == f'/{self.value}'
        except AttributeError:
            return False


# @dataclass
# class TextPost(Filter):
#     def check(self, update):
#         pass

@dataclass
class UserId(Filter):
    value: int | list[int]

    def check(self, update: Update):
        user_id = None

        with suppress(AttributeError):
            if message := update.message:
                user_id = message.from_user.id
            elif callback_query := update.callback_query:
                user_id = callback_query.from_user.id

        return user_id in utils.listify(self.value)


@dataclass
class ChatType(Filter):
    value: str | list[str]

    def check(self, update: Update):
        chat_type = None

        with suppress(AttributeError):
            if message := update.message:
                chat_type = message.chat.type
            elif channel_post := update.channel_post:
                chat_type = channel_post.chat.type
            elif callback_query := update.callback_query:
                chat_type = callback_query.message.chat.type

        return chat_type in utils.listify(self.value)


@dataclass
class Data(Filter):
    value: str

    def check(self, update: Update):
        try:
            return update.callback_query.data == self.value
        except AttributeError:
            return False


@dataclass
class State(Filter):
    value: str

    def check(self, update: Update):
        from .loader import ctx

        chat_id = None
        user_id = None

        with suppress(AttributeError):
            if message := update.message:
                chat_id = message.chat.id
            elif channel_post := update.channel_post:
                chat_id = channel_post.chat.id
            elif callback_query := update.callback_query:
                chat_id = callback_query.message.chat.id

        with suppress(AttributeError):
            if message := update.message:
                user_id = message.from_user.id
            elif callback_query := update.callback_query:
                user_id = callback_query.from_user.id

        main_key = (chat_id, user_id)
        state = ctx.storage[main_key].get('state')

        return self.value == '*' or state == self.value
