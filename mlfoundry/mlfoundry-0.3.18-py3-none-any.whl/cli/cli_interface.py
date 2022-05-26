import logging
import os

import click

from mlfoundry.cli.commands import download, login

logger = logging.getLogger(__name__)


@click.group()
@click.version_option("1.0.0")
def mlfoundry_cli():
    """MlFoundry CLI"""
    click.secho("MlFoundry CLI", bold=True, fg="green")


def create_mlfoundry_cli():
    """Generates CLI by combining all subcommands into a main CLI and returns in
    Returns:
        function: main CLI functions will all added sub-commands
    """
    _cli = mlfoundry_cli
    _cli.add_command(ui)
    _cli.add_command(download)
    _cli.add_command(login)
    return _cli()


@click.command(
    help="Generate MLFoundry Dashboard",
    short_help="Generate MLFoundry Dashboard",
)
@click.option(
    "-p",
    "--path",
    type=click.Path(exists=True, dir_okay=True, readable=True),
    default=os.path.abspath("."),
)
def ui(path: str):
    os.system(f"mlfoundry_ui start-dashboard -p {path}")
