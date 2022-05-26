
from perun.connector.connectors.LdapConnector import LdapConnector
from unittest.mock import patch, MagicMock

import pytest

from perun.connector.utils.ConfigStore import ConfigStore

loaded_config = ConfigStore.get_ldapc_config()
CONNECTOR = LdapConnector(loaded_config)

TEST_DATA = {
    "perunUserId": 1,
    "displayName": "Foe Toe",
    "cn": "Foe Toe",
    "memberOf": ['perunGroupId=1,perunVoId=1,dc=perun,dc=cesnet,dc=cz',
                 'perunGroupId=2,perunVoId=1,dc=perun,dc=cesnet,dc=cz']
}
TEST_DATA_2 = {
    "perunUserId": 2,
    "displayName": "Joe Doe",
    "cn": "Joe Doe",
    "memberOf": ['perunGroupId=1,perunVoId=1,dc=perun,dc=cesnet,dc=cz',
                 'perunGroupId=2,perunVoId=1,dc=perun,dc=cesnet,dc=cz']
}

TEST_ENTRIES = [TEST_DATA, TEST_DATA_2]
TEST_ENTRY = [TEST_DATA]
BASE = "ldap.base"
FILTERS = "(name=test_filters)"


@patch(
    "perun.connector.connectors.LdapConnector.LdapConnector._search"
)
def test_search_for_entity_not_found(mock_request):
    CONNECTOR._search = MagicMock(
        return_value=None
    )
    result = CONNECTOR.search_for_entity(BASE, FILTERS)
    assert not result


@patch(
    "perun.connector.connectors.LdapConnector.LdapConnector._search"
)
def test_search_for_entity_found(mock_request):
    CONNECTOR._search = MagicMock(
        return_value=TEST_ENTRY
    )
    result = CONNECTOR.search_for_entity(BASE, FILTERS)
    assert result == TEST_DATA


@patch(
    "perun.connector.connectors.LdapConnector.LdapConnector._search"
)
def test_search_for_entity_found_invalid(mock_request):
    CONNECTOR._search = MagicMock(
        return_value=TEST_ENTRIES
    )
    expected_error_message = 'ldap_connector.search_for_entity - ' \
                             'More than one entity found.' + ' query base:' \
                             + BASE + ', filter: ' + FILTERS + '.' + \
                             ' Hint: Use method ''search_for_entities if ' \
                             'you expect array of entities.'

    with pytest.raises(Exception) as error:
        _ = CONNECTOR.search_for_entity(BASE, FILTERS)

    assert str(error.value.args[0]) == expected_error_message


@patch(
    "perun.connector.connectors.LdapConnector.LdapConnector._search"
)
def test_search_for_entities_not_found(mock_request):
    CONNECTOR._search = MagicMock(
        return_value=None
    )
    result = CONNECTOR.search_for_entities(BASE, FILTERS)
    assert not result


@patch(
    "perun.connector.connectors.LdapConnector.LdapConnector._search"
)
def test_search_for_entities_found(mock_request):
    CONNECTOR._search = MagicMock(
        return_value=TEST_ENTRIES
    )
    result = CONNECTOR.search_for_entities(BASE, FILTERS)
    assert result == TEST_ENTRIES

    CONNECTOR._search = MagicMock(
        return_value=TEST_ENTRY
    )
    result = CONNECTOR.search_for_entities(BASE, FILTERS)
    assert result == TEST_ENTRY
