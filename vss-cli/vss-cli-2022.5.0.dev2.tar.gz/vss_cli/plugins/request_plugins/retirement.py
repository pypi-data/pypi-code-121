"""VM Retirement Request Management plugin for VSS CLI (vss-cli)."""
import logging

import click

from vss_cli import autocompletion, const, rel_opts as so
from vss_cli.cli import pass_context
from vss_cli.config import Configuration
from vss_cli.helper import format_output
from vss_cli.plugins.request import cli

_LOGGING = logging.getLogger(__name__)


@cli.group('retire', short_help='Manage virtual machine retirement requests')
@pass_context
def request_mgmt_retire(ctx: Configuration):
    """Manage virtual machine retirement requests."""
    pass


@request_mgmt_retire.command('ls', short_help='list vm retirement requests')
@so.filter_opt
@so.all_opt
@so.count_opt
@so.page_opt
@so.sort_opt
@pass_context
def request_mgmt_ret_ls(
    ctx: Configuration, filter_by, page, sort, show_all, count
):
    """List requests.

    Filter list in the following format <field_name> <operator>,<value>
    where operator is eq, ne, lt, le, gt, ge, like, in.
    For example: status=eq,PROCESSED

    vss-cli request retire ls -f status=eq,CONFIRMATION_REQUIRED

    Sort list in the following format <field_name>=<asc|desc>. For example:

    vss-cli request retire ls -s created_on=desc
    """
    columns = ctx.columns or const.COLUMNS_REQUEST_RETIRE
    _LOGGING.debug(f'Columns {columns}')
    params = dict(expand=1, sort='created_on,desc')
    if all(filter_by):
        params['filter'] = ';'.join(filter_by)
    if all(sort):
        params['sort'] = ';'.join(sort)
    # make request
    with ctx.spinner(disable=ctx.debug):
        _requests = ctx.get_retirement_requests(
            show_all=show_all, per_page=count, **params
        )

    output = format_output(ctx, _requests, columns=columns)
    # page results
    if page:
        click.echo_via_pager(output)
    else:
        ctx.echo(output)


@request_mgmt_retire.command('get', short_help='Retirement request info')
@click.argument(
    'rid',
    type=click.INT,
    required=True,
    shell_complete=autocompletion.retirement_requests,
)
@pass_context
def request_mgmt_ret_get(ctx: Configuration, rid):
    """Get Retirement Request info."""
    # make request
    with ctx.spinner(disable=ctx.debug):
        obj = ctx.get_retirement_request(rid)
    columns = ctx.columns or const.COLUMNS_REQUEST_RETIRE
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))


@request_mgmt_retire.command('cancel', short_help='Cancel retirement request.')
@click.argument('rid', type=click.INT, required=True)
@pass_context
def request_mgmt_ret_cancel(ctx: Configuration, rid):
    """Cancel Retirement Request."""
    # make request
    with ctx.spinner(disable=ctx.debug):
        obj = ctx.cancel_retirement_request(rid)
    columns = ctx.columns or const.COLUMNS_REQUEST_RETIRE_CANCEL
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))


@request_mgmt_retire.command('send', short_help='Cancel retirement request.')
@click.argument('rid', type=click.INT, required=True)
@pass_context
def request_mgmt_ret_retry(ctx: Configuration, rid):
    """Cancel Retirement Request."""
    # make request
    with ctx.spinner(disable=ctx.debug):
        obj = ctx.send_confirmation_retirement_request(rid)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_RETIRE_CANCEL
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))


@request_mgmt_retire.command(
    'confirm', short_help='Cancel retirement request.'
)
@click.argument('rid', type=click.INT, required=True)
@pass_context
def request_mgmt_ret_confirm(ctx: Configuration, rid):
    """Confirm retirement request."""
    with ctx.spinner(disable=ctx.debug):
        obj = ctx.confirm_retirement_request(rid)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_RETIRE_CONFIRM
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)
