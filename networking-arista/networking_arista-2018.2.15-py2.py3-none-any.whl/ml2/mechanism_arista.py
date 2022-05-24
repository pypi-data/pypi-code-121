# Copyright (c) 2013 OpenStack Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json

from neutron_lib.api.definitions import portbindings
from neutron_lib import constants as n_const
from neutron_lib.plugins.ml2 import api as driver_api
from oslo_concurrency import lockutils
from oslo_config import cfg
from oslo_log import log as logging

from neutron.db import segments_db
from neutron.services.trunk import constants as trunk_consts

from networking_arista.common import constants as a_const
from networking_arista.common import db_lib
from networking_arista.ml2 import arista_sync
from networking_arista.ml2 import arista_trunk
from networking_arista.ml2.rpc.arista_eapi import AristaRPCWrapperEapi

# When used as a Neutron plugin, neutron-lib imports this code. However earlier
# neutron-lib has already imported 'multiprocessing'. This means the python
# module cache (sys.modules) contains a version of 'multiprocessing' where
# select.poll() exists.
#
# Further down we import arista_sync, which spawns a greenthread. This
# greenthread then uses a green version of 'multiprocessing' where
# select.poll() has been removed.
#
# Doing here multiprocessing.Queue.put() and in the greenthread
# multiprocessing.Queue.get(timeout=...) leads to:
# AttributeError: module 'select' has no attribute 'poll'
#
# We can't do eventlet.monkey_patch() early enough (before the first
# 'mutiprocessing' import) as we would have to do it in neutron-lib and it's
# forbidden, see https://review.opendev.org/#/c/333017/
#
# The solution is to let the python module cache here forget the already
# imported 'multiprocessing' and re-import a green one. Here again
# eventlet.monkey_patch() doesn't seem to help as it doesn't seem to touch
# 'multiprocessing'. Thus we use eventlet.import_patched() instead:
import eventlet
import sys
modules_to_forget = []
for imported_module_name in sys.modules:
    if imported_module_name.startswith('multiprocessing'):
        modules_to_forget.append(imported_module_name)
for module_to_forget in modules_to_forget:
    del sys.modules[module_to_forget]

for module_to_forget in modules_to_forget:
    try:
        eventlet.import_patched(module_to_forget)
    except ImportError:
        pass

# import a green 'multiprocessing':
multiprocessing = eventlet.import_patched('multiprocessing')
from networking_arista.ml2 import arista_sync  # noqa: E402


LOG = logging.getLogger(__name__)
cfg.CONF.import_group('ml2_arista', 'networking_arista.common.config')


def log_context(function, context):
    pretty_context = json.dumps(context, sort_keys=True, indent=4)
    LOG.debug(function)
    LOG.debug(pretty_context)


class MechResource(object):
    """Container class for passing data to sync worker"""

    def __init__(self, id, resource_type, action, related_resources=None):
        self.id = id
        self.resource_type = resource_type
        self.action = action
        self.related_resources = related_resources or list()

    def __str__(self):
        return "%s %s ID: %s" % (self.action, self.resource_type, self.id)


class AristaDriver(driver_api.MechanismDriver):
    """Ml2 Mechanism driver for Arista networking hardware.

    Remembers all networks and VMs that are provisioned on Arista Hardware.
    Does not send network provisioning request if the network has already been
    provisioned before for the given port.
    """
    def __init__(self):
        confg = cfg.CONF.ml2_arista
        self.managed_physnets = confg['managed_physnets']
        self.manage_fabric = confg['manage_fabric']
        self.eapi = AristaRPCWrapperEapi()
        self.mlag_pairs = dict()

        self.provision_queue = multiprocessing.Queue()
        self.trunk_driver = None

    def initialize(self):
        self.mlag_pairs = db_lib.get_mlag_physnets()
        self.trunk_driver = arista_trunk.AristaTrunkDriver.create()

    def get_workers(self):
        return [arista_sync.AristaSyncWorker(self.provision_queue)]

    def create_network(self, network, segments):
        """Enqueue network create"""
        tenant_id = network['project_id']
        action = a_const.CREATE if tenant_id else a_const.FULL_SYNC
        n_res = MechResource(network['id'], a_const.NETWORK_RESOURCE, action)
        n_res.related_resources.append((a_const.TENANT_RESOURCE, tenant_id))
        for segment in segments:
            n_res.related_resources.append(
                (a_const.SEGMENT_RESOURCE, segment['id']))
        self.provision_queue.put(n_res)

    def delete_network(self, network, segments):
        """Enqueue network delete"""
        tenant_id = network['project_id']
        action = a_const.DELETE if tenant_id else a_const.FULL_SYNC
        n_res = MechResource(network['id'], a_const.NETWORK_RESOURCE, action)

        # Delete tenant if this was the last tenant resource
        if not db_lib.tenant_provisioned(tenant_id):
            n_res.related_resources.append(
                (a_const.TENANT_RESOURCE, tenant_id))

        for segment in segments:
            n_res.related_resources.append(
                (a_const.SEGMENT_RESOURCE, segment['id']))
        self.provision_queue.put(n_res)

    def delete_segment(self, segment):
        """Enqueue segment delete"""
        s_res = MechResource(segment['id'], a_const.SEGMENT_RESOURCE,
                             a_const.DELETE)
        self.provision_queue.put(s_res)

    def get_instance_type(self, port):
        """Determine the port type based on device owner and vnic type"""
        if port[portbindings.VNIC_TYPE] == portbindings.VNIC_BAREMETAL:
            return a_const.BAREMETAL_RESOURCE
        owner_to_type = {
            n_const.DEVICE_OWNER_DHCP: a_const.DHCP_RESOURCE,
            n_const.DEVICE_OWNER_DVR_INTERFACE: a_const.ROUTER_RESOURCE,
            n_const.DEVICE_OWNER_ROUTER_INTF: a_const.ROUTER_RESOURCE,
            n_const.DEVICE_OWNER_ROUTER_HA_INTF: a_const.ROUTER_RESOURCE,
            trunk_consts.TRUNK_SUBPORT_OWNER: a_const.VM_RESOURCE}
        if port['device_owner'] in owner_to_type.keys():
            return owner_to_type[port['device_owner']]
        elif port['device_owner'].startswith(
                n_const.DEVICE_OWNER_COMPUTE_PREFIX):
            return a_const.VM_RESOURCE
        return None

    def _get_binding_keys(self, port, host):
        """Get binding keys from the port binding"""
        binding_keys = list()
        switch_binding = port[portbindings.PROFILE].get(
            'local_link_information', None)
        if switch_binding:
            for binding in switch_binding:
                switch_id = binding.get('switch_id')
                port_id = binding.get('port_id')
                binding_keys.append((port['id'], (switch_id, port_id)))
        else:
            binding_keys.append((port['id'], host))
        return binding_keys

    def create_port_binding(self, port, host):
        """Enqueue port binding create"""
        tenant_id = port['project_id']
        instance_type = self.get_instance_type(port)
        if not instance_type:
            return
        port_type = instance_type + a_const.PORT_SUFFIX
        action = a_const.CREATE if tenant_id else a_const.FULL_SYNC
        related_resources = list()
        related_resources.append((a_const.TENANT_RESOURCE, tenant_id))
        related_resources.append((instance_type, port['device_id']))
        related_resources.append((port_type, port['id']))
        for pb_key in self._get_binding_keys(port, host):
            pb_res = MechResource(pb_key, a_const.PORT_BINDING_RESOURCE,
                                  action, related_resources=related_resources)
            self.provision_queue.put(pb_res)

    def delete_port_binding(self, port, host):
        """Enqueue port binding delete"""
        tenant_id = port['project_id']
        instance_type = self.get_instance_type(port)
        if not instance_type:
            return
        port_type = instance_type + a_const.PORT_SUFFIX
        action = a_const.DELETE if tenant_id else a_const.FULL_SYNC
        related_resources = list()

        # Delete tenant if this was the last tenant resource
        if not db_lib.tenant_provisioned(tenant_id):
            related_resources.append((a_const.TENANT_RESOURCE, tenant_id))

        # Delete instance if this was the last instance port
        if not db_lib.instance_provisioned(port['device_id']):
            related_resources.append((instance_type, port['device_id']))

        # Delete port if this was the last port binding
        if not db_lib.port_provisioned(port['id']):
            related_resources.append((port_type, port['id']))

        for pb_key in self._get_binding_keys(port, host):
            pb_res = MechResource(pb_key, a_const.PORT_BINDING_RESOURCE,
                                  action, related_resources=related_resources)
            self.provision_queue.put(pb_res)

    def create_network_postcommit(self, context):
        """Provision the network on CVX"""
        network = context.current

        log_context("create_network_postcommit: network", network)

        segments = context.network_segments
        self.create_network(network, segments)

    def update_network_postcommit(self, context):
        """Send network updates to CVX:

        - Update the network name
        - Add new segments
        """
        network = context.current
        orig_network = context.original

        log_context("update_network_postcommit: network", network)
        log_context("update_network_postcommit: orig", orig_network)

        segments = context.network_segments

        # New segments may have been added
        self.create_network(network, segments)

    def delete_network_postcommit(self, context):
        """Delete the network from CVX"""
        network = context.current

        log_context("delete_network_postcommit: network", network)

        segments = context.network_segments
        self.delete_network(network, segments)

    def update_port_postcommit(self, context):
        """Send port updates to CVX

        This method is also responsible for the initial creation of ports
        as we wait until after a port is bound to send the port data to CVX
        """
        port = context.current
        orig_port = context.original
        network = context.network.current

        log_context("update_port_postcommit: port", port)
        log_context("update_port_postcommit: orig", orig_port)

        # Device id can change without a port going DOWN, but the new device
        # id may not be supported
        if orig_port and port['device_id'] != orig_port['device_id']:
            self.delete_port_binding(orig_port, context.original_host)

        if context.status in [n_const.PORT_STATUS_ACTIVE,
                              n_const.PORT_STATUS_BUILD]:
            if context.binding_levels:
                segments = [
                    level['bound_segment'] for level in context.binding_levels]
                self.create_network(network, segments)
            self.create_port_binding(port, context.host)
        else:
            if (context.original_host and
                    context.status != context.original_status):
                self.delete_port_binding(orig_port, context.original_host)
                self._try_to_release_dynamic_segment(context, migration=True)

    def delete_port_postcommit(self, context):
        """Delete the port from CVX"""
        port = context.current

        log_context("delete_port_postcommit: port", port)

        self.delete_port_binding(port, context.host)
        self._try_to_release_dynamic_segment(context)

    def _bind_baremetal_port(self, context, segment):
        """Bind the baremetal port to the segment"""
        port = context.current
        vif_details = {
            portbindings.VIF_DETAILS_VLAN: str(
                segment[driver_api.SEGMENTATION_ID])
        }
        context.set_binding(segment[driver_api.ID],
                            portbindings.VIF_TYPE_OTHER,
                            vif_details,
                            n_const.ACTIVE)
        LOG.debug("AristaDriver: bound port info- port ID %(id)s "
                  "on network %(network)s",
                  {'id': port['id'],
                   'network': context.network.current['id']})
        if port.get('trunk_details'):
            self.trunk_driver.bind_port(port)
        return True

    def _get_physnet(self, context):
        """Find the appropriate physnet for the host

        - Baremetal ports' physnet is determined by looking at the
          local_link_information contained in the binding profile
        - Other ports' physnet is determined by looking for the host in the
          topology
        """
        port = context.current
        physnet = None
        if (port.get(portbindings.VNIC_TYPE) == portbindings.VNIC_BAREMETAL):
            physnet = self.eapi.get_baremetal_physnet(context)
        else:
            physnet = self.eapi.get_host_physnet(context)
        # If the switch is part of an mlag pair, the physnet is called
        # peer1_peer2
        physnet = self.mlag_pairs.get(physnet, physnet)
        return physnet

    def _bind_fabric(self, context, segment):
        """Allocate dynamic segments for the port

        Segment physnets are based on the switch to which the host is
        connected.
        """
        port_id = context.current['id']
        physnet = self._get_physnet(context)
        if not physnet:
            LOG.debug("bind_port for port %(port)s: no physical_network "
                      "found", {'port': port_id})
            return False

        with lockutils.lock(physnet, external=True):
            context.allocate_dynamic_segment(
                {'network_id': context.network.current['id'],
                 'network_type': n_const.TYPE_VLAN,
                 'physical_network': physnet})
        next_segment = segments_db.get_dynamic_segment(
            context._plugin_context, context.network.current['id'],
            physical_network=physnet)
        LOG.debug("bind_port for port %(port)s: "
                  "current_segment=%(current_seg)s, "
                  "next_segment=%(next_seg)s",
                  {'port': port_id, 'current_seg': segment,
                   'next_seg': next_segment})
        context.continue_binding(segment['id'], [next_segment])
        return True

    def bind_port(self, context):
        """Bind port to a network segment.

        Provisioning request to Arista Hardware to plug a host
        into appropriate network is done when the port is created
        this simply tells the ML2 Plugin that we are binding the port
        """
        port = context.current

        log_context("bind_port: port", port)

        for segment in context.segments_to_bind:
            physnet = segment.get(driver_api.PHYSICAL_NETWORK)
            segment_type = segment[driver_api.NETWORK_TYPE]
            if not physnet:
                if (segment_type == n_const.TYPE_VXLAN and self.manage_fabric):
                    if self._bind_fabric(context, segment):
                        continue
            elif (port.get(portbindings.VNIC_TYPE)
                    == portbindings.VNIC_BAREMETAL):
                if (not self.managed_physnets or
                        physnet in self.managed_physnets):
                    if self._bind_baremetal_port(context, segment):
                        continue
            LOG.debug("Arista mech driver unable to bind port %(port)s to "
                      "%(seg_type)s segment on physical_network %(physnet)s",
                      {'port': port.get('id'), 'seg_type': segment_type,
                       'physnet': physnet})

    def _try_to_release_dynamic_segment(self, context, migration=False):
        """Release dynamic segment if necessary

        If this port was the last port using a segment and the segment was
        allocated by this driver, it should be released
        """
        if migration:
            binding_levels = context.original_binding_levels
        else:
            binding_levels = context.binding_levels
        LOG.debug("_try_to_release_dynamic_segment: "
                  "binding_levels=%(bl)s", {'bl': binding_levels})
        if not binding_levels:
            return

        for prior_level, binding in enumerate(binding_levels[1:]):
            allocating_driver = binding_levels[prior_level].get(
                driver_api.BOUND_DRIVER)
            if allocating_driver != a_const.MECHANISM_DRV_NAME:
                continue
            bound_segment = binding.get(driver_api.BOUND_SEGMENT, {})
            segment_id = bound_segment.get('id')
            if not db_lib.segment_is_dynamic(segment_id):
                continue
            if not db_lib.segment_bound(segment_id):
                context.release_dynamic_segment(segment_id)
                self.delete_segment(bound_segment)
                LOG.debug("Released dynamic segment %(seg)s allocated "
                          "by %(drv)s", {'seg': segment_id,
                                         'drv': allocating_driver})
