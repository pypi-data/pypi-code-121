import pytest

from cloudshell.shell.flows.connectivity.models.connectivity_model import (
    ConnectivityActionModel,
)

from cloudshell.cp.vcenter.models.connectivity_action_model import (
    VcenterConnectivityActionModel,
)
from cloudshell.cp.vcenter.utils.connectivity_helpers import get_existed_port_group_name


@pytest.fixture()
def action_request():
    return {
        "connectionId": "96582265-2728-43aa-bc97-cefb2457ca44",
        "connectionParams": {
            "vlanId": "10-11",
            "mode": "Trunk",
            "vlanServiceAttributes": [
                {
                    "attributeName": "QnQ",
                    "attributeValue": "False",
                    "type": "vlanServiceAttribute",
                },
                {
                    "attributeName": "CTag",
                    "attributeValue": "",
                    "type": "vlanServiceAttribute",
                },
                {
                    "attributeName": "Port Group Name",
                    "attributeValue": "existed-pg",
                    "type": "vlanServiceAttribute",
                },
            ],
            "type": "setVlanParameter",
        },
        "connectorAttributes": [
            {
                "attributeName": "Selected Network",
                "attributeValue": "2",
                "type": "connectorAttribute",
            },
            {
                "attributeName": "Interface",
                "attributeValue": "mac address",
                "type": "connectorAttribute",
            },
        ],
        "actionTarget": {
            "fullName": "centos",
            "fullAddress": "full address",
            "type": "actionTarget",
        },
        "customActionAttributes": [
            {
                "attributeName": "VM_UUID",
                "attributeValue": "vm_uid",
                "type": "customAttribute",
            },
            {
                "attributeName": "Vnic Name",
                "attributeValue": "vnic",
                "type": "customAttribute",
            },
        ],
        "actionId": "96582265-2728-43aa-bc97-cefb2457ca44_0900c4b5-0f90-42e3-b495",
        "type": "removeVlan",
    }


def test_connectivity_action_model_parse_port_group_name(action_request):
    action = VcenterConnectivityActionModel.parse_obj(action_request)
    assert get_existed_port_group_name(action) == "existed-pg"


def test_connectivity_action_model_without_port_group_name(action_request):
    del action_request["connectionParams"]["vlanServiceAttributes"][2]
    action = VcenterConnectivityActionModel.parse_obj(action_request)
    assert get_existed_port_group_name(action) is None


def test_connectivity_action_model_with_default_model(action_request):
    action = ConnectivityActionModel.parse_obj(action_request)
    assert get_existed_port_group_name(action) is None
