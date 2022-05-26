from typing import List

import click
from tabulate import tabulate

from sym.flow.cli.errors import InvalidChoiceError
from sym.flow.cli.helpers.api import SymAPI
from sym.flow.cli.helpers.global_options import GlobalOptions
from sym.flow.cli.models.resource import ResourceType


@click.command(name="list", short_help="List Sym resources")
@click.argument("resource_type", required=True, type=str)
@click.make_pass_decorator(GlobalOptions, ensure=True)
def resources_list(options: GlobalOptions, resource_type: str) -> None:
    """Prints a table view of Sym resources in your Organization to STDOUT.

    Resources should be created and managed through Terraform
    (https://docs.symops.com/docs/terraform-provider).
    """

    resource_options = ResourceType.options()
    if resource_type not in resource_options:
        raise InvalidChoiceError(value=resource_type, valid_choices=resource_options)

    # We need to use getattr to retrieve the correct Enum item because MyEnum(value) uses the
    # value of the Enum item, not the name. E.g. ResourceType("SYM_FLOW") will fail but
    # ResourceType("flows") will succeed.
    resource_type_enum = getattr(ResourceType, resource_type.upper())
    table_data = get_resource_data(options.sym_api, resource_type_enum)
    if not table_data:
        click.echo(f"No {resource_type} resources were found.")
        return

    click.echo(tabulate(table_data, headers="firstrow"))


def get_resource_data(api: SymAPI, resource_type: ResourceType) -> List[List[str]]:
    resources = api.get_resources(resource_type)
    if not resources:
        return []

    has_sub_type = bool(resources[0].sub_type)
    headers = ["SRN", "Slug"]
    if has_sub_type:
        headers.append("Type")

    table_data = [headers]
    for resource in resources:
        resource_data = [resource.srn, resource.slug]
        if has_sub_type:
            resource_data.append(resource.sub_type)

        table_data.append(resource_data)

    return table_data
