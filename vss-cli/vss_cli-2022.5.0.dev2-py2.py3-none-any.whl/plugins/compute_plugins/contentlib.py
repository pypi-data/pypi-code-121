"""Compute Content Library plugin for VSS CLI (vss-cli)."""
import logging

import click

from vss_cli import const, rel_opts as so
from vss_cli.cli import pass_context
from vss_cli.config import Configuration
from vss_cli.helper import format_output
from vss_cli.plugins.compute import cli

_LOGGING = logging.getLogger(__name__)


@cli.group('contentlib', short_help='Manage Content Library Items.')
@pass_context
def compute_contentlib(ctx: Configuration):
    """Manage Manage Content Library Items.

    Virtual Machine templates, OVF, ISO and other items.
    """


@compute_contentlib.group('vm', short_help='Browse Virtual Machine Templates')
@pass_context
def compute_contentlib_vm_tmpl(ctx: Configuration):
    """Available ISO images in the VSS central store."""


@compute_contentlib_vm_tmpl.command(
    'ls', short_help='list public VM Templates'
)
@so.filter_opt
@so.sort_opt
@so.all_opt
@so.page_opt
@pass_context
def compute_contentlib_vm_tmpl_ls(
    ctx: Configuration, filter_by, show_all, sort, page
):
    """List available VM templates available in the Content Library.

    Filter by name and sort desc. For example:

    vss-cli compute contentlib vm ls -f name=like,Cent% -s path=asc
    """
    params = dict(sort='name,asc')
    if all(filter_by):
        params['filter'] = ';'.join(filter_by)
    if all(sort):
        params['sort'] = ';'.join(sort)
    # get objects
    with ctx.spinner(disable=ctx.debug):
        obj = ctx.get_content_library_vm_items(show_all=show_all, **params)
    # format
    columns = ctx.columns or const.COLUMNS_CLIB_ITEMS
    output = format_output(ctx, obj, columns=columns)
    # page results
    if page:
        click.echo_via_pager(output)
    else:
        ctx.echo(output)


@compute_contentlib.group('ovf', short_help='Browse current OVF images')
@pass_context
def compute_contentlib_ovf(ctx: Configuration):
    """Available OVF images available in Content Library."""
    pass


@compute_contentlib_ovf.command('ls', short_help='list public OVF images')
@so.filter_opt
@so.sort_opt
@so.all_opt
@so.page_opt
@pass_context
def compute_contentlib_ovf_ls(
    ctx: Configuration, filter_by, show_all, sort, page
):
    """List available OVF templates available in the Content Library.

    Filter by name and sort desc. For example:

    vss-cli compute contentlib ovf ls -f name=photon -s path=asc
    """
    params = dict(sort='name,asc')
    if all(filter_by):
        params['filter'] = ';'.join(filter_by)
    if all(sort):
        params['sort'] = ';'.join(sort)
    with ctx.spinner(disable=ctx.debug):
        obj = ctx.get_content_library_ovf_items(show_all=show_all, **params)
    # format
    columns = ctx.columns or const.COLUMNS_CLIB_ITEMS
    output = format_output(ctx, obj, columns=columns)
    # page results
    if page:
        click.echo_via_pager(output)
    else:
        ctx.echo(output)


@compute_contentlib.group('iso', short_help='Browse current ISO images')
@pass_context
def compute_contentlib_iso(ctx: Configuration):
    """Available ISO images available in Content Library."""
    pass


@compute_contentlib_iso.command('ls', short_help='list public ISO images')
@so.filter_opt
@so.sort_opt
@so.all_opt
@so.page_opt
@pass_context
def compute_contentlib_iso_ls(
    ctx: Configuration, filter_by, show_all, sort, page
):
    """List available ISO files available in the Content Library.

    Filter by name and sort desc. For example:

    vss-cli compute contentlib iso ls -f name=ubuntu -s path=asc
    """
    params = dict(sort='name,asc')
    if all(filter_by):
        params['filter'] = ';'.join(filter_by)
    if all(sort):
        params['sort'] = ';'.join(sort)
    with ctx.spinner(disable=ctx.debug):
        obj = ctx.get_content_library_iso_items(show_all=show_all, **params)
    # format
    columns = ctx.columns or const.COLUMNS_CLIB_ITEMS
    output = format_output(ctx, obj, columns=columns)
    # page results
    if page:
        click.echo_via_pager(output)
    else:
        ctx.echo(output)
