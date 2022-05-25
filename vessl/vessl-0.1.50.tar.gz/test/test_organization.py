from test.conftest import USE_MOCK

import pytest
from mock import Mock, patch

import vessl
from vessl.util.exception import InvalidOrganizationError
from vessl.util.random import random_string


@pytest.mark.skipif(USE_MOCK, reason="Does not run if mocking is used.")
class TestOrganization:
    organization_name = random_string()

    @classmethod
    def teardown_class(cls):
        vessl.vessl_api.organization_delete_api(organization_name=cls.organization_name)

    # Remove ordering because pytest executes all tests marked with orders (across all
    # test files), causing teardown to be called for test classes containing these
    # tests.
    # @pytest.mark.order(index=1)
    def test_create_organization(self):
        vessl.create_organization(
            organization_name=self.organization_name,
        )

    def test_read_organization(self):
        vessl.read_organization(self.organization_name)


def test_list_organizations():
    vessl.list_organizations()


def test_get_organization_name():
    with patch.object(vessl.vessl_api, "organization", None):
        with pytest.raises(InvalidOrganizationError):
            vessl.organization._get_organization_name()

    organization_name = "org"
    assert (
        vessl.organization._get_organization_name(organization_name=organization_name)
        == organization_name
    )

    organization = Mock()
    organization.name = organization_name
    with patch.object(vessl.vessl_api, "organization", organization):
        assert vessl.organization._get_organization_name() == organization_name
