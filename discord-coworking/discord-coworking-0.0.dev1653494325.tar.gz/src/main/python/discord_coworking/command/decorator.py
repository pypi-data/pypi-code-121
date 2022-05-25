import functools
from dataclasses import dataclass

from discord import Client as DiscordClient

from discord_coworking.command.api import UndoableResult, Result, Command
from discord_coworking.command.batch import BatchResult


@dataclass()
class UndoableResultImpl(UndoableResult):
    result: Result = None

    async def undo(self, client: DiscordClient):
        self.logger.debug(f'Undoing command {self.command}')
        return await self.result.undo(client)

    @classmethod
    def create(cls, command: Command, result: Result):
        return cls(
            command=command,
            result=result,
        )


def async_batch(fn):
    @functools.wraps(fn)
    async def wrapper(command, *args, **kwargs) -> Result:
        results = []
        try:
            async for result in fn(command, *args, **kwargs):
                results.append(result)
        except Exception as ex:
            client = kwargs.get('client', None)
            if client is None:
                client = args[0]
            for result in results[::-1]:
                await result.undo(client)
            raise ex
        return UndoableResultImpl.create(command, BatchResult(results[::-1]))

    return wrapper
