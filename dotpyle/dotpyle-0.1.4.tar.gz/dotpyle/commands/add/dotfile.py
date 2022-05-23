import click

from dotpyle.decorators.pass_config_manager import pass_config_manager
from dotpyle.decorators.pass_repo_handler import pass_repo_handler
from dotpyle.decorators.pass_logger import pass_logger
from dotpyle.services.logger import Logger
from dotpyle.services.config_manager import ConfigManager
from dotpyle.services.repo_handler import RepoHandler
from dotpyle.objects.dotfile import Dotfile
from dotpyle.objects.profile import Profile

# FIXME: when config file is empty, an error is returned
# TypeError: argument of type 'NoneType' is not iterable
@click.command()
@click.help_option(help="Add file to dotpyle")
@click.argument("name")
@click.option(
    "--profile", "-p", default="default", help="Profile name, must exist"
)
@click.option("--root", "-r", default="~", help="Root path")
@click.option(
    "--path",
    multiple=True,
    help="Program dotfiles paths starting from root path",
)
# TODO: make this optional and add everything inside root
@click.option(
    "--pre",
    multiple=True,
    help="Bash command(s) to be executed before installing configuration",
)
@click.option(
    "--post",
    multiple=True,
    help="Bash command(s) to be executed after installing configuration",
)
@click.option(
    "--not-install",
    default=False,
    is_flag=True,
    help=(
        "Add files to Dotpyle repo and remove them from original location"
        " (useful if user wants to install it afterwards, see dotpyle install)"
    ),
)
@pass_config_manager
@pass_repo_handler
@pass_logger
# @click.option("--pre-hook", multiple=True,  help="Program dotfiles paths starting from root path")
def dotfile(
    logger: Logger,
    repo_handler: RepoHandler,
    manager: ConfigManager,
    name: str,
    profile: str,
    root: str,
    path: list[str],
    pre: list[str],
    post: list[str],
    not_install: bool,
):
    """ Add DOTFILE to KEY group on Dotpyle tracker TBD """
    print(name, profile, root, path, pre, post)
    # Convert tuples to lists
    paths = list(path)
    pre_commands = list(pre)
    post_commands = list(post)

    try:
        dotfile = manager.get_dotfile(name)
    except:
        dotfile = Dotfile(program_name=name)

    print('dotfile')
    profile_data = Profile(dotfile_name=name, profile_name=profile, paths=paths, root=root, pre=pre_commands, post=post_commands)
    profile_data.linked = not not_install
    logger.log(profile_data._get_tree())

    manager.set_dotfile(dotfile.add_profile(profile_data))


    # When new key is added to dotpyle, a commit should be generated
    # (adding new files), to keep consistency between yaml and repo

    # repo_handler.add(added_paths, config_file_changed=True)
    # commit_message = "[dotpyle]: added {} on {} profile on {} program".format(
        # added_paths, profile, name
    # )
    # repo_handler.commit(commit_message)

    # if not not_install:
        # config_handler.install_key(
            # key_name=name,
            # profile_name=profile,
            # process_pre=False,
            # process_post=False,
        # )
        # local_handler.install_profile(name, profile)
        # local_handler.save(local_handler.config)
