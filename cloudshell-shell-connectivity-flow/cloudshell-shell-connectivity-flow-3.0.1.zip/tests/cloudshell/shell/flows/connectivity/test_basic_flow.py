import json

import pytest

from cloudshell.shell.flows.connectivity.basic_flow import AbstractConnectivityFlow
from cloudshell.shell.flows.connectivity.models.connectivity_model import (
    ConnectivityActionModel,
)
from cloudshell.shell.flows.connectivity.models.driver_response import (
    ConnectivityActionResult,
)
from cloudshell.shell.flows.connectivity.parse_request_service import (
    ParseConnectivityRequestService,
)


@pytest.fixture()
def parse_connectivity_request_service():
    return ParseConnectivityRequestService(
        is_vlan_range_supported=True, is_multi_vlan_supported=True
    )


@pytest.fixture()
def connectivity_flow(parse_connectivity_request_service, logger):
    class ConnectivityFlow(AbstractConnectivityFlow):
        IS_SUCCESS = True

        def _generic_change_vlan_fn(
            self, action: ConnectivityActionModel
        ) -> ConnectivityActionResult:
            if self.IS_SUCCESS:
                return ConnectivityActionResult.success_result_vm(
                    action, "successful", "mac address"
                )
            else:
                return ConnectivityActionResult.fail_result(action, "fail")

        _set_vlan = _generic_change_vlan_fn
        _remove_vlan = _generic_change_vlan_fn
        _remove_all_vlans = _generic_change_vlan_fn

    return ConnectivityFlow(parse_connectivity_request_service, logger)


def test_connectivity_flow(connectivity_flow, driver_request):
    res = connectivity_flow.apply_connectivity(json.dumps(driver_request))
    assert res == (
        '{"driverResponse": {"actionResults": [{'
        '"actionId": "96582265-2728-43aa-bc97-cefb2457ca44_0900c4b5-0f90-42e3-b495", '
        '"type": "removeVlan", '
        '"updatedInterface": "mac address", '
        '"infoMessage": "successful", '
        '"errorMessage": "", '
        '"success": true'
        "}]}}"
    )


def test_connectivity_flow_failed(connectivity_flow, driver_request):
    connectivity_flow.IS_SUCCESS = False
    res = connectivity_flow.apply_connectivity(json.dumps(driver_request))
    assert json.loads(res) == {
        "driverResponse": {
            "actionResults": [
                {
                    "actionId": (
                        "96582265-2728-43aa-bc97-cefb2457ca44_0900c4b5-0f90-42e3-b495"
                    ),
                    "type": "removeVlan",
                    "updatedInterface": "centos",
                    "infoMessage": "",
                    "errorMessage": "fail",
                    "success": False,
                }
            ]
        }
    }


def test_connectivity_flow_set_vlan(connectivity_flow, driver_request):
    driver_request["driverRequest"]["actions"][0]["type"] = "setVlan"
    res = connectivity_flow.apply_connectivity(json.dumps(driver_request))
    assert res == (
        '{"driverResponse": {"actionResults": [{'
        '"actionId": "96582265-2728-43aa-bc97-cefb2457ca44_0900c4b5-0f90-42e3-b495", '
        '"type": "setVlan", '
        '"updatedInterface": "mac address", '
        '"infoMessage": "successful", '
        '"errorMessage": "", '
        '"success": true'
        "}]}}"
    )


def test_connectivity_flow_abstract_methods(parse_connectivity_request_service, logger):
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        AbstractConnectivityFlow(parse_connectivity_request_service, logger)


def test_abstract_methods_raises(
    parse_connectivity_request_service, logger, action_model
):
    class TestClass(AbstractConnectivityFlow):
        def _set_vlan(self, action: ConnectivityActionModel) -> str:
            return super()._set_vlan(action_model)

        def _remove_vlan(self, action: ConnectivityActionModel) -> str:
            return super()._remove_vlan(action_model)

    inst = TestClass(parse_connectivity_request_service, logger)
    with pytest.raises(NotImplementedError):
        inst._set_vlan(action_model)

    with pytest.raises(NotImplementedError):
        inst._remove_vlan(action_model)
