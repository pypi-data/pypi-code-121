"""Compute Inventory plugin for VSS CLI (vss-cli)."""
import logging
from typing import List

import click

from vss_cli import const, rel_opts as so
import vss_cli.autocompletion as autocompletion
from vss_cli.cli import pass_context
from vss_cli.config import Configuration
from vss_cli.helper import format_output
from vss_cli.plugins.compute import cli

_LOGGING = logging.getLogger(__name__)


@cli.group('inventory', short_help='Manage inventory reports')
@pass_context
def cli(ctx: Configuration):
    """Create or download an inventory file of your virtual machines.

    Inventory files are created and transferred to your VSKEY-STOR
    space and are also available through the API.
    """


@cli.command('dl', short_help='download inventory report')
@click.argument(
    'request_id',
    type=click.INT,
    required=True,
    shell_complete=autocompletion.inventory_requests,
)
@click.option(
    '-d',
    '--directory',
    type=click.STRING,
    help='report destination',
    required=False,
    default=None,
)
@click.option(
    '-l', '--launch', is_flag=True, help='Launch link in default application'
)
@pass_context
def compute_inventory_dl(ctx: Configuration, request_id, directory, launch):
    """Download inventory request report.

    Also, it's possible to open downloaded file in default editor.
    """
    file_path = ctx.download_inventory_file(request_id, directory)
    # to launch or not
    if launch and file_path:
        click.launch(file_path.get('file'))


@cli.command('mk', short_help='create inventory report')
@click.argument(
    'attribute',
    nargs=-1,
    default=None,
    shell_complete=autocompletion.inventory_properties,
)
@click.option(
    '-f',
    '--fmt',
    type=click.Choice(['json', 'csv']),
    default='csv',
    help='report format',
    show_default=True,
)
@click.option(
    '--transfer/--no-transfer',
    default=False,
    help='Transfer report to personal store',
    show_default=True,
)
@click.option('-a', '--all', is_flag=True, help='include all attributes')
@pass_context
def compute_inventory_mk(
    ctx: Configuration,
    fmt: str,
    all: bool,
    attribute: List[str],
    transfer: bool,
):
    """Submit an inventory report request.

    Generate report file in JSON or CSV format of your virtual machines.
    """
    attributes = ctx.get_inventory_properties() if all else list(attribute)
    obj = ctx.create_inventory_file(
        fmt=fmt, props=attributes, transfer=transfer
    )
    # format output
    ctx.echo(
        format_output(
            ctx, [obj], columns=const.COLUMNS_REQUEST_SUBMITTED, single=True
        )
    )
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)
        if click.confirm('Would you like to download?'):
            ctx.download_inventory_file(obj['request']['id'], '')
