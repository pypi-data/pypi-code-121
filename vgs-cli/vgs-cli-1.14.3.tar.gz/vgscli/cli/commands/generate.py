import click
from click_plugins import with_plugins
from pkg_resources import iter_entry_points

from vgscli.errors import handle_errors
from vgscli.utils import read_file


@with_plugins(iter_entry_points('vgs.generate.plugins'))
@click.group('generate')
def generate() -> None:
    """
    Output a VGS resource template. Edited templates can be applied with a
    corresponding command.
    """
    pass


@generate.command('vault')
@handle_errors()
def generate_vault() -> None:
    """
    Output a vault template.
    """
    click.echo(read_file('resource-templates/vault-template.yaml'), nl=False)
