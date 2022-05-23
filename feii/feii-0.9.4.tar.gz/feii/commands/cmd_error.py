#!/usr/bin/python3

import click
from feii.cli import ErrorCLI

@click.command(
  cls=ErrorCLI,
  short_help='Correcting errors in indexes.',
  epilog="Run 'feii error COMMAND --help' for more information on a command."
)
def cli():
  """Correcting errors in indexes"""
