# Author: Snow Yang
# Date  : 2022/03/21

"""mdev entry point."""

from typing import Union, Any

import click

from mdev.build import build
from mdev.project_management import new, import_, deploy, sync, status
from mdev import log

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])

def get_version():
    from pkg_resources import get_distribution
    return get_distribution("mdev").version

def print_version(context: click.Context, param: Union[click.Option, click.Parameter], value: bool) -> Any:
    """Print the version of mbed-tools."""
    if not value or context.resilient_parsing:
        return
    click.echo(get_version())
    context.exit()

@click.group(context_settings=CONTEXT_SETTINGS)
@click.option(
    "--version",
    is_flag=True,
    callback=print_version,
    expose_value=False,
    is_eager=True,
    help="Display versions of all Mbed Tools packages.",
)
@click.option(
    "-v",
    "--verbose",
    default=0,
    count=True,
    help="Set the verbosity level, enter multiple times to increase verbosity.",
)
def cli(verbose: int) -> None:
    """The MXOS meta-tool."""
    log.set_verbosity(verbose)

cli.add_command(new, "new")
cli.add_command(import_, "import")
cli.add_command(deploy, "deploy")
cli.add_command(sync, "sync")
cli.add_command(build, "build")
cli.add_command(status, "status")
cli()