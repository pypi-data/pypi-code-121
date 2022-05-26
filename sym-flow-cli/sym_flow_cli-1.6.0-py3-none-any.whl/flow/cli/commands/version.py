import click

from ..version import __version__


@click.command(short_help="Print the version")
def version() -> None:
    click.echo(__version__)
