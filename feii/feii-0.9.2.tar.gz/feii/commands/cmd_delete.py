#!/usr/bin/python3

import click
from feii.cli import DeleteCLI

@click.command(
  cls=DeleteCLI,
  short_help='Deletion of empty indexes.',
  epilog="Run 'feii delete COMMAND --help' for more information on a command."
)
def cli():
  """Deletion of empty indexes"""
