from cloudshell.shell.flows.connectivity.models.connectivity_model import (
    ConnectivityActionModel,
)


def test_connectivity_action_model(action_request):
    action = ConnectivityActionModel.parse_obj(action_request)
    assert action.action_id == action_request["actionId"]
    assert action.type is action.type.REMOVE_VLAN
    assert action.type.value == "removeVlan"
    assert action.connection_id == action_request["connectionId"]
    assert action.connection_params.vlan_id == "10-11"
    assert action.connection_params.mode is action.connection_params.mode.TRUNK
    assert action.connection_params.mode.value == "Trunk"
    assert action.connection_params.vlan_service_attrs.qnq is False
    assert action.connection_params.vlan_service_attrs.ctag == ""
    assert action.connector_attrs.interface == "mac address"
    assert action.action_target.name == "centos"
    assert action.action_target.address == "full address"
    assert action.custom_action_attrs.vm_uuid == "vm_uid"
    assert action.custom_action_attrs.vnic == "vnic"


def test_connectivity_action_model_strip_vnic_name(action_request):
    assert action_request["customActionAttributes"][1]["attributeName"] == "Vnic Name"
    action_request["customActionAttributes"][1]["attributeValue"] = " vnic name "

    action = ConnectivityActionModel.parse_obj(action_request)

    assert action.custom_action_attrs.vnic == "vnic name"
