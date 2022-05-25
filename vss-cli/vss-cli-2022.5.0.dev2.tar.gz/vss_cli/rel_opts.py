"""Shared click options for VSS CLI (vss-cli)."""

import click

from vss_cli.helper import process_filters, process_sort

filter_opt = click.option(
    '-f',
    '--filter-by',
    multiple=True,
    type=click.STRING,
    callback=process_filters,
    default=[],
    help='filter list by <field_name>=<operator>,<value>',
)
sort_opt = click.option(
    '-s',
    '--sort',
    multiple=True,
    type=click.STRING,
    callback=process_sort,
    default=None,
    help='sort by <field_name>=<asc|desc>',
)

all_opt = click.option(
    '-a',
    '--show-all',
    is_flag=True,
    help='show all results',
    show_default=True,
)
count_opt = click.option(
    '-c', '--count', type=click.INT, help='size of results', default=50
)
page_opt = click.option(
    '-p',
    '--page',
    is_flag=True,
    help='page results in a less-like format',
    show_default=True,
)
dry_run_opt = click.option('--dry-run', is_flag=True, help='no changes')
max_del_opt = click.option(
    '-m',
    '--max-del',
    type=click.IntRange(1, 10),
    required=False,
    default=3,
    help='Maximum items to delete',
    show_default=True,
)
