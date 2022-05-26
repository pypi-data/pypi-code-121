import csv
import uuid
from copy import copy
from functools import cached_property
from typing import TYPE_CHECKING, Dict, List, Optional

from sym.flow.cli.models.service import Service
from sym.flow.cli.models.service_type import MANAGED_SERVICES, ServiceType
from sym.flow.cli.models.user import Identity, User

if TYPE_CHECKING:
    from sym.flow.cli.helpers.api_operations import OperationSets


class UserUpdateSet:
    def __init__(
        self, service_data: List[Service] = None, user_data: List[User] = None
    ) -> None:
        self.users: List[User] = user_data or []
        self.services: List[Service] = service_data or []

    @property
    def uneditable_service_types(self) -> List[str]:
        """The list of service types which may at any point be set or edited
        by users.
        """
        service_types = copy(MANAGED_SERVICES)

        # Note: ServiceType.SYM is not technically allowed to be updated, but
        # must be included in the editable list so that new users may be created.
        service_types.remove(ServiceType.SYM.type_name)
        return service_types

    def tabulate(self, include_user_id: bool = False) -> List[List[str]]:
        """Returns contained User data formatted as a list of lists
        where the inner lists contain an item for each of the User's
        Identities.

        include_user_id: Boolean indicating whether or not to include the User ID in the returned row data.
        The User ID is required when writing `symflow users list` to CSV, but hidden when printed
        to the terminal

        e.g. if the Identities are Sym, Slack, Pagerduty:
            [["user@symops.io", "U12345", "P12345"]]
        """
        result = []
        for user in self.users:
            user_data = []
            for service in self.services:
                if service.service_type not in self.uneditable_service_types:
                    identity_repr = user.identity_repr_for_service(service)
                    user_data.append(identity_repr)
            if include_user_id:
                user_data.append(user.id)
            result.append(user_data)
        return result

    def write_to_csv(self, file_path: str) -> None:
        """Writes User data to a CSV file at the path provided."""
        with open(file_path, "w") as f:
            writer = csv.writer(f)
            writer.writerow(self.headers)
            for user_data in self.tabulate(include_user_id=True):
                writer.writerow(user_data)

    def add_csv_row(self, row: Dict) -> None:
        user_id = row.pop("User ID", "")
        # If no user id is empty, assume a temporary uuid for user creation
        if user_id == "":
            user_id = str(uuid.uuid4())
        user = User(id=user_id, identities=[])

        for service_key, matcher_value in row.items():
            if service_key and matcher_value:
                user.identities.append(
                    Identity.from_csv(
                        matcher_value=matcher_value, service_key=service_key
                    )
                )

        self.users.append(user)

    @classmethod
    def compare_user_sets(
        cls, original: "UserUpdateSet", edited: "UserUpdateSet"
    ) -> "OperationSets":
        from sym.flow.cli.helpers.api_operations import (
            Operation,
            OperationSets,
            OperationType,
        )

        old_users = {user.id for user in original.users}
        new_users = {user.id for user in edited.users}

        update_user_ops = []
        delete_user_identity_operations = []
        delete_user_ops = []

        created_users = new_users - old_users
        updated_users = new_users.intersection(old_users)
        deleted_users = old_users - new_users

        for user_id in created_users:
            new_user = edited.get_user_by_id(user_id)
            operation = Operation(
                operation_type=OperationType.update_user,
                original_value=new_user,
                new_value=new_user,
            )
            update_user_ops.append(operation)

        for user_id in updated_users:
            old_user = original.get_user_by_id(user_id)
            new_user = edited.get_user_by_id(user_id)

            old_idents = {
                i.service.service_key
                for i in old_user.filtered_identities(MANAGED_SERVICES)
            }
            new_idents = {
                i.service.service_key
                for i in new_user.filtered_identities(MANAGED_SERVICES)
            }

            created_or_updated_idents = new_idents.intersection(old_idents) | (
                new_idents - old_idents
            )
            deleted_idents = old_idents - new_idents

            for service_key in created_or_updated_idents:
                old_identity = old_user.get_identity_from_key(service_key)
                new_identity = new_user.get_identity_from_key(service_key)

                if old_identity == new_identity:
                    continue

                # Either User doesn't have this identity yet or has this identity but the value is different, update the user
                operation = Operation(
                    operation_type=OperationType.update_user,
                    original_value=old_user,
                    new_value=new_user,
                )

                # operation includes all identities for a user, only append it once
                update_user_ops.append(operation)
                break

            if deleted_idents:
                # At least one identity has been deleted from the set, update the user
                operation = Operation(
                    operation_type=OperationType.delete_identity,
                    original_value=old_user,
                    new_value=new_user,
                )

                # operation includes all identities for a user, only append it once
                delete_user_identity_operations.append(operation)

        for user_id in deleted_users:
            user_to_delete = original.get_user_by_id(user_id)

            # User doesn't exist anymore, delete it
            operation = Operation(
                operation_type=OperationType.delete_user, original_value=user_to_delete
            )
            delete_user_ops.append(operation)

        return OperationSets(
            update_user_ops=update_user_ops,
            delete_identities_ops=delete_user_identity_operations,
            delete_user_ops=delete_user_ops,
        )

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        return next((u for u in self.users if u.id == user_id), None)

    @cached_property
    def headers(self) -> List[str]:
        """The list of headers from the CSV file."""
        return [
            s.service_key
            for s in self.services
            if s.service_type not in self.uneditable_service_types
        ] + ["User ID"]
