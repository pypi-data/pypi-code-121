"""Compute Shared Arguments plugin for VSS CLI (vss-cli)."""

import click

from vss_cli import autocompletion
from vss_cli.plugins.compute_plugins import callbacks

extra_config_arg = click.argument(
    'key-value',
    type=click.STRING,
    required=True,
    nargs=-1,
    callback=callbacks.process_options,
)
firmware_arg = click.argument(
    'firmware',
    shell_complete=autocompletion.vm_firmware,
    required=True,
    callback=callbacks.process_firmware,
)
