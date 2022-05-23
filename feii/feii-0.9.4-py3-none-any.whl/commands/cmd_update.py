#!/usr/bin/python3

import click
from feii.cli import UpdateCLI

@click.command(
  cls=UpdateCLI,
  short_help='Update index settings.',
  epilog="Run 'feii update COMMAND --help' for more information on a command."
)
def cli():
  """Update index settings"""
