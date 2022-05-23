import click

from dotpyle.commands.add.dotfile import dotfile
from dotpyle.commands.add.script import script


@click.group()
def add():
    """
    Add dotfiles or scripts to Dotpyle manager
    """


add.add_command(dotfile)
add.add_command(script)
