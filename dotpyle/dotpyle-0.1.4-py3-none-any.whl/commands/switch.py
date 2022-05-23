import click
from dotpyle.utils.autocompletion import DotfileNamesVarType, ProfileVarType
from dotpyle.decorators.pass_config_handler import pass_config_handler
from dotpyle.decorators.pass_local_handler import pass_local_handler
from dotpyle.decorators.pass_logger import pass_logger
from dotpyle.decorators.pass_config_manager import pass_config_manager
from dotpyle.decorators.pass_repo_handler import pass_repo_handler
from dotpyle.services.logger import Logger
from dotpyle.services.config_manager import ConfigManager
from dotpyle.services.repo_handler import RepoHandler


@click.command()
@click.argument("name", type=DotfileNamesVarType())
@click.argument("profile", default='default', type=ProfileVarType())
@click.option("--pre", is_flag=True, help="Execute pre hooks")
@click.option("--post", is_flag=True, help="Execute post hooks")
@click.option("--hooks", is_flag=True, help="Execute pre and post hooks")
@click.option(
    "--create-profile",
    is_flag=True,
    help=(
        "Force profile creation when given profile does not exist for given"
        " program"
    ),
)
@pass_config_manager
@pass_repo_handler
@pass_logger
def switch(
    logger: Logger,
    repo_handler: RepoHandler,
    manager: ConfigManager,
    name: str,
    profile: str,
    pre: bool,
    post: bool,
    hooks: bool,
    create_profile,
):
    """Change profile for a given program"""


    dotfile = manager.get_dotfile(name)
    new_profile = dotfile.get_profile(profile)
    old_profile = dotfile.linked_profile
    if not old_profile:
        logger.failure(
            "Program '{}' in not currently linked'".format(name)
        )
        return

    if new_profile.linked:
        logger.failure(
            "Profile {} already installed for {}".format(profile, name)
        )
        return

    old_profile.linked = False
    new_profile.linked = True
    new_profile.process_pre = pre or hooks
    new_profile.process_post = post or hooks

    logger.success(
        "Switched profile '{}' to '{}' for {} ".format(
            old_profile, profile, name
        )
    )


    # if profile not in config_handler.get_profiles_for_name(name):
        # if not create_profile:
            # logger.failure(
                # "'{}' profile does not exist for '{}', use --create-profile to"
                # " create a new profile with current changes".format(
                    # profile, name
                # )
            # )
            # return

        # current_profile_path = config_handler.get_profile_paths(
            # name, old_profile
        # )
        # print(current_profile_path)
        # if repo_handler.check_changes(current_profile_path):
            # logger.failure("TODO: git changes")
            # return
