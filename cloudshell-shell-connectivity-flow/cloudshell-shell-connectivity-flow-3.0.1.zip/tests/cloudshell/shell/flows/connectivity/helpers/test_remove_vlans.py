from copy import deepcopy

from cloudshell.shell.flows.connectivity.helpers.remove_vlans import (
    prepare_remove_vlan_actions,
)
from cloudshell.shell.flows.connectivity.models.connectivity_model import (
    ConnectivityActionModel,
)


def test_prepare_remove_vlan_actions_for_cloud_providers(
    action_model: ConnectivityActionModel,
):
    sa1 = deepcopy(action_model)
    sa1.type = sa1.type.SET_VLAN
    set_actions = [sa1]
    ra1 = deepcopy(action_model)
    ra1.type = ra1.type.REMOVE_VLAN
    ra2 = deepcopy(ra1)
    ra2.custom_action_attrs.vnic = "vnic2"
    ra3 = deepcopy(ra2)
    ra3.connection_params.vlan_id = "25"
    remove_actions = [ra2, ra3]

    new_remove_actions = prepare_remove_vlan_actions(set_actions, remove_actions)

    assert len(new_remove_actions) == 2

    nra1 = new_remove_actions[0]
    assert nra1.custom_action_attrs.vm_uuid == ra2.custom_action_attrs.vm_uuid
    assert nra1.custom_action_attrs.vnic == ra2.custom_action_attrs.vnic
    assert nra1.connection_params.vlan_id == ra2.connection_params.vlan_id

    nra2 = new_remove_actions[1]
    assert nra2.custom_action_attrs.vm_uuid == ra3.custom_action_attrs.vm_uuid
    assert nra2.custom_action_attrs.vnic == ra3.custom_action_attrs.vnic
    assert nra2.connection_params.vlan_id == "25"
