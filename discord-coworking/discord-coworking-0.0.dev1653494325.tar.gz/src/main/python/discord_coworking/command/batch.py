import logging
from dataclasses import dataclass, field
from logging import Logger
from typing import Sequence

from discord import Client as DiscordClient

from discord_coworking.command.api import Command, Result

__logger__: Logger = logging.getLogger(__name__)


@dataclass()
class BatchResult(Result):
    results: Sequence[Result] = field(default_factory=list)
    logger: Logger = field(default=__logger__)

    async def undo(self, client: DiscordClient):
        for result in self.results:
            try:
                await result.undo(client)
            except Exception as ex:
                self.logger.error(exc_info=ex)


@dataclass()
class BatchCommand(Command):
    commands: Sequence[Command] = field(default_factory=list)

    async def do(self, client: DiscordClient) -> Result:
        results = []
        for command in self.commands:
            results.append(await command.do(client))
        return BatchResult(results[::-1])

    @classmethod
    def create(cls, *commands: Command) -> 'BatchCommand':
        return cls(commands)
