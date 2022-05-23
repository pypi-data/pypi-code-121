import click

from dotpyle.decorators.pass_config_handler import pass_config_handler
from dotpyle.decorators.pass_repo_handler import pass_repo_handler


@click.command()
@click.option("--name", "-n", default="", help="program name")
@click.option("--profile", "-p", default="default", help="profile name")
@click.option(
    "--path",
    multiple=True,
    help="Program dotfiles paths starting from root path",
)
@click.option("--message", "-m", help="commit message")
@pass_config_handler
@pass_repo_handler
# TODO: make path option name dependant
def commit(
    repo_handler,
    config_handler,
    name: str,
    profile: str,
    path: list[str],
    message,
):

    if not message:
        print("TODO: open default editor")

    # 1. Add files based on parameters
    if name == "":
        for name, profiles in config_handler.get_names_and_profiles():
            for prof in profiles:
                if profile == "" or profile == prof:
                    for source in config_handler.get_profile_paths(name, prof):
                        repo_handler.add(paths=source)

    else:
        print("One name")
        # Expand path tuple to list
        paths = [p for p in path]
        for prof in config_handler.get_profiles_for_name(name):
            if profile == "" or profile == prof:
                for source, _ in config_handler.get_calculated_paths(
                    name, profile
                ):
                    if profile == "" or paths == [] or source in paths:
                        repo_handler.add(paths=source)

    # 2. Proceed with commit
    repo_handler.commit(message)
