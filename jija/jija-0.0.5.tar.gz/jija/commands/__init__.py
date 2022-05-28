from jija.commands.migrate import Migrate
from jija.commands.run import Run
from jija.commands.update import Update
from jija.commands.test import Test
from jija.commands.runprocess import RunProcess

COMMANDS = {
    'run': Run,
    'migrate': Migrate,
    'update': Update,
    'test': Test,
    'runprocess': RunProcess
}
