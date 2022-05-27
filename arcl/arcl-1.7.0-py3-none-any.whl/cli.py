#!/usr/bin/env python
import os
import re
import subprocess
import json

import click
from click.exceptions import ClickException
from cookiecutter.main import cookiecutter

from arcl import __version__
from arcl.auth import (
    AUTH_ACTIONS,
    AUTH_ACTIONS_GET_TOKEN,
    AUTH_ACTIONS_LOGIN,
    AUTH_ACTIONS_LOGOUT,
    AUTH_ACTIONS_SHOW,
    ArchimedesAuth,
    get_accepted_env,
)
from arcl.config import get_config_path

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])
COOKIECUTTER_TEMPLATE_GIT_URL = (
    "https://github.com/OptimeeringAS/archimedes-cookiecutter.git"
)
DEFAULT_AUTHOR_NAME = "Optimeering AS <dev@optimeering.com>"

# source for official regex for semver:
# https://semver.org/#is-there-a-suggested-regular-expression-regex-to-check-a-semver-string
SEMVER_REGEX = (
    r"(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)


class ConfigNotFoundException(Exception):
    pass


def get_author_name(user):
    name = user.get("name")
    email = user.get("email")
    username = user.get("username")

    for author_name in [name, email]:
        if author_name:
            return author_name

    return username


def get_python_version():
    errors = []

    for python_binary_name in ["python3", "python"]:
        try:
            python_version_output = subprocess.run(
                f"{python_binary_name} --version",
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
            )
            return _get_version_from_python_version_string(python_version_output)
        except subprocess.CalledProcessError as e:
            errors.append(e)

    print(
        "Error while trying to run `python --version`. Please make sure that python is installed and `python` "
        "is available in path."
    )
    print(errors)
    raise Exception("Error while trying to get available python version")


def _get_version_from_python_version_string(version_string):
    result = re.search(SEMVER_REGEX, version_string.stdout.decode("utf-8").strip())
    result_dict = result.groupdict()
    return f"{result_dict['major']}.{result_dict['minor']}.{result_dict['patch']}"


def get_config(project_name, env):
    """Create a config for the project"""
    author_name = DEFAULT_AUTHOR_NAME

    if os.path.exists(get_config_path(env)):
        config = json.loads(open(get_config_path(env), "r").read())
        author_name = get_author_name(config["user"])

    return {
        "project_name": project_name,
        "author_name": author_name,
        "python_version": get_python_version(),
    }


@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    """
    Welcome to The Archimedes CLI.

    \b
    Commands:
        arcl new         Create a new project
        arcl auth        Handle Archimedes authentication
        arcl version     Print the version number
    """
    pass


@cli.command(hidden=True)
@click.argument(
    "action", type=click.Choice(AUTH_ACTIONS, case_sensitive=False), required=True
)
@click.argument("organization", required=False)
@click.option(
    "--env",
    type=click.STRING,
    required=False,
    default="prod",
    help="Environment to setup",
)
def auth(action, organization, env):
    accepted_env = get_accepted_env()
    if env not in accepted_env:
        raise ClickException(f"env should be one of {accepted_env}")

    archimedes_auth = ArchimedesAuth(env)

    if action.lower() == AUTH_ACTIONS_LOGOUT:
        archimedes_auth.logout()
        return

    if action.lower() == AUTH_ACTIONS_LOGIN:
        archimedes_auth.login(organization)
        return

    if action.lower() == AUTH_ACTIONS_GET_TOKEN:
        click.echo(archimedes_auth.get_access_token())

    if action.lower() == AUTH_ACTIONS_SHOW:
        click.echo(archimedes_auth.show())


@cli.command(hidden=True)
@click.argument("name", required=True)
@click.option(
    "--template-version",
    "-t",
    "template_version",
    help=f"Version of the template to use. It can be a branch, name or tag of the git repo of "
    f"{COOKIECUTTER_TEMPLATE_GIT_URL}",
    default=None,
)
def new(name, template_version):
    """"""
    try:
        project_dir = cookiecutter(
            COOKIECUTTER_TEMPLATE_GIT_URL,
            checkout=template_version,
            extra_context=get_config(name, "prod"),
            no_input=True,
        )
    except ConfigNotFoundException as e:
        click.echo(e)
        return

    click.echo(f"\nYour new project has been created!")
    click.echo("")
    click.echo(f'$ cd "{project_dir}"')
    click.echo(f"$ python -m pip install wheel pip --upgrade")
    click.echo(f"$ poetry update --lock")
    click.echo(f"$ poetry install")
    click.echo("")
    click.echo(f"to get started.")
    click.echo("")


@cli.command(hidden=True)
def version():
    """
    Print the current version
    """
    click.echo(__version__)


if __name__ == "__main__":
    cli()
