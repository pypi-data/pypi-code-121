from email.message import EmailMessage
from typing import Protocol


class EmailSenderProtocol(Protocol):
    async def send(self, _message: EmailMessage):
        ...
