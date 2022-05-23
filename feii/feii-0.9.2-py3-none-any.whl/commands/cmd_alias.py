#!/usr/bin/python3

import click
from feii.cli import AliasCLI

@click.command(
  cls=AliasCLI,
  short_help='Fix indexes without an alias.',
  epilog="Run 'feii alias COMMAND --help' for more information on a command."
)
def cli():
  """Fix indexes without an alias"""
