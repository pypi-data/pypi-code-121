from dataclasses import dataclass, field
from enum import Enum, auto
from functools import cached_property
from typing import Dict, List, Optional

import click

from sym.flow.cli.helpers.api import SymAPI
from sym.flow.cli.helpers.global_options import GlobalOptions
from sym.flow.cli.helpers.users import User
from sym.flow.cli.models.service import SYM_CLOUD_KEY


class OperationType(Enum):
    update_user = auto()
    delete_user = auto()
    delete_identity = auto()


@dataclass
class Operation:
    operation_type: OperationType
    original_value: Optional[User] = None
    new_value: Optional[User] = None


@dataclass
class OperationSets:
    update_user_ops: List[Operation] = field(default_factory=list)
    delete_identities_ops: List[Operation] = field(default_factory=list)
    delete_user_ops: List[Operation] = field(default_factory=list)


class OperationHelper:
    def __init__(self, options: GlobalOptions, operations: OperationSets):
        self.api = options.sym_api
        self.operations = operations

    @cached_property
    def update_users_payload(self) -> Dict:
        users = []
        for operation in self.operations.update_user_ops:
            patch_identities = []

            for identity in operation.new_value.identities:
                patch_identities.append(
                    {
                        "service_type": identity.service.service_type,
                        "external_id": identity.service.external_id,
                        "matcher": identity.matcher,
                    }
                )
            users.append(
                {
                    "id": operation.new_value.id,
                    "identities": patch_identities,
                    "type": operation.new_value.type,
                }
            )
        return {"users": users}

    @cached_property
    def delete_user_identity_payload(self) -> Dict:
        identities = []

        for operation in self.operations.delete_identities_ops:
            identities_to_delete = set(
                [
                    identity.service.service_key
                    for identity in operation.original_value.identities_without_sym_service
                ]
            ) - set(
                [
                    identity.service.service_key
                    for identity in operation.new_value.identities
                ]
            )

            for identity in operation.original_value.identities_without_sym_service:
                if identity.service.service_key in identities_to_delete:
                    identities.append(
                        {
                            "user_id": operation.new_value.id,
                            "service_type": identity.service.service_type,
                            "external_id": identity.service.external_id,
                            "matcher": identity.matcher,
                        }
                    )

        return {"identities": identities}

    @cached_property
    def delete_users_payload(self) -> Dict:
        users = []
        for operation in self.operations.delete_user_ops:
            if not (
                sym_service_identity := operation.original_value.get_identity_from_key(
                    SYM_CLOUD_KEY
                )
            ):
                continue
            users.append(
                {
                    "id": operation.original_value.id,
                    "identity": {
                        "service_type": sym_service_identity.service.service_type,
                        "matcher": sym_service_identity.matcher,
                    },
                }
            )
        return {"users": users}

    def handle_update_users(self) -> int:
        if not self.update_users_payload["users"]:
            return 0
        res = self.api.update_users(self.update_users_payload)
        update_count = res["succeeded"]
        click.secho(f"Successfully updated {update_count} users!")
        return update_count

    def handle_delete_identities(self) -> int:
        if not self.delete_user_identity_payload["identities"]:
            return 0
        res = self.api.delete_identities(self.delete_user_identity_payload)
        delete_count = res["succeeded"]
        click.secho(f"Successfully deleted {delete_count} identities!")
        return delete_count

    def handle_delete_users(self) -> int:
        if (deleted_dict := self.delete_users_payload["users"]) and click.confirm(
            f"About to delete {len(deleted_dict)} users. Do you want to continue?"
        ):
            res = self.api.delete_user(self.delete_users_payload)
            delete_count = res["succeeded"]
            click.secho(f"Successfully deleted {delete_count} users!")
            return delete_count

        return 0

    def apply_changes(self):
        total_updates = 0
        total_updates += self.handle_update_users()
        total_updates += self.handle_delete_identities()
        total_updates += self.handle_delete_users()

        if not total_updates:
            click.secho(f"No changes detected!")
