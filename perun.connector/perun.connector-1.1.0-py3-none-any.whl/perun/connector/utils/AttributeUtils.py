from typing import List, Optional

from perun.connector.utils.Logger import Logger


class AttributeUtils:
    def __init__(self, attrs_map):
        self._logger = Logger.get_logger(self.__class__.__name__)
        self._config = attrs_map
        self._LDAP = "ldap"
        self._RPC = "rpc"
        self._TYPE = "type"
        self._INTERNAL_ATTR_NAME = "internal_attr_name"
        self._set_default_values()

    def _set_default_values(self):
        if "perunFacilityAttr_rpID" not in self._config:
            self._config["perunFacilityAttr_rpID"] = {}
            self._config["perunFacilityAttr_rpID"][
                self._RPC] = "urn:perun:facility:attribute-def:def:entityID"
            self._config["perunFacilityAttr_rpID"][self._LDAP] = "entityID"
            self._config["perunFacilityAttr_rpID"][self._TYPE] = "string"

    def get_ldap_attr_name(self, internal_attr_name: str) -> str:
        return self._get_attr_name(internal_attr_name, self._LDAP)

    def get_rpc_attr_name(self, internal_attr_name: str) -> str:
        return self._get_attr_name(internal_attr_name, self._RPC)

    def _get_attr_name(
            self,
            internal_attr_name: str,
            interface: str,
    ) -> Optional[str]:
        attr_names_grouping = self._config.get(internal_attr_name)
        if attr_names_grouping is None:
            self._logger.warning(
                f'Missing "{internal_attr_name}" attribute in config file.'
            )
            return None

        attr_name = attr_names_grouping.get(interface)
        if attr_name is None:
            self._logger.warning(
                f'Missing attribute name for interface "{interface}" in '
                f'attrubute "{internal_attr_name}" in config file.'
            )
            return None

        return attr_name

    def create_ldap_attr_name_type_map(
            self, internal_attr_names: List[str]
    ) -> dict[str, dict[str, str]]:
        return self._create_attr_name_type_map(internal_attr_names, self._LDAP)

    def create_rpc_attr_name_type_map(
            self, internal_attr_names: List[str]
    ) -> dict[str, dict[str, str]]:
        return self._create_attr_name_type_map(internal_attr_names, self._RPC)

    def _create_attr_name_type_map(
            self, internal_attr_names: List[str], interface: str
    ) -> dict[str, dict[str, str]]:
        result = {}

        for internal_attr_name in internal_attr_names:
            attr_names_grouping = self._config.get(internal_attr_name)

            if attr_names_grouping is None:
                self._logger.warning(
                    f'Missing "{internal_attr_name}" attribute in config '
                    f'file, omitting this attribute from the result map.'
                )
                continue

            if interface in attr_names_grouping:
                result[attr_names_grouping[interface]] = {
                    self._INTERNAL_ATTR_NAME: internal_attr_name,
                    self._TYPE: attr_names_grouping[self._TYPE],
                }
        return result

    def get_ldap_attr_names(
            self, internal_attr_names: List[str]
    ) -> dict[str, str]:
        return self._get_attr_names(internal_attr_names, self._LDAP)

    def get_rpc_attr_names(
            self, internal_attr_names: List[str]
    ) -> dict[str, str]:
        return self._get_attr_names(internal_attr_names, self._RPC)

    def _get_attr_names(
            self, internal_attr_names: List[str], interface: str
    ) -> dict[str, str]:
        result = {}

        for internal_attr_name in internal_attr_names:
            attr_names_grouping = self._config.get(internal_attr_name)

            if attr_names_grouping is None:
                self._logger.warning(
                    f'Missing "{internal_attr_name}" attribute in config '
                    f'file, omitting this attribute from the result map.'
                )
                continue
            if interface in attr_names_grouping:
                result[attr_names_grouping[interface]] = internal_attr_name

        return result
