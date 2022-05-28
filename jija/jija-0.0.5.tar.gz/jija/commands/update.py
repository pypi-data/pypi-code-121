import aerich
from jija.command import Command


class Update(Command):
    async def handle(self):
        from jija.apps import Apps
        from jija.config import DatabaseConfig

        for app_name in Apps.apps:
            command = aerich.Command(tortoise_config=DatabaseConfig.get_config(), app=app_name)
            await command.init()
            await command.upgrade()
