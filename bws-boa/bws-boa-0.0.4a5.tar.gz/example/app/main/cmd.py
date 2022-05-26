
from app import cmd, app
import click


@cmd.command("main__create")
# @click.argument('arg')
def main__create():
    print(app.cli.list_commands({}))
    print(app.cli.get_command({}, "cmd"))

