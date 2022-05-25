"""Compute Files plugin for VSS CLI (vss-cli)."""
import logging

import click

from vss_cli import const, rel_opts as so
from vss_cli.cli import pass_context
from vss_cli.config import Configuration
from vss_cli.helper import format_output
from vss_cli.plugins.compute import cli

_LOGGING = logging.getLogger(__name__)


@cli.group('vmdk', short_help='Manage personal VMDK files.')
@pass_context
def compute_vmdk(ctx):
    """Manage VM images.

    Available files in your personal space.
    """


@compute_vmdk.group('personal', short_help='Browse current vmdks.')
@pass_context
def compute_vmdk_personal(ctx):
    """Available VMDK in your personal VSKEY-STOR space."""
    pass


@compute_vmdk_personal.command('ls', short_help='List personal VMDK Files.')
@click.option(
    '-p', '--page', is_flag=True, help='page results in a less-like format'
)
@pass_context
def compute_vmdk_personal_ls(ctx: Configuration, page):
    """List VMDK files stored in your personal VSKEY-STOR space.

    If the VMDK you uploaded is not listed, use the sync command
    and try again.

    vss-cli compute vmdk personal sync
    vss-cli compute vmdk personal ls
    """
    with ctx.spinner(disable=ctx.debug):
        obj = ctx.get_user_vmdks()
    # format
    columns = ctx.columns or const.COLUMNS_IMAGE
    output = format_output(ctx, obj, columns=columns)
    # page results
    if page:
        click.echo_via_pager(output)
    else:
        ctx.echo(output)


@compute_vmdk_personal.command('sync', short_help='Sync personal VMDK files')
@pass_context
def compute_vmdk_personal_sync(ctx: Configuration):
    """Synchronize VMDK files stored in your personal VSKEY-STOR space.

    Once processed it should be listed with the ls command.
    """
    obj = ctx.sync_user_vmdks()
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
