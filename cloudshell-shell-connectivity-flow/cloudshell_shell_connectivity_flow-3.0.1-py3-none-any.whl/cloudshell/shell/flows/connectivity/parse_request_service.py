import json
from abc import ABC, abstractmethod
from typing import List, Type

from cloudshell.shell.flows.connectivity.helpers.vlan_helper import (
    iterate_dict_actions_by_vlan_range,
)
from cloudshell.shell.flows.connectivity.models.connectivity_model import (
    ConnectivityActionModel,
)


class AbstractParseConnectivityService(ABC):
    @abstractmethod
    def get_actions(self, request: str) -> List[ConnectivityActionModel]:
        raise NotImplementedError()


class ParseConnectivityRequestService(AbstractParseConnectivityService):
    def __init__(
        self,
        is_vlan_range_supported: bool,
        is_multi_vlan_supported: bool,
        connectivity_model_cls: Type[ConnectivityActionModel] = ConnectivityActionModel,
    ):
        """Parse a connectivity request and returns connectivity actions.

        :param is_vlan_range_supported: Indicates if VLAN ranges are supported
            like "120-130"
        :param is_multi_vlan_supported: Indicates if device supports comma separated
            VLAN request like "45, 65, 120-130"
        :param connectivity_model_cls: model that will be returned filled with request
            actions values
        """
        self.is_vlan_range_supported = is_vlan_range_supported
        self.is_multi_vlan_supported = is_multi_vlan_supported
        self.connectivity_model_cls = connectivity_model_cls

    def _iterate_dict_actions(self, request: str):
        dict_actions = json.loads(request)["driverRequest"]["actions"]
        for dict_action in dict_actions:
            yield from iterate_dict_actions_by_vlan_range(
                dict_action, self.is_vlan_range_supported, self.is_multi_vlan_supported
            )

    def get_actions(self, request: str) -> List[ConnectivityActionModel]:
        return [
            self.connectivity_model_cls.parse_obj(da)
            for da in self._iterate_dict_actions(request)
        ]
