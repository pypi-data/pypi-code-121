from __future__ import annotations

from contextlib import suppress
from logging import Logger
from threading import Lock
from typing import TYPE_CHECKING

from cloudshell.shell.flows.connectivity.basic_flow import AbstractConnectivityFlow
from cloudshell.shell.flows.connectivity.models.connectivity_model import (
    ConnectivityActionModel,
)
from cloudshell.shell.flows.connectivity.models.driver_response import (
    ConnectivityActionResult,
)
from cloudshell.shell.flows.connectivity.parse_request_service import (
    AbstractParseConnectivityService,
)

from cloudshell.cp.vcenter.exceptions import BaseVCenterException
from cloudshell.cp.vcenter.handlers.dc_handler import DcHandler
from cloudshell.cp.vcenter.handlers.managed_entity_handler import ManagedEntityNotFound
from cloudshell.cp.vcenter.handlers.network_handler import (
    AbstractNetwork,
    DVPortGroupHandler,
    NetworkHandler,
    NetworkNotFound,
)
from cloudshell.cp.vcenter.handlers.si_handler import SiHandler
from cloudshell.cp.vcenter.handlers.switch_handler import (
    AbstractSwitchHandler,
    DvSwitchNotFound,
)
from cloudshell.cp.vcenter.handlers.vm_handler import VmHandler
from cloudshell.cp.vcenter.handlers.vsphere_api_handler import (
    NotEnoughPrivilegesListObjectTags,
)
from cloudshell.cp.vcenter.handlers.vsphere_sdk_handler import VSphereSDKHandler
from cloudshell.cp.vcenter.models.connectivity_action_model import (
    VcenterConnectivityActionModel,
)
from cloudshell.cp.vcenter.resource_config import VCenterResourceConfig
from cloudshell.cp.vcenter.utils.connectivity_helpers import (
    generate_port_group_name,
    get_available_vnic,
    get_existed_port_group_name,
    should_remove_port_group,
)

if TYPE_CHECKING:
    from cloudshell.cp.core.reservation_info import ReservationInfo


class DvSwitchNameEmpty(BaseVCenterException):
    def __init__(self):
        msg = "For connectivity actions you have to specify default DvSwitch"
        super().__init__(msg)


class VCenterConnectivityFlow(AbstractConnectivityFlow):
    def __init__(
        self,
        resource_conf: VCenterResourceConfig,
        reservation_info: ReservationInfo,
        parse_connectivity_request_service: AbstractParseConnectivityService,
        logger: Logger,
    ):
        super().__init__(parse_connectivity_request_service, logger)
        self._resource_conf = resource_conf
        self._reservation_info = reservation_info
        self._si = SiHandler.from_config(resource_conf, logger)
        self._vsphere_client = VSphereSDKHandler.from_config(
            resource_config=self._resource_conf,
            reservation_info=self._reservation_info,
            logger=self._logger,
            si=self._si,
        )
        self._network_lock = Lock()

    def apply_connectivity(self, request: str) -> str:
        self._validate_dvs_present()
        return super().apply_connectivity(request)

    def _validate_dvs_present(self):
        if not self._resource_conf.default_dv_switch:
            raise DvSwitchNameEmpty

    def _set_vlan(
        self, action: ConnectivityActionModel | VcenterConnectivityActionModel
    ) -> ConnectivityActionResult:
        vlan_id = action.connection_params.vlan_id
        vc_conf = self._resource_conf
        dc = DcHandler.get_dc(vc_conf.default_datacenter, self._si)
        vm = dc.get_vm_by_uuid(action.custom_action_attrs.vm_uuid)
        default_network = dc.get_network(vc_conf.holding_network)
        self._logger.info(f"Start setting vlan {vlan_id} for the {vm}")

        switch = self._get_switch(dc, vm)
        with self._network_lock:
            vnic = get_available_vnic(
                vm,
                default_network,
                vc_conf.reserved_networks,
                self._logger,
                action.custom_action_attrs.vnic,
            )
            network = self._get_or_create_network(dc, switch, action)
            try:
                if isinstance(network, DVPortGroupHandler):
                    vm.connect_vnic_to_dv_port_group(vnic, network, self._logger)
                else:
                    vm.connect_vnic_to_network(vnic, network, self._logger)
            except Exception:
                if should_remove_port_group(network.name, action):
                    self._remove_network(network, vm)
                raise
        msg = f"Setting VLAN {vlan_id} successfully completed"
        return ConnectivityActionResult.success_result_vm(action, msg, vnic.mac_address)

    def _remove_vlan(self, action: ConnectivityActionModel) -> ConnectivityActionResult:
        vc_conf = self._resource_conf
        dc = DcHandler.get_dc(vc_conf.default_datacenter, self._si)
        vm = dc.get_vm_by_uuid(action.custom_action_attrs.vm_uuid)
        default_network = dc.get_network(vc_conf.holding_network)
        vnic = vm.get_vnic_by_mac(action.connector_attrs.interface, self._logger)
        network = vm.get_network_from_vnic(vnic)
        self._logger.info(f"Start disconnecting {network} from the {vnic} on the {vm}")

        if isinstance(default_network, DVPortGroupHandler):
            vm.connect_vnic_to_dv_port_group(vnic, default_network, self._logger)
        else:
            vm.connect_vnic_to_network(vnic, default_network, self._logger)

        with suppress(ManagedEntityNotFound):  # network can be already removed
            if should_remove_port_group(network.name, action):
                self._remove_network_tags(network)
                self._remove_network(network, vm)

        msg = "Removing VLAN successfully completed"
        return ConnectivityActionResult.success_result_vm(action, msg, vnic.mac_address)

    def _get_switch(self, dc: DcHandler, vm: VmHandler) -> AbstractSwitchHandler:
        try:
            switch = dc.get_dv_switch(self._resource_conf.default_dv_switch)
        except DvSwitchNotFound:
            switch = vm.get_v_switch(self._resource_conf.default_dv_switch)
        return switch

    def _get_or_create_network(
        self,
        dc: DcHandler,
        switch: AbstractSwitchHandler,
        action: ConnectivityActionModel | VcenterConnectivityActionModel,
    ) -> NetworkHandler | DVPortGroupHandler:
        pg_name = get_existed_port_group_name(action)
        if pg_name:
            network = dc.get_network(pg_name)
        else:
            network = self._create_network_based_on_vlan_id(dc, switch, action)
        return network

    def _create_network_based_on_vlan_id(
        self,
        dc: DcHandler,
        switch: AbstractSwitchHandler,
        action: ConnectivityActionModel | VcenterConnectivityActionModel,
    ) -> AbstractNetwork:
        port_mode = action.connection_params.mode
        vlan_id = action.connection_params.vlan_id
        pg_name = generate_port_group_name(switch.name, vlan_id, port_mode.value)

        try:
            network = dc.get_network(pg_name)
        except NetworkNotFound:
            switch.create_port_group(
                pg_name,
                vlan_id,
                port_mode,
                self._resource_conf.promiscuous_mode,
                self._logger,
            )
            port_group = switch.wait_port_group_appears(pg_name)
            network = dc.wait_network_appears(pg_name)
            if self._vsphere_client:
                try:
                    self._vsphere_client.assign_tags(obj=network)
                except Exception:
                    port_group.destroy()
                    raise
        return network

    @staticmethod
    def _remove_network(network: DVPortGroupHandler | NetworkHandler, vm: VmHandler):
        if network.wait_network_become_free():
            if isinstance(network, DVPortGroupHandler):
                network.destroy()
            else:
                vm.host.remove_port_group(network.name)

    def _remove_network_tags(self, network: AbstractNetwork):
        """Remove network's tags.

        NotEnoughPrivilegesListObjectTags error can mean that the network can be already
        removed. But we ought to check, if it isn't removed reraise the Tag's error.
        """
        if self._vsphere_client:
            try:
                self._vsphere_client.delete_tags(network)
            except NotEnoughPrivilegesListObjectTags:
                if not network.wait_network_disappears():
                    raise
