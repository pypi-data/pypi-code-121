#!/usr/bin/python3

import click
from feii.cli import RolloverCLI

@click.command(
  cls=RolloverCLI,
  short_help='Rollover the indexes.',
  epilog="Run 'feii rollover COMMAND --help' for more information on a command."
)
def cli():
  """Rollover the indexes"""
