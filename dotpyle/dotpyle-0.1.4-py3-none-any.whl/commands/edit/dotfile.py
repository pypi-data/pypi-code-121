import click
from os import system, path
from shutil import copy2
from tempfile import gettempdir
from dotpyle.utils.path import get_configuration_path, get_dotpyle_readme_path
from dotpyle.services.config_handler import ConfigHandler
from dotpyle.services.file_handler import FileHandler
from dotpyle.utils import constants
from dotpyle.decorators.pass_logger import pass_logger
from dotpyle.services.logger import Logger
from dotpyle.services.config_manager import ConfigManager

from dotpyle.utils.autocompletion import ProfileVarType, DotfileNamesVarType
from rich.prompt import Prompt


@click.command()
@click.argument("name")
@pass_logger
def dotfile(logger: Logger, name: str):
    manager = ConfigManager(logger)
    dotfile = manager.get_dotfile(name)
    logger.log(dotfile._get_tree())
    profile_options = dotfile.get_profile_names()
    profile_name = Prompt.ask(
        "Enter profile to edit",
        default=profile_options[0],
        choices=profile_options,
    )
    profile = dotfile.get_profile(profile_name)
    for action in profile._get_pending_actions():
        print(action)
    # answer = Prompt.ask("1. Add new path\n2. Delete existing path\n3. Edit pre\n4. Edit post\nSelect")
    # if answer == '1':
    # Prompt.ask("New path")
    # print(profile)
