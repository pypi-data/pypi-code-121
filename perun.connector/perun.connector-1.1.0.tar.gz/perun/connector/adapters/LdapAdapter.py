from typing import List, Union, Optional

from perun.connector.connectors.LdapConnector import LdapConnector
from perun.connector.models.Facility import Facility
from perun.connector.models.Group import Group
from perun.connector.models.User import User
from perun.connector.models.UserExtSource import UserExtSource
from perun.connector.models.VO import VO
from perun.connector.models.MemberStatusEnum import MemberStatusEnum
from perun.connector.utils.AttributeUtils import AttributeUtils
from perun.connector.utils.Logger import Logger
from perun.connector.adapters.AdapterInterface import AdapterInterface


class AdapterSkipException(Exception):
    def __init__(self, message='Adapter not able to execute given action'):
        self.message = message
        super().__init__(self.message)


class LdapAdapter(AdapterInterface):

    def __init__(self, config, attrs_map):
        self._logger = Logger.get_logger(self.__class__.__name__)
        self._ldap_base = config['base_dn']
        self.connector = LdapConnector(config)
        self._attribute_utils = AttributeUtils(attrs_map)
        self._RP_ID_ATTR = "perunFacilityAttr_rpID"

    def get_perun_user(self, idp_id: str, uids: List[str]) -> Optional[User]:
        query = ''
        for uid in uids:
            query += '(eduPersonPrincipalNames=' + uid + ')'

        if query == '':
            return None

        user = self.connector.search_for_entity(
            'ou=People,' + self._ldap_base, '(|' + query + ')',
            ['perunUserId', 'displayName', 'cn', 'givenName',
             'sn', 'preferredMail', 'mail'])

        if not user:
            return user
        if user['displayName']:
            name = user['displayName']
        elif user['cn']:
            name = user['cn'][0]
        else:
            name = None

        return User(user['perunUserId'], name)

    def get_group_by_name(self, vo: Union[VO, int], name: str) -> Group:
        vo_id = AdapterInterface.get_object_id(vo)
        group = self.connector.search_for_entity(
            'perunVoId=' + str(vo_id) + ',' + self._ldap_base,
            '(&(objectClass=perunGroup)(perunUniqueGroupName=' +
            name + '))', ['perunGroupId', 'cn', 'perunUniqueGroupName',
                          'perunVoId', 'uuid', 'description']
        )
        if not group:
            raise Exception('Group with name: ' + name + ' in VO: ' + str(vo_id) +
                            ' does not exists in Perun LDAP.')

        return self._create_internal_representation_group(group)

    def get_vo(self, short_name=None, vo_id=None) -> Optional[VO]:
        if short_name:
            vo = self.connector.search_for_entity(
                self._ldap_base,
                '(&(objectClass=perunVo)(o=' + short_name + '))',
                ['perunVoId', 'o', 'description']
            )

            if not vo:
                raise Exception('Vo with name: ' + short_name +
                                ' does not exists in Perun LDAP.')
        else:
            vo = self.connector.search_for_entity(
                self._ldap_base,
                '(&(objectClass=perunVo)(perunVoId=' + str(vo_id) + '))',
                ['o', 'description']
            )
            if not vo:
                raise Exception('Vo with id: ' + str(vo_id) +
                                ' does not exists in Perun LDAP.')

        return VO(
            vo_id or int(vo['perunVoId']),
            vo['description'][0],
            vo['o'][0]
        )

    def get_member_groups(self, user: Union[User, int], vo: Union[VO, int]) -> List[Group]:
        user_id = AdapterInterface.get_object_id(user)
        vo_id = AdapterInterface.get_object_id(vo)
        user_with_membership = self.connector.search_for_entity(
            'perunUserId=' + str(user_id) + ',ou=People,' + self._ldap_base,
            '(objectClass=perunUser)', ['perunUserId', 'memberOf'])
        groups = []
        for group_dn in user_with_membership['memberOf']:
            group_vo_id = group_dn.split(',')[1].split('=', 2)[1]
            if group_vo_id != str(vo_id):
                continue
            group = self.connector.search_for_entity(
                group_dn, '(objectClass=perunGroup)',
                ['perunGroupId', 'cn', 'perunUniqueGroupName',
                 'perunVoId', 'uuid', 'description'])
            groups.append(
                self._create_internal_representation_group(group)
            )

        return groups

    def get_sp_groups_by_facility(self, facility: Union[Facility, int]) -> List[Group]:
        if not facility:
            return []
        facility_id = AdapterInterface.get_object_id(facility)
        resources = self.connector.search_for_entities(
            self._ldap_base,
            '(&(objectClass=perunResource)(perunFacilityDn=perunFacilityId=' +
            str(facility_id) + ',' + self._ldap_base + '))',
            ['perunResourceId', 'assignedGroupId', 'perunVoId']
        )
        groups = []
        unique_ids = []

        for resource in resources:
            if 'assignedGroupId' in resource:
                for group_id in resource['assignedGroupId']:
                    group = self.connector.search_for_entity(
                        'perunGroupId=' + group_id + ',perunVoId=' +
                        resource['perunVoId'] + ',' + self._ldap_base,
                        '(objectClass=perunGroup)',
                        ['perunGroupId', 'cn', 'perunUniqueGroupName',
                         'perunVoId', 'uuid', 'description']
                    )
                    if group['perunGroupId'] not in unique_ids:
                        groups.append(
                            self._create_internal_representation_group(group)
                        )

                        unique_ids.append(group['perunGroupId'])
        return groups

    def get_sp_groups_by_rp_id(self, rp_id: str) -> List[Group]:
        facility = self.get_facility_by_rp_identifier(rp_id)
        return self.get_sp_groups_by_facility(facility)

    def get_user_attributes(
            self, user: Union[User, int], attr_names: List[str]
    ) -> dict[str, Union[str, Optional[int], bool, List[str], dict[str, str]]]:
        user_id = AdapterInterface.get_object_id(user)
        return self.connector.search_for_entity(
            'perunUserId=' + str(user_id) + ',ou=People,' + self._ldap_base,
            '(objectClass=perunUser)',
            attr_names
        )

    def get_entityless_attribute(
            self, attr_name: str
    ) -> Union[str, Optional[int], bool, List[str], dict[str, str]]:
        raise AdapterSkipException()

    def get_vo_attributes(
            self, vo: Union[VO, int], attr_names: List[str]
    ) -> dict[str, Union[str, Optional[int], bool, List[str], dict[str, str]]]:
        raise AdapterSkipException()

    def get_facility_attribute(
            self, facility: Union[Facility, int], attr_name: str
    ) -> Union[str, Optional[int], bool, List[str], dict[str, str]]:
        raise AdapterSkipException()

    def get_facility_by_rp_identifier(
            self,
            rp_identifier: str,
    ) -> Optional[Facility]:
        attr_name = \
            self._attribute_utils.get_ldap_attr_name(self._RP_ID_ATTR) \
            or "entityID"
        ldap_result = self.connector.search_for_entity(
            self._ldap_base,
            '(&(objectClass=perunFacility)(' + attr_name + '=' +
            rp_identifier + '))',
            ['perunFacilityId', 'cn', 'description']
        )
        if not ldap_result:
            self._logger.warning('perun:AdapterLdap: '
                                 'No facility with entityID \'' +
                                 rp_identifier + '\' found.')
            return

        return Facility(
            ldap_result['perunFacilityId'],
            ldap_result['cn'][0],
            ldap_result['description'][0],
            rp_identifier
        )

    def get_users_groups_on_facility(
            self, facility: Union[Facility, int], user: Union[User, int]
    ) -> List[Group]:

        if not facility:
            return []

        facility_id = AdapterInterface.get_object_id(facility)
        user_id = AdapterInterface.get_object_id(user)

        resources = self.connector.search_for_entities(
            self._ldap_base,
            '(&(objectClass=perunResource)(perunFacilityDn='
            'perunFacilityId=' +
            str(facility_id) + ',' + self._ldap_base + '))',
            ['perunResourceId']
        )

        self._logger.debug('Resources - ' + str(resources))

        if not resources:
            raise Exception('Service with spEntityId: ' + str(facility_id) +
                            ' hasn\'t assigned any resource.')
        resources_string = '(|'
        for resource in resources:
            resources_string += '(assignedToResourceId=' + \
                                resource['perunResourceId'] + ')'
        resources_string += ')'
        result_groups = []
        unique_ids = []
        groups = self.connector.search_for_entities(
            self._ldap_base,
            '(&(uniqueMember=perunUserId=' + str(user_id) + ', ou=People,' +
            self._ldap_base + ')' + resources_string + ')',
            ['perunGroupId', 'cn', 'perunUniqueGroupName',
             'perunVoId', 'uuid', 'description']
        )
        for group in groups:
            if group['perunGroupId'] not in unique_ids:
                result_groups.append(
                    self._create_internal_representation_group(group)
                )
                unique_ids.append(group['perunGroupId'])

        self._logger.debug('Groups - ' + str(result_groups))

        return result_groups

    def get_users_groups_on_facility_by_rp_id(self, rp_identifier: str, user: Union[User, int]):
        facility = self.get_facility_by_rp_identifier(rp_identifier)
        return self.get_users_groups_on_facility(facility, user)

    def get_facilities_by_attribute_value(self, attribute: dict[str, str]):
        raise AdapterSkipException()

    def get_facility_attributes(self, facility: Union[Facility, int], attr_names: List[str]):
        raise AdapterSkipException()

    def get_user_ext_source(self, ext_source_name: str, ext_source_login: str):
        raise AdapterSkipException()

    def update_user_ext_source_last_access(self, user_ext_source: Union[UserExtSource, int]):
        raise AdapterSkipException()

    def get_user_ext_source_attributes(self, user_ext_source: Union[UserExtSource, int], attr_names: List[str]):
        raise AdapterSkipException()

    def set_user_ext_source_attributes(self,
                                       user_ext_source: Union[UserExtSource, int],
                                       attributes: List[
                                           dict[str, Union[str, Optional[int], bool, List[str], dict[str, str]]]]
                                       ):
        raise AdapterSkipException()

    def get_member_status_by_user_and_vo(self, user: Union[User, int], vo: Union[VO, int]):
        user_id = AdapterInterface.get_object_id(user)
        vo_id = AdapterInterface.get_object_id(vo)
        group_id = self.connector.search_for_entity(
            self._ldap_base,
            '(&(objectClass=perunGroup)(cn=members)(perunVoId=' + str(vo_id) +
            ')(uniqueMember=perunUserId=' + str(user_id) + ', ou=People,' +
            self._ldap_base + '))',
            ['perunGroupId']
        )

        if not group_id:
            raise AdapterSkipException(
                "Member status is other than valid. Skipping to another adapter to get MemberStatus")

        return MemberStatusEnum.VALID

    def is_user_in_vo_by_short_name(self, user: Union[User, int], vo_short_name: str) -> bool:
        user_id = AdapterInterface.get_object_id(user)
        if not user_id:
            raise Exception('userId is empty')
        if vo_short_name == '':
            raise Exception('voShortName is empty')

        vo = self.get_vo(vo_short_name)
        if not vo:
            self._logger.debug('isUserInVo - No VO found, returning false')

            return False

        return MemberStatusEnum.VALID == self.get_member_status_by_user_and_vo(user, vo)

    def get_resource_capabilities_by_facility(
            self, facility: Union[Facility, int], user_groups: List[Union[Group, int]]
    ) -> List[str]:
        if not facility:
            return []

        facility_id = AdapterInterface.get_object_id(facility)
        resources = self.connector.search_for_entities(
            self._ldap_base,
            '(&(objectClass=perunResource)(perunFacilityDn=perunFacilityId=' +
            str(facility_id) + ',' + self._ldap_base + '))',
            ['capabilities', 'assignedGroupId']
        )

        user_groups_ids = []
        for user_group in user_groups:
            user_groups_ids.append(str(AdapterInterface.get_object_id(user_group)))

        resource_capabilities = []
        for resource in resources:
            if ('assignedGroupId' not in resource) or \
                    ('capabilities' not in resource):
                continue
            for group_id in resource['assignedGroupId']:
                if group_id in user_groups_ids:
                    for resource_capability in resource['capabilities']:
                        resource_capabilities.append(resource_capability)

                    break

        return resource_capabilities

    def get_resource_capabilities_by_rp_id(
            self, rp_identifier: str, user_groups: List[Union[Group, int]]
    ) -> List[str]:
        facility = self.get_facility_by_rp_identifier(rp_identifier)
        return self.get_resource_capabilities_by_facility(facility, user_groups)

    def get_facility_capabilities_by_facility(self, facility: Union[Facility, int]) -> List[str]:
        if facility is None:
            return []
        facility_id = AdapterInterface.get_object_id(facility)
        facility_capabilities = self.connector.search_for_entity(
            self._ldap_base,
            '(&(objectClass=perunFacility)(entityID=' +
            str(facility_id) + '))',
            ['capabilities']
        )

        if not facility_capabilities:
            return []

        return facility_capabilities['capabilities']

    def get_facility_capabilities_by_rp_id(self, rp_identifier: str) -> List[str]:
        facility = self.get_facility_by_rp_identifier(rp_identifier)
        return self.get_facility_capabilities_by_facility(facility)

    def _create_internal_representation_group(
            self, group: dict[str, str]
    ) -> Group:
        return Group(
            int(group['perunGroupId']),
            self.get_vo(vo_id=int(group['perunVoId'])),
            group['uuid'],
            group['cn'][0],
            group['perunUniqueGroupName'],
            group['description'][0] or ''
        )
