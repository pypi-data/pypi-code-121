import click
import os
import rich
from rich.text import Text
from rich.tree import Tree
from dotpyle.utils.autocompletion import DotfileNamesVarType, ProfileVarType
from dotpyle.decorators.pass_config_manager import pass_config_manager
from dotpyle.decorators.pass_logger import pass_logger
from dotpyle.utils.path import un_expanduser
from dotpyle.services.logger import Logger
from dotpyle.services.config_manager import ConfigManager


@click.command()
@click.argument("name", required=False, default=None, type=DotfileNamesVarType())
@click.option("--profile", "-p", default='', help="profile name", type=ProfileVarType())
@click.option(
    "--all", "-a", is_flag=True, help="list all dotfiles (linked or not)"
)
@pass_config_manager
@pass_logger
def ls(
    logger: Logger,
    manager: ConfigManager,
    name: str,
    profile: str,
    all: bool,
):
    """
    List dotfiles managed by Dotpyle
    """

    tree = Tree(
        "🌲 [b green]dotfiles",
        highlight=True,
        guide_style="bold bright_blue",
    )

    only_linked = not all
    for dotfile in manager.query_dotfiles(name):
        profile_tree = dotfile.get_tree(profile_filter=profile, only_linked=only_linked)
        if len(profile_tree.children) > 0:
            tree.add(profile_tree)
    logger.print(tree)

