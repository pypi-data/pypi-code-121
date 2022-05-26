"""Config

Allows users to get values from their Sym Flow config
"""

import click
from sym.shared.cli.helpers.sym_group import SymGroup

from sym.flow.cli.helpers.global_options import GlobalOptions

from .config_get import config_get
from .config_set import config_set


@click.group(cls=SymGroup, short_help="Interact with the Sym config file", hidden=True)
@click.make_pass_decorator(GlobalOptions, ensure=True)
def config(options: GlobalOptions) -> None:
    """Operations on the config file"""
    # For internal use only


config.add_command(config_get)
config.add_command(config_set)
