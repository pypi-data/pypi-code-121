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
@click.option("--no-pre", is_flag=True, help="Don't execute pre hooks")
@click.option("--no-post", is_flag=True, help="Don't execute post hooks")
@click.option(
    "--no-hooks", is_flag=True, help="Don't execute pre and post hooks"
)
@pass_config_manager
@pass_logger
def link(
    logger: Logger,
    manager: ConfigManager,
    name: str,
    profile: str,
    no_pre: bool,
    no_post: bool,
    no_hooks: bool,
):
    """Link dotfiles for a given program and profile (and optionally execute hooks)"""

    profile_data = manager.get_dotfile(name).get_profile(profile)
    if profile_data.linked:
        logger.failure(
            "Profile {} already installed for {}".format(profile, name)
        )
        return

    profile_data.linked = True
    profile_data.process_pre = not (no_pre or no_hooks)
    profile_data.process_post = not (no_post or no_hooks)

    logger.success("{} dotfiles installed".format(name))
