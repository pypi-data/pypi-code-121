import click

from .cmds.clean import clean
from .cmds.infer import infer
from .cmds.init import init
from .cmds.push import push
from .cmds.test import test


@click.group()
def cli():
    """
    tiyaro - Tiyaro Cli
    """
    pass


cli.add_command(init)
cli.add_command(push)
cli.add_command(test)
cli.add_command(infer)
cli.add_command(clean)
