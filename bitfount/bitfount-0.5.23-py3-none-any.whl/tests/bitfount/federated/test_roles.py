"""Tests roles.py module."""
from typing import Type
from unittest.mock import Mock

import pytest
from pytest import fixture

from bitfount.federated.roles import Role, _RolesMixIn
from tests.utils.helper import unit_test


@unit_test
class TestRolesMixIn:
    """Test RolesMixIn class."""

    @fixture
    def dummy_role_based_class(self) -> Type[_RolesMixIn]:
        """Returns dummy class that subclasses RolesMixIn."""

        class DummyClass(_RolesMixIn):
            def modeller(self) -> Mock:
                return Mock(role="modeller")

            def worker(self) -> Mock:
                return Mock(role="worker")

        return DummyClass

    def test_roles(self, dummy_role_based_class: Type[_RolesMixIn]) -> None:
        """Check that supported roles property works as expected."""
        assert dummy_role_based_class().roles == {Role.MODELLER, Role.WORKER}

    @pytest.mark.parametrize("role", ["modeller", "worker", "non_existent_role"])
    def test_create_supported_role(
        self, dummy_role_based_class: Type[_RolesMixIn], role: str
    ) -> None:
        """Check we can create roles properly by name."""
        available_roles = [item.value for item in Role]
        obj = dummy_role_based_class()
        if role in available_roles:
            modeller = obj.create(role)
            assert modeller.role == role
        else:
            with pytest.raises(ValueError):
                obj.create(role)
