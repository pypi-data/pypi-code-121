from __future__ import annotations

import re
from logging import Logger

from cloudshell.shell.flows.connectivity.models.connectivity_model import (
    ConnectivityActionModel,
)

from cloudshell.cp.vcenter.exceptions import BaseVCenterException
from cloudshell.cp.vcenter.handlers.network_handler import (
    AbstractNetwork,
    DVPortGroupHandler,
    NetworkHandler,
)
from cloudshell.cp.vcenter.handlers.vm_handler import VmHandler
from cloudshell.cp.vcenter.handlers.vnic_handler import VnicHandler
from cloudshell.cp.vcenter.models.connectivity_action_model import (
    VcenterConnectivityActionModel,
)

MAX_DVSWITCH_LENGTH = 60
QS_NAME_PREFIX = "QS"
PORT_GROUP_NAME_PATTERN = re.compile(rf"{QS_NAME_PREFIX}_.+_VLAN")


def generate_port_group_name(dv_switch_name: str, vlan_id: str, port_mode: str):
    dvs_name = dv_switch_name[:MAX_DVSWITCH_LENGTH]
    return f"{QS_NAME_PREFIX}_{dvs_name}_VLAN_{vlan_id}_{port_mode}"


def is_network_generated_name(net_name: str):
    return bool(PORT_GROUP_NAME_PATTERN.search(net_name))


def is_correct_vnic(expected_vnic: str, vnic_label: str) -> bool:
    """Check that expected vNIC name or number is equal to vNIC label.

    :param expected_vnic: vNIC name or number from the connectivity request
    :param vnic_label: vNIC name from VM
    """
    if expected_vnic.isdigit():
        index = vnic_label.rsplit(" ", 1)[-1]
        try:
            is_correct = int(index) == int(expected_vnic)
        except ValueError:
            is_correct = False
    else:
        is_correct = expected_vnic.lower() == vnic_label.lower()
    return is_correct


def get_available_vnic(
    vm: VmHandler,
    default_network: AbstractNetwork,
    reserved_networks: list[str],
    logger: Logger,
    vnic_name: str | None = None,
) -> VnicHandler:
    for vnic in vm.vnics:
        if vnic_name and not is_correct_vnic(vnic_name, vnic.label):
            continue

        network = vm.get_network_from_vnic(vnic)
        if (
            not network.name
            or network.name == default_network.name
            or (
                not is_network_generated_name(network.name)
                and network.name not in reserved_networks
            )
        ):
            break
    else:
        if len(vm.vnics) >= 10:
            raise BaseVCenterException("Limit of vNICs per VM is 10")
        vnic = vm.create_vnic(logger)
        if isinstance(default_network, DVPortGroupHandler):
            vm.connect_vnic_to_dv_port_group(vnic, default_network, logger)
        elif isinstance(default_network, NetworkHandler):
            vm.connect_vnic_to_network(vnic, default_network, logger)

        # we need to update vnic object to fill all attributes, e.g. mac_address
        vnic = vm.vnics[-1]
        assert vm.get_network_from_vnic(vnic).name == default_network.name

    return vnic


def get_existed_port_group_name(
    action: ConnectivityActionModel | VcenterConnectivityActionModel,
) -> str | None:
    # From vCenter Shell 4.2.1 and 5.0.1 we support "vCenter VLAN Port Group"
    # service that allows to connect to the existed Port Group. Before that we would
    # receive ConnectivityActionModel that know nothing about port_group_name
    pg_name = getattr(
        action.connection_params.vlan_service_attrs, "port_group_name", None
    )
    return pg_name


def should_remove_port_group(
    name: str, action: ConnectivityActionModel | VcenterConnectivityActionModel
) -> bool:
    return not bool(get_existed_port_group_name(action)) or is_network_generated_name(
        name
    )
