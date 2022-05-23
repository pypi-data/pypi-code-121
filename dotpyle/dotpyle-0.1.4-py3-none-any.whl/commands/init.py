import click
from git import Repo
from os import mkdir, path, sys
from shutil import rmtree
from dotpyle.utils.path import get_default_path
from dotpyle.utils.url import get_default_url


@click.command()
@click.option(
    "-u",
    "--url",
    required=True,
    help="Git url of existing repo (GitHub, GitLab, ...)",
)
@click.option(
    "-p",
    "--protocol",
    required=True,
    type=click.Choice(["ssh", "https"]),
    help=(
        "Protocol used to clone the repository. Currently only Git and HTTPS"
        "are supported (like Github and Gitlab)."
    ),
)
@click.option(
    "-t",
    "--token",
    required=False,
    help=(
        "Token could be used to clone a repository if it is private and the"
        "protocol is HTTPS. If the repository is private but no token provided,"
        "it will probably prompt for username/password (depends on service)."
    ),
)
@click.option(
    "-b",
    "--branch",
    required=False,
    help=(
        "Desired branch of the repository. If not provided, the `default` "
        "branch will be used."
    ),
)
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help=(
        "Force init of the package. This results that everything that cause an"
        "error will be forced to work even if that means that something will be"
        "erased."
    ),
)
# TODO copy gitignore template to default_path
def init(url: str, protocol, token: str, branch: str, force: bool):
    """
    This command will clone an existing Git repository on
    ${XDG_CONFIG_HOME}/dotpyle and will check if this repo contains a
    dotpyle.yml config file, if not, a template config file will be created.
    """
    default_path = get_default_path()

    # Check if dotpyle config file exist
    if path.exists(default_path):
        if force:
            # click.secho(
            #     "Forcing operation. Make sure you know what you are doing!",
            #     fg="red",
            # )
            # click.secho("Removing config folder...", fg="red")
            rmtree(default_path)
    else:
        # click.secho("Folder already exists.", fg="red")
        # click.secho(
        #     "If this is an error, please check folder at {0} or try apply instead of init.\nOtherwise use -f/--force instead".format(
        #         default_path
        #     ),
        #     fg="red",
        # )
        sys.exit(1)

    url = get_default_url(url, protocol, token)
    repository = Repo.clone_from(url, default_path, progress=None)

    # Check if dotpyle exist

    # dotpyle_path = get_configuration_path()
    # if not path.isfile(dotpyle_path):
    # # Create dotpyle config file
    # dotpyle_handler = open(dotpyle_path, "w+")
    # # TODO copy default file to config file
    # template = eval(open("dotpyle/services/template.py", "r").read()) # TODO
    # dotpyle_handler.write(template)
    # dotpyle_handler.close()

    # TODO: Start configuration process...
