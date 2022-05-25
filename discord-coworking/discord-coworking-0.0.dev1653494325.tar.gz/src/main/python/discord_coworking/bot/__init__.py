from discord import Client
from dataclasses import dataclass
from discord.user import User
from discord.message import Message

from discord_coworking.bot.api import MessageHandler
from discord_coworking.bot.handler import MessageHandlerChain
from discord_coworking.command.predicate import Predicate, E


@dataclass()
class NotMySelf(Predicate[Message]):
    client: Client

    def __call__(self, e: Message) -> bool:
        return e.author.id != self.client.user.id


@dataclass()
class StartByMentioningMe(Predicate[Message]):
    client: Client

    def __call__(self, e: Message) -> bool:
        mention = f'<@!{self.client.user.id}>'
        return e.content.startswith(mention)


class CoworkingBot(Client):
    message_handler: MessageHandlerChain

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message_handler = MessageHandlerChain(
            handlers=[],
            predicate=NotMySelf(self),
        )

    async def on_message(self, message: Message):
        await self.message_handler(self, message)
