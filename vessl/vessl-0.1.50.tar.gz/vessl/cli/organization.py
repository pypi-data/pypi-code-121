import sys

import click

import vessl
from vessl.cli._base import VesslGroup, vessl_argument
from vessl.cli._util import (
    Endpoint,
    generic_prompter,
    print_data,
    print_table,
    prompt_choices,
)
from vessl.organization import (
    create_organization,
    list_organizations,
    read_organization,
)
from vessl.util.exception import InvalidOrganizationError


def organization_name_prompter(
    ctx: click.Context, param: click.Parameter, value: str
) -> str:
    organizations = list_organizations()
    return prompt_choices("Organization", [x.name for x in organizations])


def region_prompter(ctx: click.Context, param: click.Parameter, value: str) -> str:
    regions = vessl.vessl_api.region_list_api().regions
    return prompt_choices("Region", [(x.name, x.value) for x in regions])


@click.command(name="organization", cls=VesslGroup)
def cli():
    pass


@cli.vessl_command()
@vessl_argument(
    "name",
    type=click.STRING,
    required=True,
    prompter=organization_name_prompter,
)
def read(name: str):
    organization = read_organization(organization_name=name)
    print_data(
        {
            "ID": organization.id,
            "Name": organization.name,
            "Region": organization.default_region,
            "Description": organization.description,
        }
    )


@cli.vessl_command()
def list():
    organizations = list_organizations()
    print_table(
        organizations,
        ["ID", "Name", "Region"],
        lambda x: [x.id, x.name, x.default_region],
    )


@cli.vessl_command()
@vessl_argument(
    "name",
    type=click.STRING,
    required=True,
    prompter=generic_prompter("Organization name"),
)
def create(name: str):
    organization = create_organization(organization_name=name)
    print(
        f"Created '{organization.name}'.\n"
        f"For more info: {Endpoint.organization.format(organization.name)}"
    )


def organization_name_callback(
    ctx: click.Context, param: click.Parameter, value: str
) -> str:
    try:
        organization_name = vessl.vessl_api.set_organization(value)
        print(f"Organization: {organization_name}")
    except InvalidOrganizationError:
        print(
            "Invalid organization. Please choose an organization using `vessl configure`."
        )
        sys.exit(1)


# Ensure this is called before other options with `is_eager=True` for
# other callbacks that need organization to be preconfigured.
organization_name_option = click.option(
    "--organization",
    "organization_name",
    type=click.STRING,
    hidden=True,
    is_eager=True,
    expose_value=False,
    callback=organization_name_callback,
    help="Override default organization.",
)
