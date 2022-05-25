"""Compute Domain plugin for VSS CLI (vss-cli)."""
import logging

import click

from vss_cli import const, rel_opts as so
import vss_cli.autocompletion as autocompletion
from vss_cli.cli import pass_context
from vss_cli.config import Configuration
from vss_cli.exceptions import VssCliError
from vss_cli.helper import format_output
from vss_cli.plugins.compute import cli

_LOGGING = logging.getLogger(__name__)


@cli.group('domain', short_help='List compute domains.')
@pass_context
def cli(ctx: Configuration):
    """Domain command.

    A fault domain consists of one or more ESXI hosts and
    Datastore Clusters grouped together according to their
    physical location in the datacenter.
    """


@cli.command('ls', short_help='list fault domains')
@so.filter_opt
@so.all_opt
@so.page_opt
@so.sort_opt
@so.count_opt
@pass_context
def domain_ls(ctx: Configuration, filter_by, show_all, sort, page, count):
    """List available fault domains."""
    columns = ctx.columns or const.COLUMNS_MOREF
    params = dict(expand=1, sort='name,asc')
    if all(filter_by):
        params['filter'] = ';'.join(filter_by)
    if all(sort):
        params['sort'] = ';'.join(sort)
    # query
    with ctx.spinner(disable=ctx.debug):
        objs = ctx.get_domains(show_all=show_all, per_page=count, **params)
    # format output
    output = format_output(ctx, objs, columns=columns)
    # page results
    if page:
        click.echo_via_pager(output)
    else:
        ctx.echo(output)


@cli.group('get', help='Given domain info.', invoke_without_command=True)
@click.argument(
    'name_or_moref',
    type=click.STRING,
    required=True,
    shell_complete=autocompletion.domains,
)
@pass_context
def domain_get(ctx: Configuration, name_or_moref):
    """Get fault domain information."""
    _domain = ctx.get_domain_by_name_or_moref(name_or_moref)
    ctx.moref = _domain[0]['moref']
    if click.get_current_context().invoked_subcommand is None:
        columns = ctx.columns or const.COLUMNS_MOREF
        with ctx.spinner(disable=ctx.debug):
            obj = ctx.get_domain(ctx.moref)
        ctx.echo(format_output(ctx, [obj], columns=columns, single=True))


@domain_get.command('vms', help='Given domain vms.')
@click.option(
    '-p', '--page', is_flag=True, help='page results in a less-like format'
)
@pass_context
def domain_get_vms(ctx: Configuration, page):
    """Get VMs in given fault domain."""
    with ctx.spinner(disable=ctx.debug):
        obj = ctx.get_vms_by_domain(ctx.moref)
    if not obj:
        raise VssCliError(
            f'Either domain {ctx.moref} does not exist, '
            f'or you do not have permission to access.'
        )
    output = format_output(ctx, obj, columns=const.COLUMNS_VM)
    # page results
    if page:
        click.echo_via_pager(output)
    else:
        ctx.echo(output)
