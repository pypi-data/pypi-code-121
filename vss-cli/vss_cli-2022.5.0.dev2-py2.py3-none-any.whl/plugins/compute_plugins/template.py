"""Compute Template plugin for VSS CLI (vss-cli)."""
import logging
from typing import List

import click

from vss_cli import autocompletion, const, rel_opts as so
from vss_cli.cli import pass_context
from vss_cli.config import Configuration
from vss_cli.helper import format_output
from vss_cli.plugins.compute import cli

_LOGGING = logging.getLogger(__name__)


@cli.group('template', short_help='List virtual machine templates')
@pass_context
def compute_template(ctx):
    """List virtual machine templates."""
    pass


@compute_template.group(
    'rm', help='Delete virtual machine templates', invoke_without_command=True
)
@click.option(
    '-s',
    '--show-info',
    is_flag=True,
    default=False,
    show_default=True,
    help='Show guest info and confirmation.',
)
@click.argument(
    'vm_id',
    type=click.STRING,
    required=True,
    nargs=-1,
    shell_complete=autocompletion.virtual_machines,
)
@so.max_del_opt
@pass_context
def compute_template_rm(
    ctx: Configuration, vm_id: List[str], max_del: int, show_info: bool,
):
    """Delete a list of virtual machine template ids.

    vss-cli compute template rm <name-or-vm-id> <name-or-vm-id> --show-info
    """
    _LOGGING.debug(f'Attempting to remove {vm_id}')
    if len(vm_id) > max_del:
        raise click.BadArgumentUsage(
            'Increase max instance removal with --max-del/-m option'
        )
    # result
    objs = list()
    with ctx.spinner(disable=ctx.debug or show_info):
        for vm in vm_id:
            skip = False
            _vm = ctx.get_vm_by_id_or_name(vm)
            if not _vm:
                _LOGGING.warning(
                    f'Virtual machine {vm} could not be found. Skipping.'
                )
                skip = True
            _LOGGING.debug(f'Found {_vm}')
            moref = _vm[0]['moref']
            if _vm and show_info:
                c_str = const.DEFAULT_VM_DEL_MSG.format(vm=_vm[0])
                confirmation = click.confirm(c_str)
                if not confirmation:
                    _LOGGING.warning(f'Skipping {moref}...')
                    skip = True
            if not skip:
                # request
                objs.append(ctx.delete_template(vm_id=moref))
    # print
    if objs:
        columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
        ctx.echo(
            format_output(ctx, objs, columns=columns, single=len(objs) == 1)
        )
        if ctx.wait_for_requests:
            if len(objs) > 1:
                ctx.wait_for_requests_to(objs, in_multiple=True)
            else:
                ctx.wait_for_request_to(objs[0])
    else:
        _LOGGING.warning('No requests have been submitted.')


@compute_template.command('ls', short_help='List virtual machine templates')
@so.filter_opt
@so.all_opt
@so.page_opt
@so.sort_opt
@so.count_opt
@pass_context
def compute_template_ls(
    ctx: Configuration, filter_by, show_all, sort, page, count
):
    """List virtual machine templates.

    Filter and sort list by any attribute. For example:

    vss-cli compute template ls -f name=like,%vm-name% -f version=like,%13

    Simple name filtering:

    vss-cli compute template ls -f name=%vm-name% -s name=desc

    """
    params = dict(expand=1, sort='name,asc')
    if all(filter_by):
        params['filter'] = ';'.join(filter_by)
    if all(sort):
        params['sort'] = ';'.join(sort)
    # get templates
    with ctx.spinner(disable=ctx.debug):
        obj = ctx.get_templates(show_all=show_all, per_page=count, **params)
    # including additional attributes?
    columns = ctx.columns or const.COLUMNS_VM_TEMPLATE
    # format output
    output = format_output(ctx, obj, columns=columns)
    # page
    if page:
        click.echo_via_pager(output)
    else:
        ctx.echo(output)
