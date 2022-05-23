import json
from copy import deepcopy

import pytest

from cloudshell.shell.flows.connectivity.exceptions import ApplyConnectivityException
from cloudshell.shell.flows.connectivity.models.connectivity_model import (
    ConnectivityActionModel,
)
from cloudshell.shell.flows.connectivity.models.driver_response import (
    ConnectivityActionResult,
)
from cloudshell.shell.flows.connectivity.simple_flow import apply_connectivity_changes


def _add_vlan_action(action: ConnectivityActionModel) -> ConnectivityActionResult:
    return ConnectivityActionResult.success_result(action, "success msg")


def _remove_vlan_action(action: ConnectivityActionModel) -> ConnectivityActionResult:
    return ConnectivityActionResult.success_result(action, "success msg")


def test_apply_connectivity_changes(logger, action_request):
    action_req_remove = action_request
    action_req_set = deepcopy(action_request)
    action_req_set["type"] = "setVlan"
    action_req_set["actionId"] = "new action id"
    driver_request = json.dumps(
        {"driverRequest": {"actions": [action_req_remove, action_req_set]}}
    )

    res = apply_connectivity_changes(
        driver_request, _add_vlan_action, _remove_vlan_action, logger
    )
    assert json.loads(res) == {
        "driverResponse": {
            "actionResults": [
                {
                    "actionId": (
                        "96582265-2728-43aa-bc97-cefb2457ca44_0900c4b5-0f90-42e3-b495"
                    ),
                    "errorMessage": "",
                    "infoMessage": "success msg",
                    "success": True,
                    "type": "removeVlan",
                    "updatedInterface": "centos",
                },
                {
                    "actionId": "new action id",
                    "errorMessage": "",
                    "infoMessage": "success msg",
                    "success": True,
                    "type": "setVlan",
                    "updatedInterface": "centos",
                },
            ]
        }
    }


def test_apply_connectivity_changes_without_request():
    with pytest.raises(ApplyConnectivityException, match="Request is None or empty"):
        apply_connectivity_changes("", _add_vlan_action, _remove_vlan_action)
