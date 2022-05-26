from typing import List

import click
from tabulate import tabulate

from sym.flow.cli.helpers.api import SymAPI
from sym.flow.cli.helpers.global_options import GlobalOptions
from sym.flow.cli.models.service import Service


@click.command(name="list", short_help="View all services")
@click.make_pass_decorator(GlobalOptions, ensure=True)
def services_list(options: GlobalOptions) -> None:
    """View all Services currently set up for your organization."""
    click.echo(get_services_data(options.sym_api))


def get_services_data(api: SymAPI) -> str:
    services: List[Service] = api.get_services()

    table_data = [["Service Type", "External ID", "Label"]]
    for s in services:
        table_data.append([s.service_type, s.external_id, s.label])

    return tabulate(table_data, headers="firstrow")
