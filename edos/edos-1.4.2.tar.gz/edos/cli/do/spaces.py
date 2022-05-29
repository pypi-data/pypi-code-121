import logging

import click

from edos.services.spaces_service import SpacesService

LOG = logging.getLogger(__name__)


@click.group()
def spaces():
    """Digital Ocean Spaces (object storage) management"""


@spaces.command()
def ls():
    """List all spaces"""
    for space in SpacesService().get_spaces():
        click.echo(space)


@spaces.command()
@click.argument("name")
def create(name):
    """Create a space"""
    if not click.confirm(f'Creating space "{name}", proceed?'):
        click.echo("creation cancelled")
        return
    SpacesService().create_space(name)
    click.echo(click.style("Created space with name: ", fg="green") + name)
