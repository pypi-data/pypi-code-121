"""CLI Helpers"""

import sys

import click


def fail(
    message="Something went wrong",
    hint="Please check the Sym documentation at https://docs.symops.com/.",
):
    """Raise a usage error with a useful message"""
    click.secho(f"✖ {message}.", fg="red", bold=True)
    click.secho(f"{hint}.", fg="cyan")

    sys.exit(1)
