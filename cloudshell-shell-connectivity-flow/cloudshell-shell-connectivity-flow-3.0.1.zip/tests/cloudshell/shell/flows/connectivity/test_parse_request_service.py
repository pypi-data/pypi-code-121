import json
from typing import List

import pytest

from cloudshell.shell.flows.connectivity.models.connectivity_model import (
    ConnectivityActionModel,
)
from cloudshell.shell.flows.connectivity.parse_request_service import (
    AbstractParseConnectivityService,
    ParseConnectivityRequestService,
)


def test_abstract_parse_connectivity_request_service_initialize():
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        AbstractParseConnectivityService()


def test_abstract_parse_connectivity_request_service_get_actions_raises(driver_request):
    class TestClass(AbstractParseConnectivityService):
        def get_actions(self, request: str) -> List[ConnectivityActionModel]:
            super().get_actions(request)

    service = TestClass()
    with pytest.raises(NotImplementedError):
        service.get_actions(driver_request)


def test_parse_connectivity_request_service(driver_request):
    service = ParseConnectivityRequestService(
        is_vlan_range_supported=False, is_multi_vlan_supported=False
    )
    actions = service.get_actions(json.dumps(driver_request))
    assert len(actions) == 2
    first, second = actions
    assert first.connection_params.vlan_id == "10"
    assert second.connection_params.vlan_id == "11"
    assert first.action_id == second.action_id
