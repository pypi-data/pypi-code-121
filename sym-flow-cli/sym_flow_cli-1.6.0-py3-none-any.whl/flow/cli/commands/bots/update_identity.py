from typing import Optional

import click
import inquirer

from sym.flow.cli.commands.users.utils import get_or_prompt_service
from sym.flow.cli.errors import MissingIdentityValueError
from sym.flow.cli.helpers.global_options import GlobalOptions
from sym.flow.cli.helpers.identity_operations import update_identity


@click.command(
    name="update-identity", short_help="Update a Bot's identity for a specific service"
)
@click.argument("username", required=True, type=str)
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
def update_bot_identity(
    options: GlobalOptions,
    username: str,
    _new_value: Optional[str],
    _service_type: Optional[str],
    _external_id: Optional[str],
) -> None:
    """For an existing Sym Bot, update a single Identity such as an AWS SSO Principal UUID or a Slack User ID.

    \b
    Example:
        `symflow bots update-identity hal`
    """

    api = options.sym_api

    user_to_update = api.get_bot(username)
    service = get_or_prompt_service(api, _service_type, _external_id)

    new_identity_value = _new_value or inquirer.text(message="New value?")

    if not new_identity_value:
        raise MissingIdentityValueError(username, command="bots")

    update_identity(options, user_to_update, new_identity_value, service)
