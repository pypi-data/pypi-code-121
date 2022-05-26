from typing import Optional

import click
import inquirer

from sym.flow.cli.commands.users.utils import get_or_prompt_service
from sym.flow.cli.errors import MissingIdentityValueError
from sym.flow.cli.helpers.api_operations import (
    Operation,
    OperationHelper,
    OperationSets,
    OperationType,
)
from sym.flow.cli.helpers.global_options import GlobalOptions
from sym.flow.cli.helpers.identity_operations import update_identity
from sym.flow.cli.models.service import SYM_CLOUD_KEY, Service
from sym.flow.cli.models.user import CSVMatcher, Identity, User


@click.command(
    name="update-identity", short_help="Update a User's identity for a specific service"
)
@click.argument("email", required=True, type=str)
@click.option("--new-value", "_new_value", help="The new identity value", type=str)
@click.option(
    "--service-type",
    "_service_type",
    help="The type of service the identity is tied to",
)
@click.option(
    "--external-id",
    "_external_id",
    help="The identifier for the service",
)
@click.make_pass_decorator(GlobalOptions, ensure=True)
def update_user_identity(
    options: GlobalOptions,
    email: str,
    _new_value: Optional[str],
    _service_type: Optional[str],
    _external_id: Optional[str],
) -> None:
    """For an existing Sym User, update a single Identity such as an AWS SSO Principal UUID or a Slack User ID.

    \b
    Example:
        `symflow users update-identity user@symops.io`
    """

    api = options.sym_api
    user_to_update = api.get_user(email)
    service = get_or_prompt_service(api, _service_type, _external_id)

    new_identity_value = _new_value or inquirer.text(message="New value?")

    if not new_identity_value:
        raise MissingIdentityValueError(email)

    update_identity(options, user_to_update, new_identity_value, service)
