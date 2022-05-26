import copy
from typing import List

import pytest

from sym.flow.cli.helpers.api_operations import OperationType
from sym.flow.cli.helpers.users import UserUpdateSet
from sym.flow.cli.models.user import User
from sym.flow.cli.tests.factories.users import UserFactory
from sym.flow.cli.tests.helpers.sandbox import Sandbox


class TestUserUpdateSet:
    @pytest.fixture
    def user_data(self) -> List[User]:
        users: List[User] = UserFactory.create_batch(5)
        return users

    @pytest.fixture
    def user_update_set(self, user_data) -> UserUpdateSet:
        # NOTE: all users should have the same service slug + external id and therefore the same
        # service keys, so it's fine to just use the first user's services
        yield UserUpdateSet(
            user_data=user_data, service_data=[i.service for i in user_data[0].identities]
        )

    @pytest.fixture
    def edited_user_data(self, user_data):
        edited_data = copy.deepcopy(user_data)
        # Edit user identity
        edited_data[0].identities[1].matcher = {"email": "new_email@symops.io"}
        # Delete user identity
        del edited_data[1].identities[1]
        # Delete an user
        del edited_data[-1]
        # Add an user
        edited_data.append(UserFactory.create())

        return edited_data

    def test_from_dict_init(self, user_data):
        user_set = UserUpdateSet(user_data=user_data)
        assert len(user_set.users) == len(user_data)

    def test_compare_sets(self, user_update_set, edited_user_data):
        edited_set = UserUpdateSet(user_data=edited_user_data)
        result = UserUpdateSet.compare_user_sets(user_update_set, edited_set)

        assert len(result.update_user_ops) == 2
        assert result.update_user_ops[0].operation_type == OperationType.update_user

        assert len(result.delete_identities_ops) == 1
        assert (
            result.delete_identities_ops[0].operation_type
            == OperationType.delete_identity
        )

        assert len(result.delete_user_ops) == 1
        assert result.delete_user_ops[0].operation_type == OperationType.delete_user

    def test_tabulate(self, user_update_set: UserUpdateSet):
        expected_user_tabluation = [
            [identity.to_csv() for identity in u.identities]
            for u in user_update_set.users
        ]
        assert user_update_set.tabulate() == expected_user_tabluation

    def test_write_to_csv(self, user_update_set: UserUpdateSet, sandbox: Sandbox):
        expected_tabulation = [
            [identity.to_csv() for identity in u.identities] + [u.id]
            for u in user_update_set.users
        ]
        headers = ",".join(user_update_set.headers)
        # e.g. [["userid", "id1", "id2"], ["userid", "id3", "id4"]] -> userid,id1,id2\nuserid,id3,id4
        expected_csv_data = "\n".join(
            [",".join(user_data) for user_data in expected_tabulation]
        )
        expected_csv_data = f"{headers}\n{expected_csv_data}\n"

        path = f"{sandbox.path}/foo.csv"
        user_update_set.write_to_csv(path)
        with open(path) as f:
            assert f.read() == expected_csv_data
