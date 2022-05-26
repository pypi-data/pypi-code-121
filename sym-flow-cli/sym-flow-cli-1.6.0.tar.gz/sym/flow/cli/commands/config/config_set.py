"""Config Set

Set a value in the Sym Flow config.
"""

import click

from sym.flow.cli.helpers.global_options import GlobalOptions


@click.command(name="set", short_help="Set a config value")
@click.make_pass_decorator(GlobalOptions, ensure=True)
@click.argument("key")
@click.argument("value")
def config_set(options: GlobalOptions, key: str, value: str) -> None:
    """Set a config value in your local Sym Flow config file"""
    # For internal use only
    raise click.UsageError("The set operation is not currently supported.")
