import inspect
from typing import List, Union, Optional

from perun.connector.adapters.PerunRpcAdapter import PerunRpcAdapter
from perun.connector.adapters.LdapAdapter import LdapAdapter
from perun.connector.adapters.LdapAdapter import AdapterSkipException
from perun.connector.utils.Logger import Logger

from perun.connector.adapters.AdapterInterface import AdapterInterface
from perun.connector.models.Facility import Facility
from perun.connector.models.Group import Group
from perun.connector.models.User import User
from perun.connector.models.UserExtSource import UserExtSource
from perun.connector.models.VO import VO
from perun.connector.perun_openapi import ApiException


class AdaptersManager(AdapterInterface):
    def __init__(self, config, attrs_map):
        self._logger = Logger.get_logger(self.__class__.__name__)
        self._STARTING_PRIORITY = 1
        self.adapters = {}

        adapters_info = config["adapters"]

        for adapter_info in adapters_info:
            config_data = adapter_info.copy()
            adapter_type = config_data.pop("type")
            priority = config_data.pop("priority")

            if adapter_type == "ldap":
                ldap_adapter = LdapAdapter(config_data, attrs_map)

                self.adapters[priority] = {
                    "name": "ldap_adapter",
                    "adapter": ldap_adapter,
                }
            elif adapter_type == "openApi":
                rpc_adapter = PerunRpcAdapter(config_data, attrs_map)

                self.adapters[priority] = {
                    "name": "rpc_adapter",
                    "adapter": rpc_adapter,
                }
            else:
                self._logger.warning(
                    f'Config file includes unsupported adapter type "'
                    f'{adapter_type}"'
                )

    def _execute_method_by_priority(self, method_name: str, *args):
        current_priority = self._STARTING_PRIORITY
        current_adapter = self.adapters.get(current_priority)

        while current_adapter is not None:
            adapter_impl = current_adapter["adapter"]
            try:
                return getattr(adapter_impl, method_name)(*args)
            except AdapterSkipException:
                self._logger.warning(
                    f'Method "{method_name}" is not supported by '
                    f'{current_adapter["name"]}. Going to try another '
                    f'adapter if available.')
                current_priority += 1
                current_adapter = self.adapters.get(current_priority)
            except ApiException as ex:
                if 'notexistsexception"' in ex.body.lower():
                    self._logger.warning(
                        "Requested entity doesn't exist in Perun")
                raise
            except Exception as ex:
                self._logger.warning(
                    f'Method "{method_name}" could not be executed '
                    f'successfully by {current_adapter["name"]}, exception '
                    f'occurred: "{ex}"')
                raise

        raise Exception(
            f'None of the provided adapters was able to resolve method "'
            f'{method_name}"'
        )

    def _get_caller_name(self):
        return inspect.stack()[1].function

    def get_perun_user(self, idp_id: str, uids: List[str]) -> Optional[User]:
        return self._execute_method_by_priority(
            self._get_caller_name(), idp_id, uids
        )

    def get_group_by_name(self, vo: Union[int, VO], name: str) -> Group:
        return self._execute_method_by_priority(
            self._get_caller_name(), vo, name
        )

    def get_vo(self, short_name: str, vo_id: int) -> VO:
        return self._execute_method_by_priority(
            self._get_caller_name(), short_name, vo_id
        )

    def get_member_groups(self, user: Union[int, User], vo: Union[int, VO]) -> List[Group]:
        return self._execute_method_by_priority(
            self._get_caller_name(), user, vo
        )

    def get_sp_groups_by_facility(self, facility: Union[Facility, int]) -> List[Group]:
        return self._execute_method_by_priority(
            self._get_caller_name(), facility
        )

    def get_sp_groups_by_rp_id(self, rp_id: str) -> List[Group]:
        return self._execute_method_by_priority(
            self._get_caller_name(), rp_id
        )

    def get_user_attributes(
            self, user: Union[int, User], attr_names: List[str]
    ) -> dict[str, Union[str, Optional[int], bool, List[str], dict[str, str]]]:
        return self._execute_method_by_priority(
            self._get_caller_name(), user, attr_names
        )

    def get_entityless_attribute(
            self, attr_name: str
    ) -> Union[str, Optional[int], bool, List[str], dict[str, str]]:
        return self._execute_method_by_priority(
            self._get_caller_name(), attr_name
        )

    def get_vo_attributes(
            self, vo: Union[int, VO], attr_names: List[str]
    ) -> dict[str, Union[str, Optional[int], bool, List[str], dict[str, str]]]:
        return self._execute_method_by_priority(
            self._get_caller_name(), vo, attr_names
        )

    def get_facility_attribute(
            self, facility: Union[int, Facility], attr_name: str
    ) -> Union[str, Optional[int], bool, List[str], dict[str, str]]:
        return self._execute_method_by_priority(
            self._get_caller_name(), facility, attr_name
        )

    def get_facility_by_rp_identifier(
            self, rp_identifier: str
    ) -> Facility:
        return self._execute_method_by_priority(
            self._get_caller_name(), rp_identifier
        )

    def get_users_groups_on_facility_by_rp_id(
            self, rp_identifier: str, user: Union[User, int]
    ) -> List[Group]:
        return self._execute_method_by_priority(
            self._get_caller_name(), rp_identifier, user
        )

    def get_users_groups_on_facility(
            self, facility: Union[Facility, int], user: Union[User, int]
    ) -> List[Group]:
        return self._execute_method_by_priority(
            self._get_caller_name(), facility, user
        )

    def get_facilities_by_attribute_value(
            self, attribute: dict[str, str]
    ) -> List[Facility]:
        return self._execute_method_by_priority(
            self._get_caller_name(), attribute
        )

    def get_facility_attributes(
            self, facility: Union[int, Facility], attr_names: List[str]
    ) -> dict[str, Union[str, Optional[int], bool, List[str], dict[str, str]]]:
        return self._execute_method_by_priority(
            self._get_caller_name(), facility, attr_names
        )

    def get_user_ext_source(
            self, ext_source_name: str, ext_source_login: str
    ) -> UserExtSource:
        return self._execute_method_by_priority(
            self._get_caller_name(), ext_source_name, ext_source_login
        )

    def update_user_ext_source_last_access(self, user_ext_source: str) -> None:
        return self._execute_method_by_priority(
            self._get_caller_name(), user_ext_source
        )

    def get_user_ext_source_attributes(
            self, user_ext_source: Union[int, UserExtSource],
            attr_names: List[str]
    ) -> dict[str, Union[str, Optional[int], bool, List[str], dict[str, str]]]:
        return self._execute_method_by_priority(
            self._get_caller_name(), user_ext_source
        )

    def set_user_ext_source_attributes(
            self, user_ext_source: Union[int, UserExtSource],
            attributes: List[
                dict[str, Union[str, Optional[int], bool, List[str], dict[str, str]]]]
    ) -> None:
        return self._execute_method_by_priority(
            self._get_caller_name(), user_ext_source
        )

    def get_member_status_by_user_and_vo(self, user: Union[int, User], vo: Union[int, VO]) -> str:
        return self._execute_method_by_priority(
            self._get_caller_name(), user, vo
        )

    def is_user_in_vo_by_short_name(self, user: Union[int, User], vo_short_name: str) -> bool:
        return self._execute_method_by_priority(
            self._get_caller_name(), user, vo_short_name
        )

    def get_resource_capabilities_by_facility(
            self, facility: Union[Facility, int], user_groups: List[Union[Group, int]]
    ) -> List[str]:
        return self._execute_method_by_priority(
            self._get_caller_name(), facility, user_groups
        )

    def get_resource_capabilities_by_rp_id(
            self, rp_identifier: str, user_groups: List[Union[Group, int]]
    ) -> List[str]:
        return self._execute_method_by_priority(
            self._get_caller_name(), rp_identifier, user_groups
        )

    def get_facility_capabilities_by_rp_id(self, rp_identifier: str) -> List[str]:
        return self._execute_method_by_priority(
            self._get_caller_name(), rp_identifier
        )

    def get_facility_capabilities_by_facility(self, facility: Union[Facility, int]) -> List[str]:
        return self._execute_method_by_priority(
            self._get_caller_name(), facility
        )
