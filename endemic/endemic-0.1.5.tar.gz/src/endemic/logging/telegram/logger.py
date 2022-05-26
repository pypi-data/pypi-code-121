from urllib.request import urlopen
from urllib.parse import urlencode

from functools import wraps

from ..interface import LoggerInterface

API = 'https://api.telegram.org/bot{token}/{method}'


def decorator_add_header(title):
    def wrapper(f):
        @wraps(f)
        def wrapped(self, text: str):
            return f(self, '{emoji} <b>[{title}]</b>\n{text}'.format(emoji=title,
                                                                     title=self.message_title,
                                                                     text=text.replace('<', '&lt;')))

        return wrapped

    return wrapper


# todo: add button

class LoggerTelegram(LoggerInterface):

    # threads - number of pool threads
    def __init__(
            self,
            token,
            chat_id,
            title: str = '',
            level: str = LoggerInterface.DEBUG,
    ):
        self.__chat_id = chat_id
        self.__token = token
        self.__message_title = title
        self.__logging_level = level

    @decorator_add_header('👷')
    def debug(self, text, tag=None):
        self.__send_message(text) if self.__logging_level <= LoggerInterface.DEBUG else None

    @decorator_add_header('💚')
    def info(self, text, tag=None):
        self.__send_message(text) if self.__logging_level <= LoggerInterface.INFO else None

    @decorator_add_header('🔶')
    def warning(self, text, tag=None):
        self.__send_message(text) if self.__logging_level <= LoggerInterface.WARNING else None

    @decorator_add_header('🔴')
    def error(self, text, tag=None):
        self.__send_message(text) if self.__logging_level <= LoggerInterface.ERROR else None

    @decorator_add_header('🔥')
    def exception(self, text, tag=None):
        self.__send_message(text) if self.__logging_level <= LoggerInterface.ERROR else None

    @decorator_add_header('‼️')
    def critical(self, text, tag=None):
        self.__send_message(text) if self.__logging_level <= LoggerInterface.CRITICAL else None

    def __send_message(self, message, notify=True):
        return self.__telegram('sendMessage', {
            'text': message,
            'chat_id': self.__chat_id,
            'parse_mode': 'HTML',
            'disable_notification': not notify})

    def __telegram(self, name, data):
        urlopen(f"https://api.telegram.org/bot{self.__token}/{name}?{urlencode(data)}")

    @property
    def message_title(self) -> str:
        return self.__message_title

    @message_title.setter
    def message_title(self, value):
        self.__message_title = value
