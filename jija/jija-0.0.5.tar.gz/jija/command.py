import asyncio
import inspect

from tortoise import Tortoise


class Command:
    def __init__(self):
        self.loop = asyncio.get_event_loop()

    async def prepare(self):
        from jija.config import DatabaseConfig
        DatabaseConfig.load()

        await Tortoise.init(config=DatabaseConfig.get_config())

    def run(self):
        asyncio.get_event_loop().run_until_complete(self.prepare())

        if inspect.iscoroutinefunction(self.handle):
            self.loop.run_until_complete(self.handle())
        else:
            self.handle()

    def handle(self):
        raise NotImplementedError()
