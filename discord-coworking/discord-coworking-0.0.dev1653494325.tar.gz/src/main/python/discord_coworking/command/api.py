import logging
from dataclasses import dataclass, field
from logging import Logger
from typing import Optional, TypeVar, Generic

from discord import Client as DiscordClient

__logger__: Logger = logging.getLogger(__name__)


class Result:

    async def undo(self, client: DiscordClient):
        raise NotImplementedError()


class Command:

    async def do(self, client: DiscordClient) -> Optional[Result]:
        raise NotImplementedError()


@dataclass
class UnundoableResult(Result):
    command: Command = None
    logger: Logger = field(default=__logger__)

    async def undo(self, client: DiscordClient):
        self.logger.warning(f'The command {self.command} cannot be undone')

    @classmethod
    def create(cls, command: Command):
        return cls(command)


C = TypeVar('C')


@dataclass()
class UndoableResult(Generic[C], Result):
    command: C = None
    logger: Logger = field(default=__logger__)

    async def undo(self, client: DiscordClient):
        raise NotImplementedError()
