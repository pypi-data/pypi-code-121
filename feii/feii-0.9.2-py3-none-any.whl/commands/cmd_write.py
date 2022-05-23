#!/usr/bin/python3

import click
from feii.cli import WriteCLI

@click.command(
  cls=WriteCLI,
  short_help='Correction of writing in indices.',
  epilog="Run 'feii write COMMAND --help' for more information on a command."
)
def cli():
  """Correction of writing in indices"""
