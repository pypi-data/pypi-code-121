import abc
from typing import List, Union, Optional

from perun.connector.models.Facility import Facility
from perun.connector.models.Group import Group
from perun.connector.models.HasIdAbstract import HasIdAbstract
from perun.connector.models.User import User
from perun.connector.models.UserExtSource import UserExtSource
from perun.connector.models.VO import VO


class AdapterInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (
                hasattr(subclass, "get_perun_user")
                and callable(subclass.get_perun_user)
                and hasattr(subclass, "get_group_by_name")
                and callable(subclass.get_group_by_name)
                and hasattr(subclass, "get_vo")
                and callable(subclass.get_vo)
                and hasattr(subclass, "get_member_groups")
                and callable(subclass.get_member_groups)
                and hasattr(subclass, "get_sp_groups_by_facility")
                and callable(subclass.get_sp_groups_by_facility)
                and hasattr(subclass, "get_sp_groups_by_rp_id")
                and callable(subclass.get_sp_groups_by_rp_id)
                and hasattr(subclass, "get_user_attributes")
                and callable(subclass.get_user_attributes)
                and hasattr(subclass, "get_entityless_attribute")
                and callable(subclass.get_entityless_attribute)
                and hasattr(subclass, "get_vo_attributes")
                and callable(subclass.get_vo_attributes)
                and hasattr(subclass, "get_facility_attribute")
                and callable(subclass.get_facility_attribute)
                and hasattr(subclass, "get_facility_by_rp_identifier")
                and callable(subclass.get_facility_by_rp_identifier)
                and hasattr(subclass, "get_users_groups_on_facility")
                and callable(subclass.get_users_groups_on_facility)
                and hasattr(subclass, "get_users_groups_on_facility_by_rp_id")
                and callable(subclass.get_users_groups_on_facility_by_rp_id)
                and hasattr(subclass, "get_facilities_by_attribute_value")
                and callable(subclass.get_facilities_by_attribute_value)
                and hasattr(subclass, "get_facility_attributes")
                and callable(subclass.get_facility_attributes)
                and hasattr(subclass, "get_user_ext_source")
                and callable(subclass.get_user_ext_source)
                and hasattr(subclass, "update_user_ext_source_last_access")
                and callable(subclass.update_user_ext_source_last_access)
                and hasattr(subclass, "get_user_ext_source_attributes")
                and callable(subclass.get_user_ext_source_attributes)
                and hasattr(subclass, "set_user_ext_source_attributes")
                and callable(subclass.set_user_ext_source_attributes)
                and hasattr(subclass, "get_member_status_by_user_and_vo")
                and callable(subclass.get_member_status_by_user_and_vo)
                and hasattr(subclass, "is_user_in_vo_by_short_name")
                and callable(subclass.is_user_in_vo_by_short_name)
                and hasattr(subclass, "get_resource_capabilities_by_facility")
                and callable(subclass.get_resource_capabilities_by_facility)
                and hasattr(subclass, "get_resource_capabilities_by_rp_id")
                and callable(subclass.get_resource_capabilities_by_rp_id)
                and hasattr(subclass, "get_facility_capabilities_by_facility")
                and callable(subclass.get_facility_capabilities_by_facility)
                and hasattr(subclass, "get_facility_capabilities_by_rp_id")
                and callable(subclass.get_facility_capabilities_by_rp_id)
                or NotImplemented
        )

    @abc.abstractmethod
    def get_perun_user(self, idp_id: str, uids: List[str]) -> Optional[User]:
        """Get Perun user with at least one of the uids"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_group_by_name(self, vo: Union[VO, int], name: str) -> Group:
        """Get Group based on its name"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_vo(self, short_name: str, vo_id: int) -> Optional[VO]:
        """Get VO by either its id or short name"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_member_groups(self, user: Union[User, int], vo: Union[VO, int]) -> List[Group]:
        """Get member groups of given user"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_sp_groups_by_facility(self, facility: Union[Facility, int]) -> List[Group]:
        """Get groups associated withs given Facility"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_sp_groups_by_rp_id(self, rp_id: str) -> List[Group]:
        """Get groups associated withs given SP entity"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_user_attributes(
            self, user: Union[User, int], attr_names: List[str]
    ) -> dict[str, Union[str, Optional[int], bool, List[str], dict[str, str]]]:
        """Get specified attributes of given user"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_entityless_attribute(
            self, attr_name: str
    ) -> Union[str, Optional[int], bool, List[str], dict[str, str]]:
        """Get value of given entityless attribute"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_vo_attributes(
            self, vo: Union[VO, int], attr_names: List[str]
    ) -> dict[str, Union[str, Optional[int], bool, List[str], dict[str, str]]]:
        """Get specified attributes of given VO"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_facility_attribute(
            self, facility: Union[Facility, int], attr_name: str
    ) -> Union[str, Optional[int], bool, List[str], dict[str, str]]:
        """Get specified attribute of given facility"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_facility_by_rp_identifier(
            self, rp_identifier: str
    ) -> Optional[Facility]:
        """Get specified facility based on given rp_identifier"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_users_groups_on_facility(
            self, facility: Union[Facility, int], user: Union[User, int]
    ) -> List[Group]:
        """Get groups of specified user on given facility"""
        raise NotImplementedError

    def get_users_groups_on_facility_by_rp_id(
            self, rp_identifier: str, user: Union[User, int]
    ) -> List[Group]:
        """Get groups of specified user on given facility by rp_id"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_facilities_by_attribute_value(
            self, attribute: dict[str, str]
    ) -> List[Facility]:
        """Search facilities based on given attribute value"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_facility_attributes(
            self, facility: Union[Facility, int], attr_names: List[str]
    ) -> dict[str, Union[str, Optional[int], bool, List[str], dict[str, str]]]:
        """Get specified attributes of given facility"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_user_ext_source(
            self, ext_source_name: str, ext_source_login: str
    ) -> UserExtSource:
        """Get user's external source based on external source name and
        login"""
        raise NotImplementedError

    @abc.abstractmethod
    def update_user_ext_source_last_access(
            self, user_ext_source: Union[UserExtSource, int]
    ) -> None:
        """Update user's last access of external source"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_user_ext_source_attributes(
            self, user_ext_source: Union[UserExtSource, int],
            attr_names: List[str]
    ) -> dict[str, Union[str, Optional[int], bool, List[str], dict[str, str]]]:
        """Get attributes of user's external source"""
        raise NotImplementedError

    @abc.abstractmethod
    def set_user_ext_source_attributes(
            self, user_ext_source: Union[UserExtSource, int],
            attributes: List[
                dict[str, Union[str, Optional[int], bool, List[str], dict[str, str]]]]
    ) -> None:
        """Set attributes of user's external source"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_member_status_by_user_and_vo(self, user: Union[User, int], vo: Union[VO, int]) -> str:
        """Get member's status based on given User and VO"""
        raise NotImplementedError

    @abc.abstractmethod
    def is_user_in_vo_by_short_name(self, user: Union[User, int], vo_short_name: str) -> bool:
        """Verifies whether given User is in given VO"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_resource_capabilities_by_facility(
            self, facility: Union[Facility, int], user_groups: List[Union[Group, int]]
    ) -> List[str]:
        """Obtains resource capabilities of groups linked to the facility
        with given facility or facility id"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_resource_capabilities_by_rp_id(
            self, rp_identifier: str, user_groups: List[Union[Group, int]]
    ) -> List[str]:
        """Obtains resource capabilities of groups linked to the facility
        with given entity ID"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_facility_capabilities_by_facility(self, facility: Union[Facility, int]) -> List[str]:
        """Obtains facility capabilities of facility with given facility or facility id"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_facility_capabilities_by_rp_id(self, rp_identifier: str) -> List[str]:
        """Obtains facility capabilities of facility with given rp identifier"""
        raise NotImplementedError

    @staticmethod
    def get_object_id(object_or_id: Union[HasIdAbstract, int]):
        if isinstance(object_or_id, HasIdAbstract):
            return object_or_id.id
        else:
            return object_or_id
