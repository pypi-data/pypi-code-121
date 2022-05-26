from typing import List, Union, Optional

from perun.connector import perun_openapi
from perun.connector.adapters.AdapterInterface import AdapterInterface
from perun.connector.models.MemberStatusEnum import MemberStatusEnum
from perun.connector.utils.Logger import Logger
from perun.connector.models.Facility import Facility
from perun.connector.models.Group import Group
from perun.connector.models.Member import Member
from perun.connector.models.User import User
from perun.connector.models.UserExtSource import UserExtSource
from perun.connector.models.VO import VO
from perun.connector.perun_openapi import ApiClient, Configuration, ApiException
from perun.connector.perun_openapi.api.attributes_manager_api import AttributesManagerApi
from perun.connector.perun_openapi.api.facilities_manager_api import FacilitiesManagerApi
from perun.connector.perun_openapi.api.groups_manager_api import GroupsManagerApi
from perun.connector.perun_openapi.api.members_manager_api import MembersManagerApi
from perun.connector.perun_openapi.api.resources_manager_api import ResourcesManagerApi
from perun.connector.perun_openapi.api.searcher_api import SearcherApi
from perun.connector.perun_openapi.api.users_manager_api import UsersManagerApi
from perun.connector.perun_openapi.api.vos_manager_api import VosManagerApi
from perun.connector.perun_openapi.model.input_get_facilities import InputGetFacilities
from perun.connector.perun_openapi.model.input_set_user_ext_source_attributes import (
    InputSetUserExtSourceAttributes,
)
from perun.connector.utils.AttributeUtils import AttributeUtils


class PerunRpcAdapter(AdapterInterface):

    def __init__(self, config_data: dict[str, str], attrs_map):
        self._CONFIG = None
        self._logger = Logger.get_logger(self.__class__.__name__)
        self._BASIC_AUTH = "BasicAuth"
        self._BEARER_AUTH = "BearerAuth"
        self._API_KEY_AUTH = "ApiKeyAuth"

        self._set_up_openapi_config(config_data)

        self._RP_ID_ATTR = "perunFacilityAttr_rpID"
        self._ATTRIBUTE_UTILS = AttributeUtils(attrs_map)

    def _set_up_openapi_config(self, config_data: dict[str, str]) -> None:
        auth_type = config_data["auth_type"]
        self._CONFIG = Configuration(host=config_data["host"])

        if auth_type == self._BASIC_AUTH:
            self._CONFIG.username = config_data["username"]
            self._CONFIG.password = config_data["password"]
        elif auth_type == self._BEARER_AUTH:
            self._CONFIG.access_token = config_data["access_token"]
        elif auth_type == self._API_KEY_AUTH:
            self._CONFIG.api_key[self._API_KEY_AUTH] = config_data["api_key"]
        else:
            exception_message = (
                f'Authentication type "{auth_type}" is not a '
                f"supported way of authentication, please "
                f'set "auth_type" to one of "'
                f'{self._BASIC_AUTH}", "{self._BEARER_AUTH}" '
                f'or "{self._API_KEY_AUTH}"'
            )
            raise ValueError(exception_message)

    def get_perun_user(self, idp_id: str, uids: List[str]) -> Optional[User]:
        with ApiClient(self._CONFIG) as api_client:
            api_instance = UsersManagerApi(api_client)
            for uid in uids:
                try:
                    user = \
                        api_instance.get_user_by_ext_source_name_and_ext_login(
                            ext_login=uid, ext_source_name=idp_id
                        )
                    name = ""
                    for user_attr in [
                        "title_before",
                        "first_name",
                        "middle_name",
                        "last_name",
                        "title_after",
                    ]:
                        if user[user_attr] is not None:
                            name += user[user_attr] + " "

                    return User(user["id"], name.strip())
                except ApiException as ex:
                    if '"name":"UserExtSourceNotExistsException"' in ex.body:
                        continue
                    raise ex
            return None

    def _get_group_unique_name(
            self,
            attributes_api_instance: AttributesManagerApi,
            group_name: str,
            group_id: int,
    ) -> str:
        attr = attributes_api_instance.get_attribute(
            group=group_id,
            attribute_name="urn:perun:group:attribute-def:virt:voShortName",
        )
        return f'{attr["value"]}:{group_name}'

    def _create_internal_representation_groups(self,
                                               input_groups: List[
                                                   perun_openapi.model.group.Group
                                               ],
                                               converted_groups: List[Group],
                                               attributes_api_instance:
                                               AttributesManagerApi) -> None:
        unique_ids = []
        for group in input_groups:
            if group["id"] not in unique_ids:
                group["unique_name"] = self._get_group_unique_name(
                    attributes_api_instance, group["name"], group["id"]
                )
                converted_groups.append(
                    Group(
                        group["id"],
                        self.get_vo(vo_id=group["vo_id"]),
                        group["uuid"],
                        group["name"],
                        group["unique_name"],
                        group["description"],
                    )
                )
                unique_ids.append(group["id"])

    def get_member_groups(self, user: Union[User, int], vo: Union[VO, int]) -> List[Group]:
        with ApiClient(self._CONFIG) as api_client:
            members_api_instance = MembersManagerApi(api_client)
            groups_api_instance = GroupsManagerApi(api_client)
            attributes_api_instance = AttributesManagerApi(api_client)

            converted_groups = []
            vo_id = AdapterInterface.get_object_id(vo)
            user_id = AdapterInterface.get_object_id(user)
            try:
                member = members_api_instance.get_member_by_user(
                    vo_id, user_id
                )
                member_groups = []
                if member:
                    member_groups = groups_api_instance.get_all_member_groups(
                        member["id"]
                    )
                self._create_internal_representation_groups(member_groups,
                                                            converted_groups,
                                                            attributes_api_instance)  # noqa E501
            except ApiException as e:
                self._logger.warning(f' OpenAPI raised an exception: "{e}"')

            return converted_groups

    def get_sp_groups_by_facility(self, facility: Union[Facility, int]) -> List[Group]:
        if facility is None:
            return []

        with ApiClient(self._CONFIG) as api_client:
            attributes_api_instance = AttributesManagerApi(api_client)
            facilities_api_instance = FacilitiesManagerApi(api_client)
            resources_api_instance = ResourcesManagerApi(api_client)

            facility_id = AdapterInterface.get_object_id(facility)
            resources = (
                facilities_api_instance.get_assigned_resources_for_facility(
                    facility_id
                )
            )

            resources_ids = [resource.id for resource in resources]

            sp_groups = []
            for resource_id in resources_ids:
                groups = resources_api_instance.get_assigned_groups(
                    resource_id
                )

                self._create_internal_representation_groups(groups,
                                                            sp_groups,
                                                            attributes_api_instance)  # noqa E501
            return sp_groups

    def get_sp_groups_by_rp_id(self, rp_id: str) -> List[Group]:
        facility = self.get_facility_by_rp_identifier(rp_id)
        return self.get_sp_groups_by_facility(facility)

    def get_group_by_name(self, vo: Union[VO, int], name: str) -> Group:
        with ApiClient(self._CONFIG) as api_client:
            attributes_api_instance = AttributesManagerApi(api_client)
            groups_api_instance = GroupsManagerApi(api_client)

            vo_id = AdapterInterface.get_object_id(vo)
            group = groups_api_instance.get_group_by_name(vo_id, name)
            group_external_representation = [group]
            converted_group = []
            self._create_internal_representation_groups(
                group_external_representation,
                converted_group,
                attributes_api_instance)
            return converted_group[0]

    def get_vo(self, short_name=None, vo_id=None) -> Optional[VO]:
        with ApiClient(self._CONFIG) as api_client:
            vos_api_instance = VosManagerApi(api_client)

            if short_name and vo_id:
                raise ValueError(
                    "VO can be obtained either by its short_name or id, "
                    "not both "
                    "at the same time."
                )
            elif vo_id:
                vo_lookup_method = vos_api_instance.get_vo_by_id
                vo_lookup_attribute = vo_id
                identifier = "id"
            elif short_name:
                vo_lookup_method = vos_api_instance.get_vo_by_short_name
                vo_lookup_attribute = short_name
                identifier = "short name"
            else:
                raise ValueError(
                    "Neither short_name nor id was provided, please specify "
                    "exactly one to find VO by."
                )

            try:
                vo = vo_lookup_method(vo_lookup_attribute)
                return VO(vo.id, vo.name, vo.short_name)
            except ApiException as ex:
                vo_not_found = '"name":"VoNotExistsException"' in ex.body

                if vo_not_found:
                    self._logger.warning(
                        f'VO looked up by {identifier} "'
                        f'{vo_lookup_attribute}" does not exist in Perun.'
                    )
                    return None
                raise ex

    def get_facility_by_rp_identifier(
            self,
            rp_identifier: str,
    ) -> Optional[Facility]:
        with ApiClient(self._CONFIG) as api_client:
            facilities_api_instance = FacilitiesManagerApi(api_client)

            attr_name = self._ATTRIBUTE_UTILS.get_rpc_attr_name(
                self._RP_ID_ATTR
            )

            facilities = facilities_api_instance.get_facilities_by_attribute(
                attribute_name=attr_name, attribute_value=rp_identifier
            )

            if not facilities:
                self._logger.warning(
                    f"No facility with rpID '{rp_identifier}' found."
                )
                return None

            if len(facilities) > 1:
                self._logger.warning(
                    f"There is more than one facility with rpID '"
                    f"{rp_identifier}'."
                )
                return None
            return Facility(
                facilities[0]["id"],
                facilities[0]["name"],
                facilities[0]["description"],
                rp_identifier,
            )

    def get_users_groups_on_facility(
            self, facility: Union[Facility, int], user: Union[User, int]
    ) -> List[Group]:
        if facility is None:
            return []

        with ApiClient(self._CONFIG) as api_client:
            users_api_instance = UsersManagerApi(api_client)
            attributes_api_instance = AttributesManagerApi(api_client)

            facility_id = AdapterInterface.get_object_id(facility)
            user_id = AdapterInterface.get_object_id(user)
            users_groups_on_facility = (
                users_api_instance.get_groups_for_facility_where_user_is_active(  # noqa E501
                    user_id,
                    facility_id,
                )
            )
            converted_groups = []
            self._create_internal_representation_groups(
                users_groups_on_facility, converted_groups,
                attributes_api_instance)
            return converted_groups

    def get_users_groups_on_facility_by_rp_id(
            self, rp_identifier: str, user: Union[User, int]
    ) -> List[Group]:
        facility = self.get_facility_by_rp_identifier(rp_identifier)
        return self.get_users_groups_on_facility(facility, user)

    def _get_rp_id(self, facility: Facility) -> str:
        return self.get_facility_attributes(facility, [self._RP_ID_ATTR]) \
            .get(self._RP_ID_ATTR)

    # TODO test this method once SearcherAPI is supported on Devel
    def get_facilities_by_attribute_value(
            self, attribute: dict[str, str]
    ) -> List[Facility]:
        if len(attribute) != 1:
            self._logger.warning(
                f'Attribute must contain exactly one name and one value. '
                f'Given attribute contains: "{attribute}".'
            )
            return []

        with ApiClient(self._CONFIG) as api_client:
            searcher_api = SearcherApi(api_client)

            attribute_to_match_in_facilities = InputGetFacilities(attribute)
            perun_facilities = searcher_api.get_facilities(
                attribute_to_match_in_facilities
            )

            facilities = []
            for perun_facility in perun_facilities:
                facility = Facility(perun_facility['id'],
                                    perun_facility['name'],
                                    perun_facility['description'],
                                    "")
                facility.rp_id = self._get_rp_id(facility)
                facilities.append(facility)

        return facilities

    def get_facility_attributes(
            self, facility: Union[Facility, int], attr_names: List[str]
    ) -> dict[str, Union[str, Optional[int], bool, List[str], dict[str, str]]]:
        with ApiClient(self._CONFIG) as api_client:
            attributes_api_instance = AttributesManagerApi(api_client)

            facility_id = AdapterInterface.get_object_id(facility)

            attr_names_map = self._ATTRIBUTE_UTILS.get_rpc_attr_names(
                attr_names
            )
            perun_attrs = (
                attributes_api_instance.get_facility_attributes_by_names(
                    facility_id, list(attr_names_map.keys())
                )
            )
            facility_attrs = self._get_attributes(perun_attrs, attr_names_map)
            return {
                facility_attr_name: facility_attr["value"]
                for facility_attr_name, facility_attr in facility_attrs.items()
            }

    def get_user_ext_source(
            self, ext_source_name: str, ext_source_login: str
    ) -> UserExtSource:
        with ApiClient(self._CONFIG) as api_client:
            users_api_instance = UsersManagerApi(api_client)

            user_ext_source_perun = \
                users_api_instance.get_user_ext_source_by_ext_login_and_ext_source_name(  # noqa E501
                    ext_source_name=ext_source_name,
                    ext_source_login=ext_source_login
                )

            ext_source_id = user_ext_source_perun["id"]
            login = user_ext_source_perun["login"]

            ext_source_details = user_ext_source_perun["ext_source"]
            name = ext_source_details["name"]

            user = self.get_perun_user(ext_source_name, [ext_source_login])

            return UserExtSource(ext_source_id, name, login, user)

    def update_user_ext_source_last_access(
            self, user_ext_source: Union[UserExtSource, int]
    ) -> None:
        user_ext_source_id = AdapterInterface.get_object_id(user_ext_source)

        with ApiClient(self._CONFIG) as api_client:
            users_api_instance = UsersManagerApi(api_client)

            users_api_instance.update_user_ext_source_last_access(
                user_ext_source_id
            )

    def get_user_ext_source_attributes(
            self, user_ext_source: Union[UserExtSource, int], attr_names: List[str]
    ) -> dict[str, Union[str, Optional[int], bool, List[str], dict[str, str]]]:
        with ApiClient(self._CONFIG) as api_client:
            attributes_api_instance = AttributesManagerApi(api_client)

            user_ext_source_id = AdapterInterface.get_object_id(user_ext_source)

            attr_names_map = self._ATTRIBUTE_UTILS.get_rpc_attr_names(
                attr_names
            )
            perun_attrs = \
                attributes_api_instance.get_user_ext_source_attributes_by_names(  # noqa E501
                    user_ext_source=user_ext_source_id,
                    attr_names=list(attr_names_map.keys()),
                )
            return self._get_attributes(perun_attrs, attr_names_map)

    def set_user_ext_source_attributes(
            self,
            user_ext_source: Union[UserExtSource, int],
            attributes: List[
                dict[
                    str, Union[
                        str, Optional[int], bool, List[str], dict[str, str]]
                ]
            ],
    ) -> None:
        with ApiClient(self._CONFIG) as api_client:
            attributes_api_instance = AttributesManagerApi(api_client)

            user_ext_source_id = AdapterInterface.get_object_id(user_ext_source)
            attributes_api_instance.set_user_ext_source_attributes(
                InputSetUserExtSourceAttributes(user_ext_source_id, attributes)
            )

    def get_member_status_by_user_and_vo(
            self, user: Union[User, int], vo: Union[VO, int]
    ) -> Optional[str]:

        member = self.get_member_by_user(user, vo)

        if member is not None:
            return member.status

        return None

    def is_user_in_vo_by_short_name(self, user: Union[User, int], vo_short_name: str) -> bool:
        user_id = AdapterInterface.get_object_id(user)
        if not user_id:
            raise ValueError("User's ID is empty")

        if not vo_short_name:
            raise ValueError("VO short name is empty")

        vo_of_user = self.get_vo(short_name=vo_short_name)

        if vo_of_user is None:
            self._logger.debug(
                f'No VO with short name "{vo_short_name}" found')
            return False

        user_status = self.get_member_status_by_user_and_vo(user, vo_of_user)
        valid_status = MemberStatusEnum.VALID

        return user_status == valid_status

    def get_member_by_user(self, user: Union[User, int], vo: Union[VO, int]) -> Optional[Member]:
        with ApiClient(self._CONFIG) as api_client:
            members_api_instance = MembersManagerApi(api_client)

            user_id = AdapterInterface.get_object_id(user)
            vo_id = AdapterInterface.get_object_id(vo)

            try:
                member = members_api_instance.get_member_by_user(vo_id,
                                                                 user_id)
                return Member(member["id"], vo, member["status"])
            except ApiException as ex:
                user_not_found = '"name":"UserNotExistsException"' in ex.body
                vo_not_found = '"name":"VoNotExistsException"' in ex.body
                member_not_exists = '"name":"MemberNotExistsException"' in \
                                    ex.body

                if user_not_found:
                    self._logger.warning(
                        f'User with id "{user_id}" does not exist in '
                        f'Perun.'
                    )
                if vo_not_found:
                    self._logger.warning(
                        f'VO with id "{vo_id}" does not '
                        f'exist in Perun.'
                    )
                if member_not_exists:
                    self._logger.warning(
                        f'Member with VO "{vo_id}" and user id "'
                        f'{user_id}" does not exist in Perun.'
                    )

                if user_not_found or vo_not_found or member_not_exists:
                    return None

                raise ex

    def get_resource_capabilities_by_facility(
            self, facility: Union[Facility, int], user_groups: List[Union[Group, int]]
    ) -> List[str]:
        capabilities = []
        if facility is None:
            return capabilities

        with ApiClient(self._CONFIG) as api_client:
            facilities_api_instance = FacilitiesManagerApi(api_client)
            resources_api_instance = ResourcesManagerApi(api_client)
            attributes_api_instance = AttributesManagerApi(api_client)

            facility_id = AdapterInterface.get_object_id(facility)
            resources = (
                facilities_api_instance.get_assigned_resources_for_facility(
                    facility_id
                )
            )
            user_groups_ids = [AdapterInterface.get_object_id(user_group) for user_group in user_groups]
            for resource in resources:
                resource_groups = resources_api_instance.get_assigned_groups(
                    resource["id"]
                )

                resource_capabilities = attributes_api_instance.get_attribute(
                    resource=resource["id"],
                    attribute_name="urn:perun:resource:attribute-def:def"
                                   ":capabilities"
                )["value"]

                if resource_capabilities is None:
                    continue

                for resource_group in resource_groups:
                    if resource_group["id"] in user_groups_ids:
                        capabilities.extend(resource_capabilities)
                        break
        return capabilities

    def get_resource_capabilities_by_rp_id(
            self, rp_identifier: str, user_groups: List[Union[Group, int]]
    ) -> List[str]:
        facility = self.get_facility_by_rp_identifier(rp_identifier)
        return self.get_resource_capabilities_by_facility(facility, user_groups)

    def get_facility_capabilities_by_facility(self, facility: Union[Facility, int]) -> List[str]:
        if facility is None:
            return []

        with ApiClient(self._CONFIG) as api_client:
            attributes_api_instance = AttributesManagerApi(api_client)

            facility_id = AdapterInterface.get_object_id(facility)

            facility_capabilities = attributes_api_instance.get_attribute(
                facility=facility_id,
                attribute_name="urn:perun:facility:attribute-def:def"
                               ":capabilities",
            )["value"]

            return facility_capabilities

    def get_facility_capabilities_by_rp_id(self, rp_identifier: str) -> List[str]:
        facility = self.get_facility_by_rp_identifier(rp_identifier)
        return self.get_facility_capabilities_by_facility(facility)

    def get_user_attributes(
            self, user: Union[User, int], attr_names: List[str]
    ) -> dict[str, Union[str, Optional[int], bool, List[str], dict[str, str]]]:
        default_attribute_name = "perunUserAttribute_loa"
        if not attr_names:
            attr_names.append(default_attribute_name)

        with ApiClient(self._CONFIG) as api_client:
            attributes_api_instance = AttributesManagerApi(api_client)

            user_id = AdapterInterface.get_object_id(user)

            attr_names_map = self._ATTRIBUTE_UTILS.get_rpc_attr_names(
                attr_names
            )

            perun_attrs = attributes_api_instance.get_user_attributes_by_names(
                user_id, list(attr_names_map.keys())
            )

            user_attrs = self._get_attributes(perun_attrs, attr_names_map)

            return {
                user_attr_name: user_attr["value"]
                for user_attr_name, user_attr in user_attrs.items()
            }

    def get_entityless_attribute(
            self, attr_name: str
    ) -> Union[str, Optional[int], bool, List[str], dict[str, str]]:
        with ApiClient(self._CONFIG) as api_client:
            attributes_api_instance = AttributesManagerApi(api_client)

            attributes = {}
            perun_attr_values = (
                attributes_api_instance.get_entityless_attributes_by_name(
                    attr_name=self._ATTRIBUTE_UTILS.get_rpc_attr_name(
                        attr_name)
                )
            )

            attr_id = perun_attr_values[0].get("id")
            if attr_id is None:
                return attributes

            perun_attr_keys = attributes_api_instance.get_entityless_keys(
                attr_id
            )

            return dict(zip(perun_attr_keys, perun_attr_values))

    def get_vo_attributes(
            self, vo: Union[VO, int], attr_names: List[str]
    ) -> dict[str, Union[str, Optional[int], bool, List[str], dict[str, str]]]:
        default_attribute_name = "perunVoAttribute_id"
        if not attr_names:
            attr_names.append(default_attribute_name)

        with ApiClient(self._CONFIG) as api_client:
            attributes_api_instance = AttributesManagerApi(api_client)

            vo_id = AdapterInterface.get_object_id(vo)

            attr_names_map = self._ATTRIBUTE_UTILS.get_rpc_attr_names(
                attr_names
            )

            perun_attrs = attributes_api_instance.get_vo_attributes_by_names(
                vo_id, list(attr_names_map.keys())
            )

            vo_attrs = self._get_attributes(perun_attrs, attr_names_map)

            return {
                vo_attr_name: user_attr["value"]
                for vo_attr_name, user_attr in vo_attrs.items()
            }

    def get_facility_attribute(
            self, facility: Union[Facility, int], attr_name: str
    ) -> Union[str, Optional[int], bool, List[str], dict[str, str]]:
        with ApiClient(self._CONFIG) as api_client:
            attributes_api_instance = AttributesManagerApi(api_client)

            facility_id = AdapterInterface.get_object_id(facility)

            attr_name = self._ATTRIBUTE_UTILS.get_rpc_attr_name(attr_name)
            perun_attr = attributes_api_instance.get_attribute(
                facility=facility_id, attribute_name=attr_name
            )

            return perun_attr["value"]

    def _get_attributes(
            self, perun_attrs: List[dict[str, str]],
            attr_names_map: dict[str, str]
    ) -> dict[
        str,
        dict[str, Union[str, Optional[int], bool, List[str], dict[str, str]]],
    ]:
        attributes = {}
        for perun_attr in perun_attrs:
            perun_attr_name = perun_attr["namespace"] + ":" + perun_attr[
                "friendly_name"]

            attributes[attr_names_map[perun_attr_name]] = {
                "id": perun_attr["id"],
                "name": attr_names_map[perun_attr_name],
                "display_name": perun_attr["display_name"],
                "type": perun_attr["type"],
                "value": perun_attr["value"],
                "friendly_name": perun_attr["friendly_name"]
            }

        return attributes
