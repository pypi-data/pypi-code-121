import asyncio
from dataclasses import dataclass
from typing import Callable, Awaitable, List

from discord import Client
from discord.message import Message

from discord_coworking.bot.api import MessageHandler
from discord_coworking.command.predicate import Predicate, ANY


@dataclass()
class MessageHandlerNode(MessageHandler):
    handler: Callable[[Client, Message], Awaitable]
    predicate: Predicate[Message] = ANY

    def accept(self, message: Message) -> bool:
        return self.predicate(message)

    async def handle(self, client: Client, message: Message):
        await self.handler(client, message)


@dataclass()
class MessageHandlerChain(MessageHandler):
    handlers: List[MessageHandler]
    predicate: Predicate[Message] = ANY

    def accept(self, message: Message) -> bool:
        return self.predicate(message)

    async def handle(self, client: Client, message: Message):
        for handler in self.handlers:
            if handler.accept(message):
                asyncio.create_task(handler.handle(client, message))
