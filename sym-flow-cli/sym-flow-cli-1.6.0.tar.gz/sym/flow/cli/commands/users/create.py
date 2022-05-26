import uuid
from typing import Dict, List, Optional

import click
import inflection
import inquirer

from sym.flow.cli.errors import InvalidChoiceError, MissingServiceError, UserAlreadyExists
from sym.flow.cli.helpers.api import SymAPI
from sym.flow.cli.helpers.api_operations import (
    Operation,
    OperationHelper,
    OperationSets,
    OperationType,
)
from sym.flow.cli.helpers.global_options import GlobalOptions
from sym.flow.cli.models.service import Service
from sym.flow.cli.models.service_type import ServiceType
from sym.flow.cli.models.user import CSVMatcher, Identity, User


def to_service_list(ctx: click.Context, param, value) -> Dict[ServiceType, List[Service]]:
    """Parses the space separated --identities list into services to set up identities for
    e.g. "--identities slack aws_sso"

    Validates that the requested services exist in the organization
    Returns a list of services to prompt for identities
    """
    options: GlobalOptions = ctx.find_object(GlobalOptions)
    registered_services = options.sym_api.get_services()

    # always set up a sym identity
    sym_service = next(
        (s for s in registered_services if s.service_type == ServiceType.SYM.type_name)
    )
    requested_services = {ServiceType.SYM: [sym_service]}

    for service_type_str in value:
        service_type = ServiceType.get(service_type_str)
        # Requested service is not recognized
        if not service_type:
            existing_types = {s.service_type for s in registered_services}
            raise InvalidChoiceError(service_type_str, sorted(list(existing_types)))

        if services := [
            s for s in registered_services if s.service_type == str(service_type)
        ]:
            requested_services[service_type] = services
        else:
            # A valid service type, but not one registered with the organization
            raise MissingServiceError(service_type_str)

    return requested_services


def prompt_for_identity(
    service_type: ServiceType, service: Service
) -> Optional[Identity]:
    prompt = f"{inflection.titleize(service_type.type_name)} ({service.external_id}) {service_type.matcher}"

    if identity_value := inquirer.text(prompt).strip():
        return Identity(
            service=service,
            matcher=CSVMatcher(service=service, value=identity_value).to_dict(),
        )

    return None


@click.command(
    name="create",
    short_help="Create a new User",
)
@click.argument("email", required=True, type=str)
@click.option(
    "-s",
    "--service-type",
    "prompt_identities",
    multiple=True,
    callback=to_service_list,
    help="Service type to set up an Identity for",
)
@click.make_pass_decorator(GlobalOptions, ensure=True)
def users_create(
    options: GlobalOptions,
    email: str,
    prompt_identities: Dict[ServiceType, List[Service]],
) -> None:
    """Creates a single user with the given email and starts a wizard to set up identities for the service types specified

    \b
    Example:
        `symflow users create user@symops.io -s aws_sso -s slack`
    """
    users = options.sym_api.get_users()

    if email in [u.sym_email for u in users]:
        raise UserAlreadyExists(email)

    # Sym Service should always exist, set by `to_service_list`
    sym_service = prompt_identities.pop(ServiceType.SYM)[0]
    identities = [
        Identity(
            service=sym_service,
            matcher=CSVMatcher(service=sym_service, value=email).to_dict(),
        )
    ]

    if prompt_identities:
        click.echo("Leave blank to skip identity")
        # Prompt for identity values for any remaining services
        for (service_type, services) in prompt_identities.items():
            for service in services:
                if identity := prompt_for_identity(service_type, service):
                    identities.append(identity)

    operations = OperationSets(
        # update_user also handles create user
        update_user_ops=[
            Operation(
                operation_type=OperationType.update_user,
                original_value=None,
                new_value=User(id=str(uuid.uuid4()), identities=identities),
            )
        ],
        delete_identities_ops=[],
        delete_user_ops=[],
    )

    operation_helper = OperationHelper(options, operations)
    operation_helper.handle_update_users()
