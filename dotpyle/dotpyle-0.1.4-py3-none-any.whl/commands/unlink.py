import click
from dotpyle.decorators.pass_config_manager import pass_config_manager
from dotpyle.decorators.pass_logger import pass_logger
from dotpyle.utils.autocompletion import ProfileVarType, DotfileNamesVarType
from dotpyle.services.logger import Logger
from dotpyle.services.config_manager import ConfigManager


@click.command()
@click.argument("name", type=DotfileNamesVarType())
@click.option(
    "--profile",
    "-p",
    default="default",
    help="profile name",
    type=ProfileVarType(),
)
@pass_config_manager
@pass_logger
def unlink(
    logger: Logger,
    manager: ConfigManager,
    name: str,
    profile: str,
):
    """
    Unlink dotfiles for a program (and profile). Dotfiles will not
    be removed from Dotpyle repository
    """

    profile_data = manager.get_dotfile(name).get_profile(profile)
    if not profile_data.linked:
        logger.failure(
            "Profile {} is not installed for {}".format(profile, name)
        )
        return

    profile_data.linked = False
    logger.success("{} dotfiles uninstalled".format(name))
