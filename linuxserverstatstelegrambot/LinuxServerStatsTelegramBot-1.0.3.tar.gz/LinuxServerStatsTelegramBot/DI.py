import os
from typing import Union

from LinuxServerStatsTelegramBot.sender.Sender import Sender


class DI:
    sender: Sender = None
    actual_sender: Sender = None

    @classmethod
    def set_sender(cls, sender: Sender) -> None:
        cls.sender = sender

    @classmethod
    def get_sender(cls) -> Sender:
        return cls.sender

    @classmethod
    def set_sender_temporarily(cls, sender: Sender) -> None:
        if cls.sender and isinstance(cls.sender, Sender):
            cls.actual_sender = cls.sender
        cls.sender = sender

    @classmethod
    def set_original_sender(cls) -> None:
        if cls.actual_sender and isinstance(cls.actual_sender, Sender):
            cls.sender = cls.actual_sender

    @staticmethod
    def get_server_name() -> str:
        server_alias = os.getenv("LSSTB_SERVER_ALIAS", "Unamed Server")
        return server_alias

    @staticmethod
    def project_root() -> str:
        return os.path.dirname(os.path.abspath(__file__))

    @staticmethod
    def get_tg_bot_token() -> str:
        token = os.getenv("LSSTB_BOT")
        return token

    @staticmethod
    def get_tg_chat_id() -> Union[str, int]:
        chat_id = os.getenv("LSSTB_CHAT")
        return chat_id
