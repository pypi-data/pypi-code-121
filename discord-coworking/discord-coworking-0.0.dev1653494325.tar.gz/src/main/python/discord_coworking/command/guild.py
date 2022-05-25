import logging
from dataclasses import dataclass, field
from logging import Logger

from discord import Client as DiscordClient
from discord import Guild

from discord_coworking.command.api import Command, Result
from discord_coworking.command.decorator import async_batch
from discord_coworking.command.predicate import ByAttributesPredicate, Predicate, ANY

__logger__: Logger = logging.getLogger(__name__)


class GuildPredicate(ByAttributesPredicate[Guild]):

    @classmethod
    def of(cls, guild: Guild):
        return cls.create(id=guild.id)


@dataclass()
class GuildResult(Result):
    guild: Predicate[Guild] = ANY

    async def undo(self, client: DiscordClient):
        for guild in self.guild.filter(client.guilds):
            await self.undo_on_guild(client, guild)

    async def undo_on_guild(self, client: DiscordClient, guild: Guild):
        raise NotImplementedError()


@dataclass()
class GuildCommand(Command):
    guild: Predicate[Guild] = ANY
    logger: Logger = field(default=__logger__)

    @async_batch
    async def do(self, client: DiscordClient) -> Result:
        for guild in self.guild.filter(client.guilds):
            self.logger.info(f'Running command {self} on guild {guild.name}({guild.id})')
            yield await self.do_on_guild(client, guild)

    async def do_on_guild(self, client: DiscordClient, guild: Guild) -> Result:
        raise NotImplementedError()
