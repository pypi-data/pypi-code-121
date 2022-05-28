import os

import aerich
from jija.command import Command


class Migrate(Command):
    async def handle(self):
        from jija.apps import Apps
        from jija.config import DatabaseConfig

        for app_name in Apps.apps:
            command = aerich.Command(tortoise_config=DatabaseConfig.get_config(), app=app_name)
            if not os.path.exists(os.path.join(os.getcwd(), 'migrations', app_name)):
                await command.init_db(safe=True)
            else:
                await command.init()
                await command.migrate()
