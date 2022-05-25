"""Compute OS plugin for VSS CLI (vss-cli)."""
import logging

import click

from vss_cli import const, rel_opts as so
from vss_cli.cli import pass_context
from vss_cli.config import Configuration
from vss_cli.helper import format_output
from vss_cli.plugins.compute import cli

_LOGGING = logging.getLogger(__name__)


@cli.group('os', short_help='Supported OS.')
@pass_context
def compute_os(ctx):
    """Supported operating systems by our infrastructure.

    This resource is useful when deploying a new or
    reconfiguring an existing virtual machine.
    """


@compute_os.command('ls', short_help='list operating systems')
@so.filter_opt
@so.sort_opt
@so.all_opt
@so.count_opt
@so.page_opt
@pass_context
def compute_os_ls(ctx: Configuration, filter_by, page, sort, show_all, count):
    """List requests.

    Filter list in the following format <field_name>=<operator>,<value>
    where operator is eq, ne, lt, le, gt, ge, like, in.
    For example: status=eq,PROCESSED

    vss-cli compute os ls -f full_name=like,CentOS%

    Sort list in the following format <field_name>=<asc|desc>. For example:

    vss-cli compute os ls -s guest_id=asc
    """
    params = dict(expand=1, sort='guest_id,asc')
    if all(filter_by):
        params['filter'] = ';'.join(filter_by)
    if all(sort):
        params['sort'] = ';'.join(sort)
    with ctx.spinner(disable=ctx.debug):
        obj = ctx.get_os(show_all=show_all, per_page=count, **params)
    # format
    columns = ctx.columns or const.COLUMNS_OS
    output = format_output(ctx, obj, columns=columns)
    # page results
    if page:
        click.echo_via_pager(output)
    else:
        ctx.echo(output)
