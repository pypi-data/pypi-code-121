from perun.connector.adapters.LdapAdapter import LdapAdapter
from perun.connector.models.Facility import Facility
from perun.connector.models.Group import Group
from perun.connector.models.User import User
from perun.connector.models.VO import VO
from perun.connector.models.MemberStatusEnum import MemberStatusEnum
import pytest
from unittest.mock import patch, MagicMock

from perun.connector.utils.ConfigStore import ConfigStore

adapters_cfg = ConfigStore.get_adapters_manager_config().get('adapters')
ldapAdapterCfg = None
for adapter in adapters_cfg:
    if adapter["type"] == "ldap":
        ldapAdapterCfg = adapter
        break

ADAPTER = LdapAdapter(ldapAdapterCfg, ConfigStore.get_attribute_map())

# USER
USER_WITH_ALL = {
    "perunUserId": 1,
    "displayName": "Foe Toe",
    "cn": "Foe Toe",
    "mail": "foetoe@cesnet.cz"
}
USER_WITH_DN = {
    "perunUserId": 1,
    "displayName": "Foe Toe",
    "cn": []
}
USER_WITH_CN = {
    "perunUserId": 1,
    "displayName": "",
    "cn": ["Foe Toe"],
}
USER_WITHOUT_NAME = {
    "perunUserId": 1,
    "displayName": "",
    "cn": [],
}
USER_NOT_FOUND = None
USER = User(1, 'Foe Toe')
USER_WITHOUT_ID = User(None, 'Foe Without Toe')
USER_WITHOUT_NAME_INIT = User(1, None)
USER_DATA = {
    "perunUserId": 1,
    "displayName": "Foe Toe",
    "cn": "Foe Toe",
    "memberOf": ['perunGroupId=1,perunVoId=1,dc=perun,dc=cesnet,dc=cz',
                 'perunGroupId=2,perunVoId=1,dc=perun,dc=cesnet,dc=cz']
}
USER_DATA_EMPTY = {
    "perunUserId": 1,
    "displayName": "Foe Toe",
    "cn": "Foe Toe",
    "memberOf": []
}

# VO
TEST_VO = VO(1, 'organization', 'org')
TEST_FALSE_VO = VO(2, 'fake', 'fk')
VO_1 = {
    'perunVoId': '1',
    'description': ['voo1'],
    'o': ['vo1']
}
VO_2 = {
    'perunVoId': '1',
    'description': ['organization'],
    'o': ['org']
}

INITIALIZED_VO_1 = VO(1, 'voo1', 'vo1')
INITIALIZED_VO_2 = VO(1, 'organization', 'org')

# GROUP
GROUP_1 = {
    'perunGroupId': 1,
    'perunVoId': 1,
    'uuid': "",
    'cn': ["group1"],
    'perunUniqueGroupName': 'grp1',
    'description': ['this group1']
}
GROUP_2 = {
    'perunGroupId': 2,
    'perunVoId': 1,
    'uuid': "",
    'cn': ["group2"],
    'perunUniqueGroupName': 'grp2',
    'description': ['this group2']
}
GROUP_3 = {
    'perunGroupId': 3,
    'perunVoId': 1,
    'uuid': "",
    'cn': ["group3"],
    'perunUniqueGroupName': 'grp3',
    'description': ['this group3']
}
INITIALIZED_GROUP_1 = Group(1, TEST_VO, "", "group1", "grp1", "this group1")
INITIALIZED_GROUP_2 = Group(2, TEST_VO, "", "group2", "grp2", "this group2")
INITIALIZED_GROUP_3 = Group(3, TEST_VO, "", "group3", "grp3", "this group3")
INITIALIZED_GROUPS = [INITIALIZED_GROUP_1,
                      INITIALIZED_GROUP_2,
                      INITIALIZED_GROUP_3]
GROUPS_REPEATED = [GROUP_1, GROUP_1, GROUP_2, GROUP_3]
GROUPS = [GROUP_1, GROUP_2, GROUP_3]
GROUPS_EMPTY = []
GROUP_ID = {
    "perunGroupId": '1'
}

# FACILITY
FACILITY_DATA = {
    'perunFacilityId': '1',
    'cn': 'facility',
    'description': "this is a testing facility",
    'capabilities': ["capability1", "capability2"]
}
FACILITY = Facility(1, "facility", "this is a testing facility", '1')
FACILITY_EMPTY = None

# RESOURCE
RESOURCE_1 = {
    'perunVoId': '1',
    "assignedGroupId": ['1'],
    "perunResourceId": '1',
    "capabilities": ["capability1, capability2"]
}
RESOURCE_2 = {
    'perunVoId': '1',
    "assignedGroupId": ['1', '2', '3'],
    "perunResourceId": '2',
    "capabilities": ["capability1, capability2"]
}
RESOURCE_3 = {
    'perunVoId': '1',
    "assignedGroupId": [],
    "perunResourceId": '3',
    "capabilities": ["capability3"]
}
RESOURCES_REPEATED = [RESOURCE_1, RESOURCE_2]
RESOURCES_NOT_GROUPS = [RESOURCE_3]
RESOURCES_EMPTY = []
RESOURCES = [RESOURCE_2]


@patch(
    "perun.connector.connectors.LdapConnector.LdapConnector.search_for_entity"
)
def test_user_with_all(mock_request):
    ADAPTER.connector.search_for_entity = MagicMock(
        return_value=USER_WITH_ALL
    )
    user = ADAPTER.get_perun_user("1", ["1"])
    assert user == USER


@patch(
    "perun.connector.connectors.LdapConnector.LdapConnector.search_for_entity"
)
def test_user_with_dn(mock_request):
    ADAPTER.connector.search_for_entity = MagicMock(
        return_value=USER_WITH_DN
    )
    user = ADAPTER.get_perun_user("1", ["1"])
    assert user == USER


@patch(
    "perun.connector.connectors.LdapConnector.LdapConnector.search_for_entity"
)
def test_user_with_cn(mock_request):
    ADAPTER.connector.search_for_entity = MagicMock(
        return_value=USER_WITH_CN
    )
    user = ADAPTER.get_perun_user("1", ["1"])
    assert user == USER


@patch(
    "perun.connector.connectors.LdapConnector.LdapConnector.search_for_entity"
)
def test_user_without_name(mock_request):
    ADAPTER.connector.search_for_entity = MagicMock(
        return_value=USER_WITHOUT_NAME
    )
    user = ADAPTER.get_perun_user("1", ["1"])
    assert user == USER_WITHOUT_NAME_INIT


@patch(
    "perun.connector.connectors.LdapConnector.LdapConnector.search_for_entity"
)
def test_user_not_found(mock_request):
    ADAPTER.connector.search_for_entity = MagicMock(
        return_value=USER_NOT_FOUND
    )
    user = ADAPTER.get_perun_user("1", ["1"])
    assert user is None


@patch(
    "perun.connector.connectors.LdapConnector.LdapConnector.search_for_entity"
)
def test_group_exist_in_vo(mock_request):
    ADAPTER.connector.search_for_entity = MagicMock(
        side_effect=(GROUP_1, VO_2)
    )
    group = ADAPTER.get_group_by_name(TEST_VO, 'grp')
    assert group == INITIALIZED_GROUP_1


@patch(
    "perun.connector.connectors.LdapConnector.LdapConnector.search_for_entity"
)
def test_group_does_not_exist_in_vo(mock_request):
    ADAPTER.connector.search_for_entity = MagicMock(
        return_value=None
    )

    expected_error_message = 'Group with name: grp in VO: ' \
                             '2 does not exists in Perun LDAP.'

    with pytest.raises(Exception) as error:
        _ = ADAPTER.get_group_by_name(TEST_FALSE_VO, 'grp')

    assert str(error.value.args[0]) == expected_error_message


@patch(
    "perun.connector.connectors.LdapConnector.LdapConnector.search_for_entity"
)
def test_get_vo_by_short_name_that_exists(mock_request):
    ADAPTER.connector.search_for_entity = MagicMock(
        return_value=VO_1
    )
    vo = ADAPTER.get_vo('vo1')
    assert vo == INITIALIZED_VO_1


@patch(
    "perun.connector.connectors.LdapConnector.LdapConnector.search_for_entity"
)
def test_get_vo_by_id_that_exist(mock_request):
    ADAPTER.connector.search_for_entity = MagicMock(
        return_value=VO_1
    )
    vo = ADAPTER.get_vo(None, 1)
    assert vo == INITIALIZED_VO_1


@patch(
    "perun.connector.connectors.LdapConnector.LdapConnector.search_for_entity"
)
def test_get_vo_by_non_existent_short_name(mock_request):
    ADAPTER.connector.search_for_entity = MagicMock(
        return_value=None
    )
    expected_error_message = 'Vo with name: fake_short_name ' \
                             'does not exists in Perun LDAP.'

    with pytest.raises(Exception) as error:
        _ = ADAPTER.get_vo('fake_short_name')

    assert str(error.value.args[0]) == expected_error_message


@patch(
    "perun.connector.connectors.LdapConnector.LdapConnector.search_for_entity"
)
def test_get_vo_by_non_existent_id(mock_request):
    ADAPTER.connector.search_for_entity = MagicMock(
        return_value=None
    )
    expected_error_message = 'Vo with id: -1 does ' \
                             'not exists in Perun LDAP.'

    with pytest.raises(Exception) as error:
        _ = ADAPTER.get_vo(None, -1)

    assert str(error.value.args[0]) == expected_error_message


@patch(
    "perun.connector.connectors.LdapConnector.LdapConnector.search_for_entity"
)
def test_get_member_groups(mock_request):
    ADAPTER.connector.search_for_entity = MagicMock(
        side_effect=[USER_DATA, GROUP_1, VO_2, GROUP_2, VO_2]
    )
    groups = ADAPTER.get_member_groups(USER, TEST_VO)

    expected_groups = [INITIALIZED_GROUP_1, INITIALIZED_GROUP_2]
    assert expected_groups.sort(key=lambda x: x.id) == groups.sort(key=lambda x: x.id)


@patch(
    "perun.connector.connectors.LdapConnector.LdapConnector.search_for_entity"
)
def test_get_member_groups_empty(mock_request):
    ADAPTER.connector.search_for_entity = MagicMock(
        side_effect=[USER_DATA_EMPTY, GROUP_1, GROUP_2]
    )
    groups = ADAPTER.get_member_groups(USER, TEST_VO)
    assert groups == []


@patch(
    "perun.connector.adapters.LdapAdapter.LdapAdapter.get_vo"
)
@patch(
    "perun.connector.connectors.LdapConnector.LdapConnector.search_for_entities"
)
@patch(
    "perun.connector.connectors.LdapConnector.LdapConnector.search_for_entity"
)
def test_get_sp_groups(mock_request, mock_request2, mock_request3):
    ADAPTER.get_vo = MagicMock(
        return_value=TEST_VO
    )
    ADAPTER.connector.search_for_entities = MagicMock(
        return_value=RESOURCES
    )
    ADAPTER.connector.search_for_entity = MagicMock(
        side_effect=[GROUP_1, GROUP_2, GROUP_3]
    )

    groups = ADAPTER.get_sp_groups_by_facility(FACILITY)
    expected_groups = [INITIALIZED_GROUP_1, INITIALIZED_GROUP_2, INITIALIZED_GROUP_3]
    assert expected_groups.sort(key=lambda x: x.id) == groups.sort(key=lambda x: x.id)


@patch(
    "perun.connector.adapters.LdapAdapter.LdapAdapter.get_vo"
)
@patch(
    "perun.connector.connectors.LdapConnector.LdapConnector.search_for_entities"
)
@patch(
    "perun.connector.connectors.LdapConnector.LdapConnector.search_for_entity"
)
def test_get_sp_groups_repeated_groups(mock_request,
                                       mock_request2,
                                       mock_request3):
    ADAPTER.get_vo = MagicMock(
        return_value=TEST_VO
    )
    ADAPTER.connector.search_for_entities = MagicMock(
        return_value=RESOURCES_REPEATED
    )
    ADAPTER.connector.search_for_entity = MagicMock(
        side_effect=[GROUP_1, GROUP_1, GROUP_2, GROUP_3]
    )

    groups = ADAPTER.get_sp_groups_by_facility(FACILITY)
    expected_groups = [INITIALIZED_GROUP_1, INITIALIZED_GROUP_2, INITIALIZED_GROUP_3]
    assert expected_groups.sort(key=lambda x: x.id) == groups.sort(key=lambda x: x.id)


@patch(
    "perun.connector.adapters.LdapAdapter.LdapAdapter.get_facility_by_rp_identifier"
)
@patch(
    "perun.connector.connectors.LdapConnector.LdapConnector.search_for_entities"
)
def test_get_sp_groups_not_assigned_groups(mock_request, mock_request2):
    ADAPTER.get_facility_by_rp_identifier = MagicMock(
        return_value=FACILITY
    )
    ADAPTER.connector.search_for_entities = MagicMock(
        return_value=RESOURCES_NOT_GROUPS
    )

    groups = ADAPTER.get_sp_groups_by_facility(FACILITY)
    assert groups == []


@patch(
    "perun.connector.adapters.LdapAdapter.LdapAdapter.get_facility_by_rp_identifier"
)
@patch(
    "perun.connector.connectors.LdapConnector.LdapConnector.search_for_entities"
)
def test_get_sp_groups_empty_resources(mock_request, mock_request2):
    ADAPTER.get_facility_by_rp_identifier = MagicMock(
        return_value=FACILITY
    )
    ADAPTER.connector.search_for_entities = MagicMock(
        return_value=RESOURCES_EMPTY
    )

    groups = ADAPTER.get_sp_groups_by_facility(FACILITY)
    assert groups == []


@patch(
    "perun.connector.adapters.LdapAdapter.LdapAdapter.get_facility_by_rp_identifier"
)
def test_user_attributes(mock_request):
    empty_user_attributes = []
    ADAPTER.connector.search_for_entity = MagicMock(
        side_effect=[USER_WITH_ALL, USER_NOT_FOUND]
    )
    attributes = ADAPTER.get_user_attributes(USER, empty_user_attributes)
    assert attributes['displayName'] == 'Foe Toe'
    assert attributes['cn'] == 'Foe Toe'
    assert attributes['mail'] == 'foetoe@cesnet.cz'
    assert attributes['perunUserId'] == 1

    attributes = ADAPTER.get_user_attributes(USER, ['fakeAttribute'])
    assert not attributes


@patch(
    "perun.connector.connectors.LdapConnector.LdapConnector.search_for_entity"
)
def test_get_facility_by_rp_id(mock_request):
    ADAPTER.connector.search_for_entity = MagicMock(
        return_value=FACILITY_DATA
    )
    facility = ADAPTER.get_facility_by_rp_identifier('1')
    assert facility == FACILITY


@patch(
    "perun.connector.adapters.LdapAdapter.LdapAdapter.get_facility_by_rp_identifier"
)
def test_users_group_on_facility_facility_not_found(mock_request):
    ADAPTER.get_facility_by_rp_identifier = MagicMock(
        return_value=FACILITY_EMPTY
    )
    groups = ADAPTER.get_users_groups_on_facility(None, None)
    assert groups == []


@patch(
    "perun.connector.adapters.LdapAdapter.LdapAdapter.get_facility_by_rp_identifier"
)
@patch(
    "perun.connector.connectors.LdapConnector.LdapConnector.search_for_entities"
)
def test_users_group_on_facility_resources_not_found(mock_request,
                                                     mock_request2):
    ADAPTER.get_facility_by_rp_identifier = MagicMock(
        return_value=FACILITY
    )
    ADAPTER.connector.search_for_entities = MagicMock(
        return_value=RESOURCES_EMPTY
    )
    expected_error_message = 'Service with spEntityId: ' \
                             '1 hasn\'t assigned any resource.'

    with pytest.raises(Exception) as error:
        _ = ADAPTER.get_users_groups_on_facility(FACILITY, USER)

    assert str(error.value.args[0]) == expected_error_message


@patch(
    "perun.connector.adapters.LdapAdapter.LdapAdapter.get_facility_by_rp_identifier"
)
@patch(
    "perun.connector.connectors.LdapConnector.LdapConnector.search_for_entities"
)
def test_users_group_on_facility_groups_not_found(mock_request,
                                                  mock_request2):
    ADAPTER.get_facility_by_rp_identifier = MagicMock(
        return_value=FACILITY
    )
    ADAPTER.connector.search_for_entities = MagicMock(
        side_effect=[RESOURCES_REPEATED, GROUPS_EMPTY]
    )
    groups = ADAPTER.get_users_groups_on_facility(FACILITY, USER)

    assert groups == []


@patch(
    "perun.connector.adapters.LdapAdapter.LdapAdapter.get_vo"
)
@patch(
    "perun.connector.connectors.LdapConnector.LdapConnector.search_for_entities"
)
def test_users_group_on_facility_repeated_groups(mock_request, mock_request2):
    ADAPTER.get_vo = MagicMock(
        return_value=TEST_VO
    )
    ADAPTER.connector.search_for_entities = MagicMock(
        side_effect=[RESOURCES_REPEATED, GROUPS_REPEATED]
    )
    groups = ADAPTER.get_users_groups_on_facility(FACILITY, USER)
    expected_groups = [INITIALIZED_GROUP_1, INITIALIZED_GROUP_2, INITIALIZED_GROUP_3]
    assert expected_groups.sort(key=lambda x: x.id) == groups.sort(key=lambda x: x.id)


@patch(
    "perun.connector.adapters.LdapAdapter.LdapAdapter.get_vo"
)
@patch(
    "perun.connector.connectors.LdapConnector.LdapConnector.search_for_entities"
)
def test_users_group_on_facility_not_repeated_groups(mock_request,
                                                     mock_request2):
    ADAPTER.get_vo = MagicMock(
        return_value=TEST_VO
    )
    ADAPTER.connector.search_for_entities = MagicMock(
        side_effect=[RESOURCES_REPEATED, GROUPS]
    )
    groups = ADAPTER.get_users_groups_on_facility(FACILITY, USER)
    expected_groups = [INITIALIZED_GROUP_1, INITIALIZED_GROUP_2, INITIALIZED_GROUP_3]
    assert expected_groups.sort(key=lambda x: x.id) == groups.sort(key=lambda x: x.id)


@patch(
    "perun.connector.connectors.LdapConnector.LdapConnector.search_for_entity"
)
def test_member_status_invalid(mock_request):
    ADAPTER.connector.search_for_entity = MagicMock(
        return_value=None
    )
    expected_error_message = "Member status is other than valid. Skipping to another adapter to get MemberStatus"
    with pytest.raises(Exception) as error:
        _ = ADAPTER.get_member_status_by_user_and_vo(USER, TEST_VO)
    assert str(error.value.args[0] == expected_error_message)


@patch(
    "perun.connector.connectors.LdapConnector.LdapConnector.search_for_entity"
)
def test_member_status_valid(mock_request):
    ADAPTER.connector.search_for_entity = MagicMock(
        return_value=GROUP_ID
    )
    validity = ADAPTER.get_member_status_by_user_and_vo(USER, TEST_VO)
    assert validity == MemberStatusEnum.VALID


def test_is_user_in_vo_no_short_name():
    expected_error_message = 'voShortName is empty'

    with pytest.raises(Exception) as error:
        _ = ADAPTER.is_user_in_vo_by_short_name(USER, '')

    assert str(error.value.args[0]) == expected_error_message


def test_is_user_in_vo_user_without_id():
    expected_error_message = 'userId is empty'

    with pytest.raises(Exception) as error:
        _ = ADAPTER.is_user_in_vo_by_short_name(USER_WITHOUT_ID, 'org')

    assert str(error.value.args[0]) == expected_error_message


@patch(
    "perun.connector.adapters.LdapAdapter.LdapAdapter.get_vo"
)
def test_is_user_in_vo_vo_not_found(mock_request):
    ADAPTER.get_vo = MagicMock(
        return_value=None
    )
    user_in_vo = ADAPTER.is_user_in_vo_by_short_name(USER, 'fake_short_name')
    assert not user_in_vo


@patch(
    "perun.connector.adapters.LdapAdapter.LdapAdapter.get_vo"
)
@patch(
    "perun.connector.adapters.LdapAdapter.LdapAdapter.get_member_status_by_user_and_vo"
)
def test_is_not_user_in_vo(mock_request, mock_request2):
    ADAPTER.get_vo = MagicMock(
        return_value=TEST_VO
    )
    ADAPTER.get_member_status_by_user_and_vo = MagicMock(
        return_value=MemberStatusEnum.INVALID
    )
    user_in_vo = ADAPTER.is_user_in_vo_by_short_name(USER, 'org')
    assert not user_in_vo


@patch(
    "perun.connector.adapters.LdapAdapter.LdapAdapter.get_vo"
)
@patch(
    "perun.connector.adapters.LdapAdapter.LdapAdapter.get_member_status_by_user_and_vo"
)
def test_is_user_in_vo(mock_request, mock_request2):
    ADAPTER.get_vo = MagicMock(
        return_value=TEST_VO
    )
    ADAPTER.get_member_status_by_user_and_vo = MagicMock(
        return_value=MemberStatusEnum.VALID
    )
    user_in_vo = ADAPTER.is_user_in_vo_by_short_name(USER, 'org')
    assert user_in_vo


@patch(
    "perun.connector.adapters.LdapAdapter.LdapAdapter.get_facility_by_rp_identifier"
)
def test_resource_capabilities_no_facility(mock_request):
    ADAPTER.get_facility_by_rp_identifier = MagicMock(
        return_value=FACILITY_EMPTY
    )
    resource_capabilities = \
        ADAPTER.get_resource_capabilities_by_facility(FACILITY_EMPTY, INITIALIZED_GROUPS)
    assert resource_capabilities == []


@patch(
    "perun.connector.adapters.LdapAdapter.LdapAdapter.get_facility_by_rp_identifier"
)
@patch(
    "perun.connector.connectors.LdapConnector.LdapConnector.search_for_entities"
)
def test_resource_capabilities_empty(mock_request, mock_request2):
    ADAPTER.get_facility_by_rp_identifier = MagicMock(
        return_value=FACILITY
    )
    ADAPTER.connector.search_for_entities = MagicMock(
        return_value=RESOURCES_EMPTY
    )
    resource_capabilities = \
        ADAPTER.get_resource_capabilities_by_facility(FACILITY, INITIALIZED_GROUPS)
    assert resource_capabilities == []


@patch(
    "perun.connector.adapters.LdapAdapter.LdapAdapter.get_facility_by_rp_identifier"
)
@patch(
    "perun.connector.connectors.LdapConnector.LdapConnector.search_for_entities"
)
def test_resource_capabilities(mock_request, mock_request2):
    ADAPTER.get_facility_by_rp_identifier = MagicMock(
        return_value=FACILITY
    )
    ADAPTER.connector.search_for_entities = MagicMock(
        return_value=RESOURCES_REPEATED
    )
    resource_capabilities = \
        ADAPTER.get_resource_capabilities_by_facility(FACILITY, INITIALIZED_GROUPS)

    assert len(resource_capabilities) == 2
    assert "capability1, capability2" in resource_capabilities


@patch(
    "perun.connector.connectors.LdapConnector.LdapConnector.search_for_entity"
)
def test_facility_capabilities_empty(mock_request):
    ADAPTER.connector.search_for_entity = MagicMock(
        return_value=None
    )
    facility_capabilities = ADAPTER.get_facility_capabilities_by_facility(FACILITY)
    assert facility_capabilities == []


@patch(
    "perun.connector.connectors.LdapConnector.LdapConnector.search_for_entity"
)
def test_facility_capabilities(mock_request):
    ADAPTER.connector.search_for_entity = MagicMock(
        return_value=FACILITY_DATA
    )
    facility_capabilities = ADAPTER.get_facility_capabilities_by_facility(FACILITY)
    assert facility_capabilities == FACILITY_DATA['capabilities']
