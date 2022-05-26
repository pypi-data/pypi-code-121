import click

from sym.flow.cli.helpers.api_operations import (
    Operation,
    OperationHelper,
    OperationSets,
    OperationType,
)
from sym.flow.cli.helpers.global_options import GlobalOptions
from sym.flow.cli.models import CSVMatcher, Identity, Service, User
from sym.flow.cli.models.service import SYM_CLOUD_KEY


def update_identity(
    options: GlobalOptions,
    user_to_update: User,
    new_identity_value: str,
    service: Service,
):
    """Given a user and a service, executes the operation helper for creating/updating the identity."""
    new_identity = Identity(
        service=service,
        matcher=CSVMatcher(service=service, value=new_identity_value).to_dict(),
    )
    sym_identity = user_to_update.get_identity_from_key(SYM_CLOUD_KEY)

    operations = OperationSets(
        # Don't need to send in all the existing identities,
        # just the identity to update and the Sym identity to identify the user
        update_user_ops=[
            Operation(
                operation_type=OperationType.update_user,
                original_value=None,
                new_value=User(
                    id=user_to_update.id, identities=[new_identity, sym_identity]
                ),
            )
        ],
        delete_identities_ops=[],
        delete_user_ops=[],
    )

    operation_helper = OperationHelper(options, operations)
    operation_helper.handle_update_users()


def delete_identity(options: GlobalOptions, original_user: User, service: Service):
    """Given a user and a service, executes the operation helper for deleting the identity."""
    identity_to_delete = original_user.get_identity_from_key(service.service_key)
    if not identity_to_delete:
        click.secho(
            f"{original_user.sym_identifier} has no identity for service {service.service_key}",
            fg="yellow",
        )

    new_identities = [i for i in original_user.identities if i != identity_to_delete]

    operations = OperationSets(
        update_user_ops=[],
        delete_identities_ops=[
            Operation(
                operation_type=OperationType.delete_identity,
                original_value=original_user,
                new_value=User(id=original_user.id, identities=new_identities),
            )
        ],
        delete_user_ops=[],
    )

    operation_helper = OperationHelper(options, operations)
    operation_helper.handle_delete_identities()
