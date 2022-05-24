import sys

from subprocess import check_output

import os

import click

from dnastack.cli.auth.commands import auth
from dnastack.cli.cli_config.commands import config_command_group
from dnastack.cli.collections.commands import collection_command_group
from dnastack.cli.dataconnect.commands import data_connect_command_group
from dnastack.cli.endpoints import endpoint_command_group
from dnastack.cli.files.commands import drs_command_group
from dnastack.cli.service_registry import registry_command_group
from dnastack.alpha.commands import alpha_command_group
from .constants import (
    __version__,
)

APP_NAME = 'dnastack'


@click.group(APP_NAME)
@click.version_option(__version__, message="%(version)s")
def dnastack():
    """
    DNAstack Client CLI

    https://www.dnastack.com
    """


@dnastack.command("version")
def get_version():
    """
    Show the version of CLI/library
    """
    library_version = (
        f"{check_output(['git', 'describe', '--abbrev=7']).decode().strip()} (dev)"
        if os.path.exists('.git')
        else __version__
    )
    python_version = str(sys.version).replace("\n", " ")
    click.echo(f'{APP_NAME} {library_version}', nl=False)
    click.secho(f' with Python {python_version}', dim=True)


# noinspection PyTypeChecker
dnastack.add_command(data_connect_command_group)
# noinspection PyTypeChecker
dnastack.add_command(config_command_group)
# noinspection PyTypeChecker
dnastack.add_command(drs_command_group)
# noinspection PyTypeChecker
dnastack.add_command(auth)
# noinspection PyTypeChecker
dnastack.add_command(collection_command_group)
# noinspection PyTypeChecker
dnastack.add_command(registry_command_group)
# noinspection PyTypeChecker
dnastack.add_command(endpoint_command_group)
# noinspection PyTypeChecker
dnastack.add_command(alpha_command_group)

if __name__ == "__main__":
    dnastack.main(prog_name="dnastack")
