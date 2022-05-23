import click

from dotpyle.commands.edit.config import config
from dotpyle.commands.edit.readme import readme
from dotpyle.commands.edit.dotfile import dotfile


@click.group()
def edit():
    """ Manually edit Dotpyle internal files """
    pass


edit.add_command(config)
edit.add_command(readme)
edit.add_command(dotfile)
