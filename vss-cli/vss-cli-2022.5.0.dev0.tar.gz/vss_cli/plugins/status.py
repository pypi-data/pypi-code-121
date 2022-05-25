"""Status plugin for VSS CLI (vss-cli)."""
import logging

import click

from vss_cli.cli import pass_context
from vss_cli.config import Configuration
from vss_cli.hcio import check_status as check_hcio
from vss_cli.helper import format_output
from vss_cli.sstatus import check_status as check_sstatus

_LOGGING = logging.getLogger(__name__)


@click.group(
    'status', invoke_without_command=True, short_help='Check API Status.'
)
@pass_context
def cli(ctx: Configuration):
    """Check API from https://healthchecks.io."""
    ctx.set_defaults()
    with ctx.spinner(disable=ctx.debug):
        objs = [check_hcio(), check_sstatus()]
    if click.get_current_context().invoked_subcommand is None:
        columns = [('NAME', 'name'), ('STATUS', 'status'), ('ICON', 'icon')]
        columns = ctx.columns or columns
        click.echo(format_output(ctx, objs, columns=columns))


@cli.command('vss', short_help='Check VSS Status.')
@click.option(
    '--maintenance',
    '-m',
    help='Show any scheduled maintenance',
    is_flag=True,
    default=False,
)
@pass_context
def get_vss_status_and_maint(ctx: Configuration, maintenance):
    """Check VSS Status from https://www.systemstatus.utoronto.ca/."""
    ctx.set_defaults()
    with ctx.spinner(disable=ctx.debug):
        system_status = check_sstatus()
    if maintenance:
        columns = [
            ('NAME', 'name'),
            ('IMPACT', 'impact'),
            ('STATUS', 'status'),
            ('DESCRIPTION', 'description[0:100]'),
            ('SCHEDULED', 'scheduled_for'),
        ]
        columns = ctx.columns or columns
        dat = system_status.get('upcoming_maintenances')
        click.echo(format_output(ctx, dat, columns=columns))
    else:
        columns = [
            ('NAME', 'name'),
            ('DESCRIPTION', 'description'),
            ('STATUS', 'status'),
            ('UPDATED', 'updated_at'),
            ('MAINTENANCE', 'upcoming_maintenances[*].name'),
        ]
        columns = ctx.columns or columns
        click.echo(
            format_output(ctx, [system_status], columns=columns, single=True)
        )
