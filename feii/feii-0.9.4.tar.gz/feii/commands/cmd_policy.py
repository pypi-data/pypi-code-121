#!/usr/bin/python3

import click
from feii.cli import PolicyCLI

@click.command(
  cls=PolicyCLI,
  short_help='Working with ilm policy.',
  epilog="Run 'feii policy COMMAND --help' for more information on a command."
)
def cli():
  """Working with ilm policy"""
