import uuid

import click

from sym.flow.cli.errors import BotAlreadyExists
from sym.flow.cli.helpers.api import SymAPI
from sym.flow.cli.helpers.api_operations import (
    Operation,
    OperationHelper,
    OperationSets,
    OperationType,
)
from sym.flow.cli.helpers.global_options import GlobalOptions
from sym.flow.cli.models import BaseService, Identity, ServiceType, User
from sym.flow.cli.models.user_type import UserType


@click.command(name="create", short_help="Create a new Sym Bot User")
@click.make_pass_decorator(GlobalOptions, ensure=True)
@click.argument("username")
def bots_create(options: GlobalOptions, username: str) -> None:
    """
    Creates a new bot-user with the given username
    """
    bot_users = options.sym_api.get_users({"type": UserType.BOT})
    if username in [u.sym_identifier for u in bot_users]:
        raise BotAlreadyExists(username)

    identities = [
        Identity(
            service=BaseService(slug=ServiceType.SYM.type_name, external_id="cloud"),
            matcher={"username": username},
        )
    ]

    operations = OperationSets(
        # update_user also handles create user
        update_user_ops=[
            Operation(
                operation_type=OperationType.update_user,
                original_value=None,
                new_value=User(
                    id=str(uuid.uuid4()), identities=identities, type=UserType.BOT
                ),
            )
        ],
        delete_identities_ops=[],
        delete_user_ops=[],
    )

    operation_helper = OperationHelper(options, operations)
    options.sym_api.update_users(operation_helper.update_users_payload)
    click.secho(f"Successfully created {username}!", fg="green")
