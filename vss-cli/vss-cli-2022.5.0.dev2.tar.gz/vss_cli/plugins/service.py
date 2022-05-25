"""VSS Service Management plugin for VSS CLI (vss-cli)."""
import click

from vss_cli import const, rel_opts as so
from vss_cli.cli import pass_context
from vss_cli.config import Configuration
from vss_cli.helper import format_output


@click.group('service', short_help='ITS Service catalog.')
@pass_context
def cli(ctx: Configuration):
    """Browse ITS Service catalog."""
    with ctx.spinner(disable=ctx.debug):
        ctx.load_config()


@cli.command('ls', short_help='list available ITS Service catalog.')
@so.filter_opt
@so.sort_opt
@so.all_opt
@so.count_opt
@so.page_opt
@pass_context
def service_ls(ctx: Configuration, filter_by, page, sort, show_all, count):
    """List services.

    Filter list in the following format <field_name> <operator>,<value>
    where operator is eq, ne, lt, le, gt, ge, like, in.
    For example: name=like,%VPN%

    vss-cli service ls -f name=like,%VPN%

    Sort list in the following format <field_name>=<asc|desc>. For example:

    vss-cli service ls -s label=desc
    """
    columns = ctx.columns or const.COLUMNS_VSS_SERVICE
    params = dict()
    if all(filter_by):
        params['filter'] = ';'.join(filter_by)
    if all(sort):
        params['sort'] = ';'.join(sort)
    # make request
    with ctx.spinner(disable=ctx.debug):
        _requests = ctx.get_vss_services(
            show_all=show_all, per_page=count, **params
        )
    # format output
    output = format_output(ctx, _requests, columns=columns)
    # page results
    if page:
        click.echo_via_pager(output)
    else:
        ctx.echo(output)
