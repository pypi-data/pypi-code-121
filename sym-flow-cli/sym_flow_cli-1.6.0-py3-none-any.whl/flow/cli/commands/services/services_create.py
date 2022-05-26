import click

from sym.flow.cli.commands.services.click.external_id_option import ExternalIdOption
from sym.flow.cli.commands.services.click.service_type_option import ServiceTypeOption
from sym.flow.cli.commands.services.hooks.slack_new import slack_new
from sym.flow.cli.errors import InvalidExternalIdError
from sym.flow.cli.helpers.api import SymAPI
from sym.flow.cli.helpers.global_options import GlobalOptions
from sym.flow.cli.models.service import Service
from sym.flow.cli.models.service_type import ServiceType


def post_service_create_hooks(options: GlobalOptions, service: Service) -> None:
    """Registered hooks to call after successful creation of services"""

    if service.service_type == ServiceType.SLACK.type_name:
        slack_new(options.sym_api, service.id)


@click.command(name="create", short_help="Set up a new service")
@click.make_pass_decorator(GlobalOptions, ensure=True)
@click.option(
    "--service-type",
    help="The service to set up",
    prompt=True,
    required=True,
    cls=ServiceTypeOption,
)
@click.option(
    "--external-id",
    help="The identifier for the service",
    prompt=True,
    required=True,
    cls=ExternalIdOption,
)
def services_create(
    options: GlobalOptions, service_type: ServiceType, external_id: str
) -> None:
    """Set up a new service for your organization."""

    # If a validator is defined, validate the external ID.
    if service_type.validator and not service_type.validator(external_id):
        raise InvalidExternalIdError(service_type, external_id)

    service = options.sym_api.create_service(service_type, external_id)

    click.secho(
        f"Successfully set up service type {service_type.type_name} with external ID {external_id}!",
        fg="green",
    )

    post_service_create_hooks(options, service)
