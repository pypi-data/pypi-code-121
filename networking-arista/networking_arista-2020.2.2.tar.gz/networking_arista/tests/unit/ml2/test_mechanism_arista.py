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

import mock

from neutron.tests.common import helpers
from neutron_lib import constants as n_const
from oslo_config import cfg

from networking_arista.tests.unit.ml2 import ml2_test_base

from neutron_lib.api.definitions import portbindings


class BasicMechDriverTestCase(ml2_test_base.MechTestBase):

    def test_create_network(self):
        # Test create regular network
        tenant_id = 'tid'
        reg_net_dict = {'network': {'name': 'net1',
                                    'tenant_id': tenant_id,
                                    'admin_state_up': True,
                                    'shared': False,
                                    'provider:physical_network': self.physnet,
                                    'provider:network_type': 'vlan'}}
        reg_network, reg_n_ctx = self.create_network(reg_net_dict)
        self.assertTenantCreated(tenant_id)
        self.assertNetworkCreated(reg_network['id'])
        for segment in reg_n_ctx.network_segments:
            self.assertSegmentCreated(segment['id'])

        # Test create shared network
        shrd_net_dict = {'network': {'name': 'shared_net',
                                     'tenant_id': tenant_id,
                                     'admin_state_up': True,
                                     'shared': True,
                                     'provider:physical_network': self.physnet,
                                     'provider:network_type': 'vlan'}}
        shared_network, shared_n_ctx = self.create_network(shrd_net_dict)
        self.assertTenantCreated(tenant_id)
        self.assertNetworkCreated(shared_network['id'])
        for segment in shared_n_ctx.network_segments:
            self.assertSegmentCreated(segment['id'])

        # Test delete regular network
        self.delete_network(reg_network['id'])
        self.assertTenantCreated(tenant_id)
        self.assertNetworkDeleted(reg_network['id'])
        for segment in reg_n_ctx.network_segments:
            self.assertSegmentDeleted(segment['id'])

        # Test delete shared network
        self.delete_network(shared_network['id'])
        self.assertTenantDeleted(tenant_id)
        self.assertNetworkDeleted(shared_network['id'])
        for segment in shared_n_ctx.network_segments:
            self.assertSegmentDeleted(segment['id'])

    def test_basic_dhcp_port(self):
        network_tenant = 'net-ten'
        net_dict = {'network': {'name': 'net',
                                'tenant_id': network_tenant,
                                'admin_state_up': True,
                                'shared': False,
                                'provider:physical_network': self.physnet,
                                'provider:network_type': 'vlan'}}
        network, _ = self.create_network(net_dict)

        # Create DHCP port
        device_id = 'dhcp-1'
        port_tenant = 'port-ten'
        port_host = self.host1
        port_dict = {'name': 'port1',
                     'tenant_id': port_tenant,
                     'network_id': network['id'],
                     'admin_state_up': True,
                     'fixed_ips': [],
                     'device_id': device_id,
                     'device_owner': n_const.DEVICE_OWNER_DHCP,
                     'binding:host_id': port_host}
        port, _ = self.create_port(port_dict)
        self.assertTenantCreated(port_tenant)
        self.assertDhcpCreated(device_id)
        self.assertDhcpPortCreated(port['id'])
        self.assertPortBindingCreated((port['id'], port_host))

        # Delete DHCP port
        self.delete_port(port['id'])
        self.assertTenantDeleted(port_tenant)
        self.assertDhcpDeleted(device_id)
        self.assertDhcpPortDeleted(port['id'])
        self.assertPortBindingDeleted((port['id'], port_host))

    def test_basic_dvr_port(self):
        network_tenant = 'net-ten'
        net_dict = {'network': {'name': 'net',
                                'tenant_id': network_tenant,
                                'admin_state_up': True,
                                'shared': False,
                                'provider:physical_network': self.physnet,
                                'provider:network_type': 'vlan'}}
        network, _ = self.create_network(net_dict)

        # Create DVR port
        device_id = 'router-1'
        port_tenant = 'port-ten'
        port_host_1 = self.host1
        port_dict = {'name': 'port1',
                     'tenant_id': port_tenant,
                     'network_id': network['id'],
                     'admin_state_up': True,
                     'fixed_ips': [],
                     'device_id': device_id,
                     'device_owner': n_const.DEVICE_OWNER_DVR_INTERFACE}
        port, _ = self.create_port(port_dict)
        self.bind_dvr_to_host(port, port_host_1)
        self.assertTenantCreated(port_tenant)
        self.assertRouterCreated(device_id)
        self.assertRouterPortCreated(port['id'])
        self.assertPortBindingCreated((port['id'], port_host_1))

        # Bring up a second DVR host
        port_host_2 = self.host2
        port, port_ctx = self.bind_dvr_to_host(port, port_host_2)
        self.assertPortBindingCreated((port['id'], port_host_2))

        # Delete the port
        self.delete_port(port['id'])
        self.assertTenantDeleted(port_tenant)
        self.assertRouterDeleted(device_id)
        self.assertRouterPortDeleted(port['id'])
        self.assertPortBindingDeleted((port['id'], port_host_1))
        self.assertPortBindingDeleted((port['id'], port_host_2))

    def test_dvr_port_host_bind_unbind(self):
        network_tenant = 'net-ten'
        net_dict = {'network': {'name': 'net',
                                'tenant_id': network_tenant,
                                'admin_state_up': True,
                                'shared': False,
                                'provider:physical_network': self.physnet,
                                'provider:network_type': 'vlan'}}
        network, _ = self.create_network(net_dict)

        # Create DVR port
        device_id = 'router-1'
        port_tenant = 'port-ten'
        port_host_1 = self.host1
        port_dict = {'name': 'port1',
                     'tenant_id': port_tenant,
                     'network_id': network['id'],
                     'admin_state_up': True,
                     'fixed_ips': [],
                     'device_id': device_id,
                     'device_owner': n_const.DEVICE_OWNER_DVR_INTERFACE}
        port, _ = self.create_port(port_dict)
        port, port_ctx = self.bind_dvr_to_host(port, port_host_1)
        self.assertTenantCreated(port_tenant)
        self.assertRouterCreated(device_id)
        self.assertRouterPortCreated(port['id'])
        self.assertPortBindingCreated((port['id'], port_host_1))

        # Bring up a second DVR host
        port_host_2 = self.host2
        port, port_ctx = self.bind_dvr_to_host(port, port_host_2)
        self.assertPortBindingCreated((port['id'], port_host_2))

        # Removed the second host
        self.unbind_dvr_from_host(port, port_host_2)
        self.assertPortBindingDeleted((port['id'], port_host_2))
        self.assertTenantCreated(port_tenant)
        self.assertRouterCreated(device_id)
        self.assertRouterPortCreated(port['id'])
        self.assertPortBindingCreated((port['id'], port_host_1))

        # Delete the port
        self.delete_port(port['id'])
        self.assertTenantDeleted(port_tenant)
        self.assertRouterDeleted(device_id)
        self.assertRouterPortDeleted(port['id'])
        self.assertPortBindingDeleted((port['id'], port_host_1))

    def test_dvr_port_race(self):
        network_tenant = 'net-ten'
        net_dict = {'network': {'name': 'net',
                                'tenant_id': network_tenant,
                                'admin_state_up': True,
                                'shared': False,
                                'provider:physical_network': self.physnet,
                                'provider:network_type': 'vlan'}}
        network, net_ctx = self.create_network(net_dict)

        # Create DVR port
        device_id = 'router-1'
        port_tenant = 'port-ten'
        port_host_1 = self.host1
        port_dict = {'name': 'port1',
                     'tenant_id': port_tenant,
                     'network_id': network['id'],
                     'admin_state_up': True,
                     'fixed_ips': [],
                     'device_id': device_id,
                     'device_owner': n_const.DEVICE_OWNER_DVR_INTERFACE}
        port, _ = self.create_port(port_dict)
        port, port_ctx = self.bind_dvr_to_host(port, port_host_1)
        self.assertTenantCreated(port_tenant)
        self.assertRouterCreated(device_id)
        self.assertRouterPortCreated(port['id'])
        self.assertPortBindingCreated((port['id'], port_host_1))

        # Bring up a second DVR host, but don't notify the mech_plugin
        port_host_2 = self.host2
        port, port_ctx = self.bind_dvr_to_host(
            port, port_host_2, notify_ml2=False,
            seg_id=net_ctx.network_segments[0]['id'])
        self.assertPortBindingCreated((port['id'], port_host_2))

        # Removed the second host
        self.unbind_dvr_from_host(port, port_host_2)
        self.assertPortBindingDeleted((port['id'], port_host_2))
        self.assertTenantCreated(port_tenant)
        self.assertRouterCreated(device_id)
        self.assertRouterPortCreated(port['id'])
        self.assertPortBindingCreated((port['id'], port_host_1))

        # Delete the port
        self.delete_port(port['id'])
        self.assertTenantDeleted(port_tenant)
        self.assertRouterDeleted(device_id)
        self.assertRouterPortDeleted(port['id'])
        self.assertPortBindingDeleted((port['id'], port_host_1))

    def test_basic_vm_port(self):
        network_tenant = 'net-ten'
        net_dict = {'network': {'name': 'net',
                                'tenant_id': network_tenant,
                                'admin_state_up': True,
                                'shared': False,
                                'provider:physical_network': self.physnet,
                                'provider:network_type': 'vlan'}}
        network, _ = self.create_network(net_dict)

        # Create VM port
        device_id = 'vm-1'
        port_tenant = 'port-ten'
        port_host = self.host1
        port_dict = {'name': 'port1',
                     'tenant_id': port_tenant,
                     'network_id': network['id'],
                     'admin_state_up': True,
                     'fixed_ips': [],
                     'device_id': device_id,
                     'device_owner': 'compute:',
                     'binding:host_id': port_host}
        port, _ = self.create_port(port_dict)
        self.assertTenantCreated(port_tenant)
        self.assertVmCreated(device_id)
        self.assertVmPortCreated(port['id'])
        self.assertPortBindingCreated((port['id'], port_host))

        # Delete VM port
        self.delete_port(port['id'])
        self.assertTenantDeleted(port_tenant)
        self.assertVmDeleted(device_id)
        self.assertVmPortDeleted(port['id'])
        self.assertPortBindingDeleted((port['id'], port_host))

    def test_basic_baremetal_port(self):
        network_tenant = 'net-ten'
        net_dict = {'network': {'name': 'net',
                                'tenant_id': network_tenant,
                                'admin_state_up': True,
                                'shared': False,
                                'provider:physical_network': self.physnet,
                                'provider:network_type': 'vlan'}}
        network, _ = self.create_network(net_dict)

        # Create baremetal port
        device_id = 'baremetal-1'
        port_tenant = 'port-ten'
        port_host = 'bm-host'
        switch_id = '00:11:22:33:44:55'
        switch_port = 'Ethernet1/1'
        port_dict = {'name': 'port1',
                     'tenant_id': port_tenant,
                     'network_id': network['id'],
                     'admin_state_up': True,
                     'fixed_ips': [],
                     'device_id': device_id,
                     'device_owner': n_const.DEVICE_OWNER_BAREMETAL_PREFIX,
                     'binding:host_id': port_host,
                     'binding:profile': {'local_link_information': [
                         {'switch_id': switch_id,
                          'port_id': switch_port}]},
                     'binding:vnic_type': 'baremetal'}
        port, _ = self.create_port(port_dict)
        self.assertTenantCreated(port_tenant)
        self.assertBaremetalCreated(device_id)
        self.assertBaremetalPortCreated(port['id'])
        self.assertPortBindingCreated((port['id'], (switch_id, switch_port)))

        # Delete baremetal port
        self.delete_port(port['id'])
        self.assertTenantDeleted(port_tenant)
        self.assertBaremetalDeleted(device_id)
        self.assertBaremetalPortDeleted(port['id'])
        self.assertPortBindingDeleted((port['id'], (switch_id, switch_port)))

    def test_basic_baremetal_mlag(self):
        network_tenant = 'net-ten'
        net_dict = {'network': {'name': 'net',
                                'tenant_id': network_tenant,
                                'admin_state_up': True,
                                'shared': False,
                                'provider:physical_network': self.physnet,
                                'provider:network_type': 'vlan'}}
        network, _ = self.create_network(net_dict)

        # Create baremetal port
        device_id = 'baremetal-1'
        port_tenant = 'port-ten'
        port_host = 'bm-host'
        switch_1_id = '00:11:22:33:44:55'
        switch_1_port = 'Ethernet1/1'
        switch_2_id = '55:44:33:22:11:00'
        switch_2_port = 'Ethernet2'
        port_dict = {'name': 'port1',
                     'tenant_id': port_tenant,
                     'network_id': network['id'],
                     'admin_state_up': True,
                     'fixed_ips': [],
                     'device_id': device_id,
                     'device_owner': n_const.DEVICE_OWNER_BAREMETAL_PREFIX,
                     'binding:host_id': port_host,
                     'binding:profile': {'local_link_information': [
                         {'switch_id': switch_1_id,
                          'port_id': switch_1_port},
                         {'switch_id': switch_2_id,
                          'port_id': switch_2_port}]},
                     'binding:vnic_type': 'baremetal'}
        port, _ = self.create_port(port_dict)
        self.assertTenantCreated(port_tenant)
        self.assertBaremetalCreated(device_id)
        self.assertBaremetalPortCreated(port['id'])
        self.assertPortBindingCreated(
            (port['id'], (switch_1_id, switch_1_port)))
        self.assertPortBindingCreated(
            (port['id'], (switch_2_id, switch_2_port)))

        # Delete baremetal port
        self.delete_port(port['id'])
        self.assertTenantDeleted(port_tenant)
        self.assertBaremetalDeleted(device_id)
        self.assertBaremetalPortDeleted(port['id'])
        self.assertPortBindingDeleted(
            (port['id'], (switch_1_id, switch_2_port)))
        self.assertPortBindingDeleted(
            (port['id'], (switch_2_id, switch_2_port)))

    def test_host_migration(self):
        network_tenant = 'net-ten'
        net_dict = {'network': {'name': 'net',
                                'tenant_id': network_tenant,
                                'admin_state_up': True,
                                'shared': False,
                                'provider:physical_network': self.physnet,
                                'provider:network_type': 'vlan'}}
        network, _ = self.create_network(net_dict)

        # Create VM port
        device_id = 'vm-1'
        port_tenant = 'port-ten'
        port_host = self.host1
        port_dict = {'name': 'port1',
                     'tenant_id': port_tenant,
                     'network_id': network['id'],
                     'admin_state_up': True,
                     'fixed_ips': [],
                     'device_id': device_id,
                     'device_owner': 'compute:',
                     'binding:host_id': port_host}
        port, _ = self.create_port(port_dict)
        self.assertTenantCreated(port_tenant)
        self.assertVmCreated(device_id)
        self.assertVmPortCreated(port['id'])
        self.assertPortBindingCreated((port['id'], port_host))

        # Migrate the port
        new_port_host = self.host2
        port, _ = self.migrate_port(port['id'], new_port_host)
        self.assertTenantCreated(port_tenant)
        self.assertVmCreated(device_id)
        self.assertVmPortCreated(port['id'])
        self.assertPortBindingDeleted((port['id'], port_host))
        self.assertPortBindingCreated((port['id'], new_port_host))

        # Delete VM port
        self.delete_port(port['id'])
        self.assertTenantDeleted(port_tenant)
        self.assertVmDeleted(device_id)
        self.assertVmPortDeleted(port['id'])
        self.assertPortBindingDeleted((port['id'], new_port_host))

    def test_dhcp_migration(self):
        network_tenant = 'net-ten'
        net_dict = {'network': {'name': 'net',
                                'tenant_id': network_tenant,
                                'admin_state_up': True,
                                'shared': False,
                                'provider:physical_network': 'physnet1',
                                'provider:network_type': 'vlan'}}
        network, _ = self.create_network(net_dict)

        # Create DHCP port
        device_id = 'dhcp-1'
        port_tenant = 'port-ten'
        port_host = self.host1
        port_dict = {'name': 'port1',
                     'tenant_id': port_tenant,
                     'network_id': network['id'],
                     'admin_state_up': True,
                     'fixed_ips': [],
                     'device_id': device_id,
                     'device_owner': n_const.DEVICE_OWNER_DHCP,
                     'binding:host_id': port_host,
                     'binding:vnic_type': 'normal'}
        port, _ = self.create_port(port_dict)
        self.assertTenantCreated(port_tenant)
        self.assertDhcpCreated(device_id)
        self.assertDhcpPortCreated(port['id'])
        self.assertPortBindingCreated((port['id'], port_host))

        # Migrate the DHCP port to a new dhcp instance
        new_device_id = 'dhcp-2'
        self.migrate_dhcp_device(port['id'], new_device_id)
        self.assertTenantCreated(port_tenant)
        self.assertDhcpCreated(new_device_id)
        self.assertDhcpDeleted(device_id)
        self.assertDhcpPortCreated(port['id'])
        self.assertPortBindingCreated((port['id'], port_host))

        # Delete DHCP port
        self.delete_port(port['id'])
        self.assertTenantDeleted(port_tenant)
        self.assertDhcpDeleted(device_id)
        self.assertDhcpPortDeleted(port['id'])
        self.assertPortBindingDeleted((port['id'], port_host))

    def test_vm_trunk_port(self):
        network_tenant = 'net-ten'
        net_dict = {'network': {'name': 'net1',
                                'tenant_id': network_tenant,
                                'admin_state_up': True,
                                'shared': False,
                                'provider:physical_network': self.physnet,
                                'provider:network_type': 'vlan'}}
        network1, _ = self.create_network(net_dict)
        net_dict = {'network': {'name': 'net2',
                                'tenant_id': network_tenant,
                                'admin_state_up': True,
                                'shared': False,
                                'provider:physical_network': self.physnet,
                                'provider:network_type': 'vlan'}}
        network2, _ = self.create_network(net_dict)

        # Create trunk port with subport
        device_id = 'vm-1'
        port_tenant = 'port-ten'
        port_host = self.host1
        trunkport_dict = {'name': 'port1',
                          'tenant_id': port_tenant,
                          'network_id': network1['id'],
                          'admin_state_up': True,
                          'fixed_ips': [],
                          'device_id': '',
                          'device_owner': ''}
        trunkport, _ = self.create_port(trunkport_dict)
        subport_dict = {'name': 'port2',
                        'tenant_id': port_tenant,
                        'network_id': network2['id'],
                        'admin_state_up': True,
                        'fixed_ips': [],
                        'device_id': '',
                        'device_owner': ''}
        subport, _ = self.create_port(subport_dict)
        trunk_dict = {'trunk': {'port_id': trunkport['id'],
                                'tenant_id': port_tenant,
                                'sub_ports': [{'port_id': subport['id'],
                                               'segmentation_type': 'vlan',
                                               'segmentation_id': 123}]}}
        trunk = self.trunk_plugin.create_trunk(self.context, trunk_dict)
        self.bind_trunk_to_host(trunkport, device_id, port_host)
        self.assertTenantCreated(port_tenant)
        self.assertVmCreated(device_id)
        self.assertVmPortCreated(trunkport['id'])
        self.assertPortBindingCreated((trunkport['id'], port_host))
        self.assertVmPortCreated(subport['id'])
        self.assertPortBindingCreated((subport['id'], port_host))

        # Delete the trunk and subport
        self.unbind_port_from_host(trunkport['id'])
        self.trunk_plugin.delete_trunk(self.context, trunk['id'])
        self.delete_port(trunkport['id'])
        self.delete_port(subport['id'])
        self.assertTenantDeleted(port_tenant)
        self.assertVmDeleted(device_id)
        self.assertVmPortDeleted(trunkport['id'])
        self.assertPortBindingDeleted((trunkport['id'], port_host))
        self.assertVmPortDeleted(subport['id'])
        self.assertPortBindingDeleted((subport['id'], port_host))

    def test_trunk_add_remove_subport(self):
        network_tenant = 'net-ten'
        net_dict = {'network': {'name': 'net1',
                                'tenant_id': network_tenant,
                                'admin_state_up': True,
                                'shared': False,
                                'provider:physical_network': self.physnet,
                                'provider:network_type': 'vlan'}}
        network1, _ = self.create_network(net_dict)
        net_dict = {'network': {'name': 'net2',
                                'tenant_id': network_tenant,
                                'admin_state_up': True,
                                'shared': False,
                                'provider:physical_network': self.physnet,
                                'provider:network_type': 'vlan'}}
        network2, _ = self.create_network(net_dict)
        net_dict = {'network': {'name': 'net3',
                                'tenant_id': network_tenant,
                                'admin_state_up': True,
                                'shared': False,
                                'provider:physical_network': self.physnet,
                                'provider:network_type': 'vlan'}}
        network3, _ = self.create_network(net_dict)

        # Create trunk port with subport, add subport after initial binding
        device_id = 'vm-1'
        port_tenant = 'port-ten'
        port_host = self.host1
        trunkport_dict = {'name': 'port1',
                          'tenant_id': port_tenant,
                          'network_id': network1['id'],
                          'admin_state_up': True,
                          'fixed_ips': [],
                          'device_id': '',
                          'device_owner': ''}
        trunkport, _ = self.create_port(trunkport_dict)
        subport_dict = {'name': 'port2',
                        'tenant_id': port_tenant,
                        'network_id': network2['id'],
                        'admin_state_up': True,
                        'fixed_ips': [],
                        'device_id': '',
                        'device_owner': ''}
        subport, _ = self.create_port(subport_dict)
        trunk_dict = {'trunk': {'port_id': trunkport['id'],
                                'tenant_id': port_tenant,
                                'sub_ports': [{'port_id': subport['id'],
                                               'segmentation_type': 'vlan',
                                               'segmentation_id': 123}]}}
        subport_dict2 = {'name': 'port3',
                         'tenant_id': port_tenant,
                         'network_id': network3['id'],
                         'admin_state_up': True,
                         'fixed_ips': [],
                         'device_id': '',
                         'device_owner': ''}
        trunk = self.trunk_plugin.create_trunk(self.context, trunk_dict)
        self.bind_trunk_to_host(trunkport, device_id, port_host)
        subport2, _ = self.create_port(subport_dict2)
        self.trunk_plugin.add_subports(self.context, trunk['id'],
                                       {'sub_ports':
                                        [{'port_id': subport2['id'],
                                          'segmentation_type': 'vlan',
                                          'segmentation_id': 111}]})
        self.bind_subport_to_trunk(subport2, trunk)
        self.assertTenantCreated(port_tenant)
        self.assertVmCreated(device_id)
        self.assertVmPortCreated(trunkport['id'])
        self.assertPortBindingCreated((trunkport['id'], port_host))
        self.assertVmPortCreated(subport['id'])
        self.assertPortBindingCreated((subport['id'], port_host))
        self.assertVmPortCreated(subport2['id'])
        self.assertPortBindingCreated((subport2['id'], port_host))

        # Remove the trunk subport
        self.trunk_plugin.remove_subports(self.context, trunk['id'],
                                          {'sub_ports':
                                           [{'port_id': subport2['id']}]})
        self.unbind_port_from_host(subport2['id'])
        self.assertPortBindingDeleted((subport2['id'], port_host))

        # Delete the trunk and remaining subport
        self.unbind_port_from_host(trunkport['id'])
        self.trunk_plugin.delete_trunk(self.context, trunk['id'])
        self.delete_port(trunkport['id'])
        self.delete_port(subport['id'])
        self.delete_port(subport2['id'])
        self.assertTenantDeleted(port_tenant)
        self.assertVmDeleted(device_id)
        self.assertVmPortDeleted(trunkport['id'])
        self.assertPortBindingDeleted((trunkport['id'], port_host))
        self.assertVmPortDeleted(subport['id'])
        self.assertPortBindingDeleted((subport['id'], port_host))

    def test_baremetal_trunk_basic(self):
        network_tenant = 'net-ten'
        net_dict = {'network': {'name': 'net1',
                                'tenant_id': network_tenant,
                                'admin_state_up': True,
                                'shared': False,
                                'provider:physical_network': self.physnet,
                                'provider:network_type': 'vlan'}}
        network1, _ = self.create_network(net_dict)
        net_dict = {'network': {'name': 'net2',
                                'tenant_id': network_tenant,
                                'admin_state_up': True,
                                'shared': False,
                                'provider:physical_network': self.physnet,
                                'provider:network_type': 'vlan'}}
        network2, _ = self.create_network(net_dict)

        # Create baremetal port
        device_id = 'baremetal-1'
        port_tenant = 'port-ten'
        port_host = 'bm-host'
        switch_id = '00:11:22:33:44:55'
        switch_port = 'Ethernet1/1'
        trunkport_dict = {'name': 'port1',
                          'tenant_id': port_tenant,
                          'network_id': network1['id'],
                          'admin_state_up': True,
                          'fixed_ips': [],
                          'device_id': '',
                          'device_owner': ''}
        trunkport, _ = self.create_port(trunkport_dict)
        subport_dict = {'name': 'port2',
                        'tenant_id': port_tenant,
                        'network_id': network2['id'],
                        'admin_state_up': True,
                        'fixed_ips': [],
                        'device_id': '',
                        'device_owner': ''}
        subport, _ = self.create_port(subport_dict)
        trunk_dict = {'trunk': {'port_id': trunkport['id'],
                                'tenant_id': port_tenant,
                                'sub_ports': [{'port_id': subport['id'],
                                               'segmentation_type': 'inherit',
                                               'segmentation_id': 'inherit'}]}}
        self.trunk_plugin.create_trunk(self.context, trunk_dict)
        self.bind_trunk_to_baremetal(trunkport['id'], device_id, port_host,
                                     switch_id, switch_port)
        self.assertTenantCreated(port_tenant)
        self.assertBaremetalCreated(device_id)
        self.assertBaremetalPortCreated(trunkport['id'])
        self.assertPortBindingCreated(
            (trunkport['id'], (switch_id, switch_port)))
        self.assertBaremetalPortCreated(subport['id'])
        self.assertPortBindingCreated(
            (subport['id'], (switch_id, switch_port)))

        # Simulate baremetal shutdown
        self.unbind_trunk_from_baremetal(trunkport['id'])
        self.assertBaremetalDeleted(device_id)
        self.assertPortBindingDeleted(
            (trunkport['id'], (switch_id, switch_port)))
        self.assertPortBindingDeleted(
            (subport['id'], (switch_id, switch_port)))

    def test_baremetal_trunk_bind_unbind(self):
        network_tenant = 'net-ten'
        net_dict = {'network': {'name': 'net1',
                                'tenant_id': network_tenant,
                                'admin_state_up': True,
                                'shared': False,
                                'provider:physical_network': self.physnet,
                                'provider:network_type': 'vlan'}}
        network1, _ = self.create_network(net_dict)
        net_dict = {'network': {'name': 'net2',
                                'tenant_id': network_tenant,
                                'admin_state_up': True,
                                'shared': False,
                                'provider:physical_network': self.physnet,
                                'provider:network_type': 'vlan'}}
        network2, _ = self.create_network(net_dict)
        net_dict = {'network': {'name': 'net3',
                                'tenant_id': network_tenant,
                                'admin_state_up': True,
                                'shared': False,
                                'provider:physical_network': self.physnet,
                                'provider:network_type': 'vlan'}}
        network3, _ = self.create_network(net_dict)

        # Create baremetal port
        device_id = 'baremetal-1'
        port_tenant = 'port-ten'
        port_host = 'bm-host'
        switch_id = '00:11:22:33:44:55'
        switch_port = 'Ethernet1/1'
        trunkport_dict = {'name': 'port1',
                          'tenant_id': port_tenant,
                          'network_id': network1['id'],
                          'admin_state_up': True,
                          'fixed_ips': [],
                          'device_id': '',
                          'device_owner': ''}
        trunkport, _ = self.create_port(trunkport_dict)
        subport_dict = {'name': 'port2',
                        'tenant_id': port_tenant,
                        'network_id': network2['id'],
                        'admin_state_up': True,
                        'fixed_ips': [],
                        'device_id': '',
                        'device_owner': ''}
        subport, _ = self.create_port(subport_dict)
        trunk_dict = {'trunk': {'port_id': trunkport['id'],
                                'tenant_id': port_tenant,
                                'sub_ports': [{'port_id': subport['id'],
                                               'segmentation_type': 'inherit',
                                               'segmentation_id': 'inherit'}]}}
        trunk = self.trunk_plugin.create_trunk(self.context, trunk_dict)
        self.bind_trunk_to_baremetal(trunkport['id'], device_id, port_host,
                                     switch_id, switch_port)
        self.assertTenantCreated(port_tenant)
        self.assertBaremetalCreated(device_id)
        self.assertBaremetalPortCreated(trunkport['id'])
        self.assertPortBindingCreated(
            (trunkport['id'], (switch_id, switch_port)))
        self.assertBaremetalPortCreated(subport['id'])
        self.assertPortBindingCreated(
            (subport['id'], (switch_id, switch_port)))

        subport_dict2 = {'name': 'port3',
                         'tenant_id': port_tenant,
                         'network_id': network3['id'],
                         'admin_state_up': True,
                         'fixed_ips': [],
                         'device_id': '',
                         'device_owner': ''}
        subport2, _ = self.create_port(subport_dict2)
        self.trunk_plugin.add_subports(self.context, trunk['id'],
                                       {'sub_ports':
                                        [{'port_id': subport2['id'],
                                          'segmentation_type': 'inherit',
                                          'segmentation_id': 'inherit'}]})
        self.assertBaremetalPortCreated(subport2['id'])
        self.assertPortBindingCreated(
            (subport2['id'], (switch_id, switch_port)))

        self.trunk_plugin.remove_subports(self.context, trunk['id'],
                                          {'sub_ports':
                                           [{'port_id': subport2['id']}]})
        self.assertPortBindingDeleted(
            (subport2['id'], (switch_id, switch_port)))

        # Simulate baremetal shutdown
        self.unbind_trunk_from_baremetal(trunkport['id'])
        self.assertBaremetalDeleted(device_id)
        self.assertPortBindingDeleted(
            (trunkport['id'], (switch_id, switch_port)))
        self.assertPortBindingDeleted(
            (subport['id'], (switch_id, switch_port)))

    def test_baremetal_trunk_pre_bound(self):
        network_tenant = 'net-ten'
        net_dict = {'network': {'name': 'net1',
                                'tenant_id': network_tenant,
                                'admin_state_up': True,
                                'shared': False,
                                'provider:physical_network': self.physnet,
                                'provider:network_type': 'vlan'}}
        network1, _ = self.create_network(net_dict)
        net_dict = {'network': {'name': 'net2',
                                'tenant_id': network_tenant,
                                'admin_state_up': True,
                                'shared': False,
                                'provider:physical_network': self.physnet,
                                'provider:network_type': 'vlan'}}
        network2, _ = self.create_network(net_dict)

        # Create baremetal port
        device_id = 'baremetal-1'
        port_tenant = 'port-ten'
        port_host = 'bm-host'
        switch_id = '00:11:22:33:44:55'
        switch_port = 'Ethernet1/1'
        trunkport_dict = {'name': 'port1',
                          'tenant_id': port_tenant,
                          'network_id': network1['id'],
                          'admin_state_up': True,
                          'fixed_ips': [],
                          'device_id': '',
                          'device_owner': ''}
        trunkport, _ = self.create_port(trunkport_dict)
        subport_dict = {'name': 'port2',
                        'tenant_id': port_tenant,
                        'network_id': network2['id'],
                        'admin_state_up': True,
                        'fixed_ips': [],
                        'device_id': '',
                        'device_owner': ''}
        subport, _ = self.create_port(subport_dict)
        trunk_dict = {'trunk': {'port_id': trunkport['id'],
                                'tenant_id': port_tenant,
                                'sub_ports': [{'port_id': subport['id'],
                                               'segmentation_type': 'inherit',
                                               'segmentation_id': 'inherit'}]}}
        self.bind_trunk_to_baremetal(trunkport['id'], device_id, port_host,
                                     switch_id, switch_port)
        self.trunk_plugin.create_trunk(self.context, trunk_dict)
        self.assertTenantCreated(port_tenant)
        self.assertBaremetalCreated(device_id)
        self.assertBaremetalPortCreated(trunkport['id'])
        self.assertPortBindingCreated(
            (trunkport['id'], (switch_id, switch_port)))
        self.assertBaremetalPortCreated(subport['id'])
        self.assertPortBindingCreated(
            (subport['id'], (switch_id, switch_port)))

        # Simulate baremetal shutdown
        self.unbind_trunk_from_baremetal(trunkport['id'])
        self.assertBaremetalDeleted(device_id)
        self.assertPortBindingDeleted(
            (trunkport['id'], (switch_id, switch_port)))
        self.assertPortBindingDeleted(
            (subport['id'], (switch_id, switch_port)))

    def test_error_port(self):
        network_tenant = 'net-ten'
        net_dict = {'network': {'name': 'net',
                                'tenant_id': network_tenant,
                                'admin_state_up': True,
                                'shared': False,
                                'provider:physical_network': self.physnet,
                                'provider:network_type': 'vlan'}}
        network, _ = self.create_network(net_dict)

        # Create port
        device_id = 'vm-1'
        port_tenant = 'port-ten'
        port_host = self.host1
        port_dict = {'name': 'port1',
                     'tenant_id': port_tenant,
                     'network_id': network['id'],
                     'admin_state_up': True,
                     'fixed_ips': [],
                     'device_id': device_id,
                     'device_owner': 'compute:',
                     'binding:host_id': port_host}
        port, _ = self.create_port(port_dict)
        self.assertTenantCreated(port_tenant)
        self.assertVmCreated(device_id)
        self.assertVmPortCreated(port['id'])
        self.assertPortBindingCreated((port['id'], port_host))

        # Set port to ERROR state
        self.set_port_to_error_state(port)
        self.assertVmDeleted(device_id)
        self.assertVmPortDeleted(port['id'])
        self.assertPortBindingDeleted((port['id'], port_host))


class FQDNFalseTestCase(ml2_test_base.MechTestBase):

    def setUp(self):
        cfg.CONF.set_override('use_fqdn', False, "ml2_arista")
        super(FQDNFalseTestCase, self).setUp()
        self.fqdnHost = 'fqdnhost.full.domain.com'
        helpers.register_ovs_agent(
            host=self.fqdnHost, bridge_mappings={self.physnet: 'br-eth1'})

    def test_fqdn_false(self):
        network_tenant = 'net-ten'
        net_dict = {'network': {'name': 'net',
                                'tenant_id': network_tenant,
                                'admin_state_up': True,
                                'shared': False,
                                'provider:physical_network': self.physnet,
                                'provider:network_type': 'vlan'}}
        network, _ = self.create_network(net_dict)

        # Create VM port
        device_id = 'vm-1'
        port_tenant = 'port-ten'
        port_host = self.fqdnHost
        port_dict = {'name': 'port1',
                     'tenant_id': port_tenant,
                     'network_id': network['id'],
                     'admin_state_up': True,
                     'fixed_ips': [],
                     'device_id': device_id,
                     'device_owner': 'compute:',
                     'binding:host_id': port_host}
        port, _ = self.create_port(port_dict)
        self.assertTenantCreated(port_tenant)
        self.assertVmCreated(device_id)
        self.assertVmPortCreated(port['id'])
        self.assertPortBindingCreated((port['id'], 'fqdnhost'))

        # Delete VM port
        self.delete_port(port['id'])
        self.assertTenantDeleted(port_tenant)
        self.assertVmDeleted(device_id)
        self.assertVmPortDeleted(port['id'])
        self.assertPortBindingDeleted((port['id'], 'fqdnhost'))


class FQDNTrueTestCase(ml2_test_base.MechTestBase):

    def setUp(self):
        super(FQDNTrueTestCase, self).setUp()
        self.fqdnHost = 'fqdnhost.full.domain.com'
        helpers.register_ovs_agent(
            host=self.fqdnHost, bridge_mappings={self.physnet: 'br-eth1'})

    def test_fqdn_true(self):
        network_tenant = 'net-ten'
        net_dict = {'network': {'name': 'net',
                                'tenant_id': network_tenant,
                                'admin_state_up': True,
                                'shared': False,
                                'provider:physical_network': self.physnet,
                                'provider:network_type': 'vlan'}}
        network, _ = self.create_network(net_dict)

        # Create VM port
        device_id = 'vm-1'
        port_tenant = 'port-ten'
        port_host = self.fqdnHost
        port_dict = {'name': 'port1',
                     'tenant_id': port_tenant,
                     'network_id': network['id'],
                     'admin_state_up': True,
                     'fixed_ips': [],
                     'device_id': device_id,
                     'device_owner': 'compute:',
                     'binding:host_id': port_host}
        port, _ = self.create_port(port_dict)
        self.assertTenantCreated(port_tenant)
        self.assertVmCreated(device_id)
        self.assertVmPortCreated(port['id'])
        self.assertPortBindingCreated((port['id'], self.fqdnHost))

        # Delete VM port
        self.delete_port(port['id'])
        self.assertTenantDeleted(port_tenant)
        self.assertVmDeleted(device_id)
        self.assertVmPortDeleted(port['id'])
        self.assertPortBindingDeleted((port['id'], self.fqdnHost))


class BasicHpbMechDriverTestCase(ml2_test_base.MechTestBase):

    def setUp(self):
        cfg.CONF.set_override('manage_fabric', True, "ml2_arista")
        super(BasicHpbMechDriverTestCase, self).setUp()

    def test_basic_hpb_port(self):
        network_tenant = 'net-ten'
        net_dict = {'network': {'name': 'net',
                                'tenant_id': network_tenant,
                                'admin_state_up': True,
                                'shared': False,
                                'provider:physical_network': None,
                                'provider:network_type': 'vxlan'}}
        network, _ = self.create_network(net_dict)
        self.assertNetworkCreated(network['id'])

        # Create HPB port
        device_id = 'vm-1'
        port_tenant = 'port-ten'
        port_host = self.host1
        port_dict = {'name': 'port1',
                     'tenant_id': port_tenant,
                     'network_id': network['id'],
                     'admin_state_up': True,
                     'fixed_ips': [],
                     'device_id': device_id,
                     'device_owner': 'compute:',
                     'binding:host_id': port_host}
        with mock.patch.object(self.drv.eapi,
                               'get_host_physnet',
                               return_value=self.physnet):
            port, port_ctx = self.create_port(port_dict)
        self.assertTenantCreated(port_tenant)
        self.assertVmCreated(device_id)
        self.assertVmPortCreated(port['id'])
        self.assertPortBindingCreated((port['id'], port_host))

        # Check that the dynamic segment was created
        network_segments = [level['bound_segment']
                            for level in port_ctx.binding_levels]
        self.assertTrue(len(network_segments) == 2)
        for segment in network_segments:
            self.assertSegmentCreated(segment['id'])

        # Delete HPB port
        self.delete_port(port['id'])
        self.assertTenantDeleted(port_tenant)
        self.assertVmDeleted(device_id)
        self.assertVmPortDeleted(port['id'])
        self.assertPortBindingDeleted((port['id'], port_host))

    def test_hpb_dvr_port(self):
        network_tenant = 'net-ten'
        net_dict = {'network': {'name': 'net',
                                'tenant_id': network_tenant,
                                'admin_state_up': True,
                                'shared': False,
                                'provider:physical_network': None,
                                'provider:network_type': 'vxlan'}}
        network, _ = self.create_network(net_dict)

        # Create DVR port
        device_id = 'router-1'
        port_tenant = 'port-ten'
        port_host_1 = self.host1
        port_dict = {'name': 'port1',
                     'tenant_id': port_tenant,
                     'network_id': network['id'],
                     'admin_state_up': True,
                     'fixed_ips': [],
                     'device_id': device_id,
                     'device_owner': n_const.DEVICE_OWNER_DVR_INTERFACE}
        port, _ = self.create_port(port_dict)
        with mock.patch.object(self.drv.eapi,
                               'get_host_physnet',
                               return_value=self.physnet):
            port, port_ctx = self.bind_dvr_to_host(port, port_host_1)
        self.assertTenantCreated(port_tenant)
        self.assertRouterCreated(device_id)
        self.assertRouterPortCreated(port['id'])
        self.assertPortBindingCreated((port['id'], port_host_1))
        network_segments = [level['bound_segment']
                            for level in port_ctx.binding_levels]
        self.assertTrue(len(network_segments) == 2)
        for segment in network_segments:
            self.assertSegmentCreated(segment['id'])

        # Bring up a second DVR host
        port_host_2 = self.host3
        with mock.patch.object(self.drv.eapi,
                               'get_host_physnet',
                               return_value=self.physnet2):
            port, port_ctx = self.bind_dvr_to_host(port, port_host_2)
        self.assertPortBindingCreated((port['id'], port_host_2))
        network_segments = [level['bound_segment']
                            for level in port_ctx.binding_levels]
        self.assertTrue(len(network_segments) == 2)
        for segment in network_segments:
            self.assertSegmentCreated(segment['id'])

        # Delete the port
        self.delete_port(port['id'])
        self.assertTenantDeleted(port_tenant)
        self.assertRouterDeleted(device_id)
        self.assertRouterPortDeleted(port['id'])
        self.assertPortBindingDeleted((port['id'], port_host_1))
        self.assertPortBindingDeleted((port['id'], port_host_2))


class UnmanagedFabricUnmanagedPhysnetHpbTestCase(ml2_test_base.MechTestBase):

    _mechanism_drivers = ['arista_test_fabric', 'arista', 'openvswitch']

    def setUp(self):
        cfg.CONF.set_override('manage_fabric', False, "ml2_arista")
        cfg.CONF.set_override('managed_physnets', ['other_physnet'],
                              "ml2_arista")
        super(UnmanagedFabricUnmanagedPhysnetHpbTestCase, self).setUp()

    def test_unmanaged_fabric_unmanaged_hpb_port(self):
        network_tenant = 'net-ten'
        net_dict = {'network': {'name': 'net',
                                'tenant_id': network_tenant,
                                'admin_state_up': True,
                                'shared': False,
                                'provider:physical_network': None,
                                'provider:network_type': 'vxlan'}}
        network, _ = self.create_network(net_dict)
        self.assertNetworkCreated(network['id'])

        # Create HPB port
        device_id = 'vm-1'
        port_tenant = 'port-ten'
        port_host = self.host1
        port_dict = {'name': 'port1',
                     'tenant_id': port_tenant,
                     'network_id': network['id'],
                     'admin_state_up': True,
                     'fixed_ips': [],
                     'device_id': device_id,
                     'device_owner': 'compute:',
                     'binding:host_id': port_host}
        port, port_ctx = self.create_port(port_dict)
        self.assertTenantCreated(port_tenant)
        # Check that the dynamic segment was created
        network_segments = [level['bound_segment']
                            for level in port_ctx.binding_levels]
        self.assertTrue(len(network_segments) == 2)
        for segment in network_segments:
            self.assertSegmentCreated(segment['id'])

        # The VM/Port should not have been created
        self.assertVmDeleted(device_id)
        self.assertVmPortDeleted(port['id'])
        self.assertPortBindingDeleted((port['id'], port_host))

        # Delete HPB port
        self.delete_port(port['id'])
        self.assertTenantDeleted(port_tenant)
        self.assertVmDeleted(device_id)
        self.assertVmPortDeleted(port['id'])
        self.assertPortBindingDeleted((port['id'], port_host))


class ManagedFabricUnmanagedPhysnetHpbTestCase(ml2_test_base.MechTestBase):

    def setUp(self):
        cfg.CONF.set_override('manage_fabric', True, "ml2_arista")
        cfg.CONF.set_override('managed_physnets', ['other_physnet'],
                              "ml2_arista")
        super(ManagedFabricUnmanagedPhysnetHpbTestCase, self).setUp()

    def test_managed_fabric_unmanaged_hpb_port(self):
        network_tenant = 'net-ten'
        net_dict = {'network': {'name': 'net',
                                'tenant_id': network_tenant,
                                'admin_state_up': True,
                                'shared': False,
                                'provider:physical_network': None,
                                'provider:network_type': 'vxlan'}}
        network, _ = self.create_network(net_dict)
        self.assertNetworkCreated(network['id'])

        # Create HPB port
        device_id = 'vm-1'
        port_tenant = 'port-ten'
        port_host = self.host1
        port_dict = {'name': 'port1',
                     'tenant_id': port_tenant,
                     'network_id': network['id'],
                     'admin_state_up': True,
                     'fixed_ips': [],
                     'device_id': device_id,
                     'device_owner': 'compute:',
                     'binding:host_id': port_host}
        with mock.patch.object(self.drv.eapi,
                               'get_host_physnet',
                               return_value=self.physnet):
            port, port_ctx = self.create_port(port_dict)
        self.assertTenantCreated(port_tenant)
        # Check that the dynamic segment was created
        network_segments = [level['bound_segment']
                            for level in port_ctx.binding_levels]
        self.assertTrue(len(network_segments) == 2)
        for segment in network_segments:
            self.assertSegmentCreated(segment['id'])

        # The VM/Port should not have been created
        self.assertVmDeleted(device_id)
        self.assertVmPortDeleted(port['id'])
        self.assertPortBindingDeleted((port['id'], port_host))

        # Delete HPB port
        self.delete_port(port['id'])
        self.assertTenantDeleted(port_tenant)
        self.assertVmDeleted(device_id)
        self.assertVmPortDeleted(port['id'])
        self.assertPortBindingDeleted((port['id'], port_host))


class UnmanagedFabricManagedPhysnetHpbTestCase(ml2_test_base.MechTestBase):

    _mechanism_drivers = ['arista_test_fabric', 'arista', 'openvswitch']

    def setUp(self):
        self.physnet = 'physnet1'
        cfg.CONF.set_override('manage_fabric', False, "ml2_arista")
        cfg.CONF.set_override('managed_physnets', [self.physnet],
                              "ml2_arista")
        super(UnmanagedFabricManagedPhysnetHpbTestCase, self).setUp()

    def test_unmanaged_fabric_managed_hpb_port(self):
        network_tenant = 'net-ten'
        net_dict = {'network': {'name': 'net',
                                'tenant_id': network_tenant,
                                'admin_state_up': True,
                                'shared': False,
                                'provider:physical_network': None,
                                'provider:network_type': 'vxlan'}}
        network, _ = self.create_network(net_dict)
        self.assertNetworkCreated(network['id'])

        # Create HPB port
        device_id = 'vm-1'
        port_tenant = 'port-ten'
        port_host = self.host1
        port_dict = {'name': 'port1',
                     'tenant_id': port_tenant,
                     'network_id': network['id'],
                     'admin_state_up': True,
                     'fixed_ips': [],
                     'device_id': device_id,
                     'device_owner': 'compute:',
                     'binding:host_id': port_host}
        port, port_ctx = self.create_port(port_dict)
        self.assertTenantCreated(port_tenant)
        self.assertVmCreated(device_id)
        self.assertVmPortCreated(port['id'])
        self.assertPortBindingCreated((port['id'], port_host))

        # Check that the dynamic segment was created
        network_segments = [level['bound_segment']
                            for level in port_ctx.binding_levels]
        self.assertTrue(len(network_segments) == 2)
        for segment in network_segments:
            self.assertSegmentCreated(segment['id'])

        # Delete HPB port
        self.delete_port(port['id'])
        self.assertTenantDeleted(port_tenant)
        self.assertVmDeleted(device_id)
        self.assertVmPortDeleted(port['id'])
        self.assertPortBindingDeleted((port['id'], port_host))


class ManagedFabricManagedFabricHpbTestCase(ml2_test_base.MechTestBase):

    def setUp(self):
        self.physnet = 'physnet1'
        cfg.CONF.set_override('manage_fabric', True, "ml2_arista")
        cfg.CONF.set_override('managed_physnets', [self.physnet],
                              "ml2_arista")
        super(ManagedFabricManagedFabricHpbTestCase, self).setUp()

    def test_managed_fabric_managed_hpb_port(self):
        network_tenant = 'net-ten'
        net_dict = {'network': {'name': 'net',
                                'tenant_id': network_tenant,
                                'admin_state_up': True,
                                'shared': False,
                                'provider:physical_network': None,
                                'provider:network_type': 'vxlan'}}
        network, _ = self.create_network(net_dict)
        self.assertNetworkCreated(network['id'])

        # Create HPB port
        device_id = 'vm-1'
        port_tenant = 'port-ten'
        port_host = self.host1
        port_dict = {'name': 'port1',
                     'tenant_id': port_tenant,
                     'network_id': network['id'],
                     'admin_state_up': True,
                     'fixed_ips': [],
                     'device_id': device_id,
                     'device_owner': 'compute:',
                     'binding:host_id': port_host}
        with mock.patch.object(self.drv.eapi,
                               'get_host_physnet',
                               return_value=self.physnet):
            port, port_ctx = self.create_port(port_dict)
        self.assertTenantCreated(port_tenant)
        self.assertVmCreated(device_id)
        self.assertVmPortCreated(port['id'])
        self.assertPortBindingCreated((port['id'], port_host))

        # Check that the dynamic segment was created
        network_segments = [level['bound_segment']
                            for level in port_ctx.binding_levels]
        self.assertTrue(len(network_segments) == 2)
        for segment in network_segments:
            self.assertSegmentCreated(segment['id'])

        # Delete HPB port
        self.delete_port(port['id'])
        self.assertTenantDeleted(port_tenant)
        self.assertVmDeleted(device_id)
        self.assertVmPortDeleted(port['id'])
        self.assertPortBindingDeleted((port['id'], port_host))


class ManagedPhysnetNoHpbTestCase(ml2_test_base.MechTestBase):

    def setUp(self):
        self.physnet = 'physnet1'
        cfg.CONF.set_override('managed_physnets', [self.physnet],
                              "ml2_arista")
        super(ManagedPhysnetNoHpbTestCase, self).setUp()

    def test_managed_physnet_no_hpb(self):
        network_tenant = 'net-ten'
        net_dict = {'network':
                    {'name': 'net',
                     'tenant_id': network_tenant,
                     'admin_state_up': True,
                     'shared': False,
                     'provider:physical_network': self.physnet,
                     'provider:network_type': 'vlan'}}
        network, _ = self.create_network(net_dict)

        other_net_dict = {'network':
                          {'name': 'net',
                           'tenant_id': network_tenant,
                           'admin_state_up': True,
                           'shared': False,
                           'provider:physical_network': self.physnet2,
                           'provider:network_type': 'vlan'}}
        other_network, _ = self.create_network(other_net_dict)

        # Create VM port
        device_id_1 = 'vm-1'
        port_tenant = 'port-ten'
        port_host_1 = self.host1
        port_dict_1 = {'name': 'port1',
                       'tenant_id': port_tenant,
                       'network_id': network['id'],
                       'admin_state_up': True,
                       'fixed_ips': [],
                       'device_id': device_id_1,
                       'device_owner': 'compute:',
                       'binding:host_id': port_host_1}
        port_1, _ = self.create_port(port_dict_1)
        self.assertTenantCreated(port_tenant)
        self.assertVmCreated(device_id_1)
        self.assertVmPortCreated(port_1['id'])
        self.assertPortBindingCreated((port_1['id'], port_host_1))

        # Create VM port on unmanaged physnet
        device_id_2 = 'vm-2'
        port_host_2 = self.host3
        port_dict_2 = {'name': 'port2',
                       'tenant_id': port_tenant,
                       'network_id': other_network['id'],
                       'admin_state_up': True,
                       'fixed_ips': [],
                       'device_id': device_id_2,
                       'device_owner': 'compute:',
                       'binding:host_id': port_host_2}
        port_2, _ = self.create_port(port_dict_2)
        # The VM/Port should not have been created
        self.assertVmDeleted(device_id_2)
        self.assertVmPortDeleted(port_2['id'])
        self.assertPortBindingDeleted((port_2['id'], port_host_2))

        # Delete VM port
        self.delete_port(port_1['id'])
        self.assertVmDeleted(device_id_1)
        self.assertVmPortDeleted(port_1['id'])
        self.assertPortBindingDeleted((port_1['id'], port_host_1))

        # Delete other unmanaged VM port
        self.delete_port(port_2['id'])
        self.assertTenantDeleted(port_tenant)


class BasicL3HARouterTests(object):

    def test_create_delete_router(self):
        ha_router_ports = []
        router = self.create_router(ha=True)
        for l3_agent in self.l3_agents:
            port = self.update_routers_states(router['id'], l3_agent)
            ha_router_ports.append(port)
        ha_network_id = self.get_ha_network(router)
        ha_segments = self.get_network_segments(ha_network_id)
        self.assertTenantCreated(router['project_id'])
        self.assertL3HANetworkCreated(router, ha_network_id)
        self.assertRouterCreated(router['id'])
        self.assertL3HARouterCreated(router)
        for port in ha_router_ports:
            self.assertL3HAPortCreated(router, port['id'])
            self.assertPortBindingCreated((port['id'],
                                           port[portbindings.HOST_ID]))
        self.assertSegmentsCreated(ha_segments)

        # Delete the router
        self.delete_router(router['id'])
        self.assertRouterPortsDeleted([p['id'] for p in ha_router_ports])
        self.assertRouterDeleted(router['id'])
        self.assertSegmentsDeleted(ha_segments)
        self.assertNetworkDeleted(ha_network_id)
        self.assertTenantDeleted(router['project_id'])
        for port in ha_router_ports:
            self.assertPortBindingDeleted((port['id'],
                                           port[portbindings.HOST_ID]))


class BasicRouterTests(object):
    def test_create_delete_router(self):
        router = self.create_router()
        net_list = []
        port_list = []
        segment_list = []
        for net in self.net_dict:
            network, net_ctx = self.create_network(net)
            net_list.append((network, net_ctx))
        self.assertTenantCreated(router['project_id'])
        for net, net_ctx in net_list:
            interface_info = {'subnet_id': net_ctx.current['subnets'][0]}
            intf = self.add_router_interface(router, interface_info)
            self.sync_routers(router['id'], self.l3_agent1['host'])
            port = self.get_legacy_router_port(intf['port_id'])
            self.assertNotEqual(len(port), 0)
            port_list.append(port)
        self.assertLegacyRouterCreated(router, self.l3_agent1['host'])
        for network, _ in net_list:
            self.assertNetworkCreated(network['id'])
            segment_list.extend(self.get_network_segments(network['id']))
        self.assertEqual(len(segment_list), self.total_segments)
        self.assertSegmentsCreated(segment_list)
        for port in port_list:
            self.assertRouterPortCreated(port['id'])
            self.assertPortBindingCreated((port['id'],
                                           port[portbindings.HOST_ID]))

        # Delete the router interfaces and router
        # Remove one of router's interface
        network, net_ctx = net_list[0]
        interface_info = {'subnet_id': net_ctx.current['subnets'][0]}
        intf = self.remove_router_interface(router, interface_info)
        self.assertRouterCreated(router['id'])
        self.assertRouterPortDeleted(intf['port_id'])
        self.assertPortBindingDeleted((intf['port_id'],
                                       port[portbindings.HOST_ID]))

        # Remove second router interface
        network, net_ctx = net_list[1]
        interface_info = {'subnet_id': net_ctx.current['subnets'][0]}
        intf = self.remove_router_interface(router, interface_info)
        self.assertRouterDeleted(router['id'])
        self.assertRouterPortDeleted(intf['port_id'])
        self.assertPortBindingDeleted((intf['port_id'],
                                       port[portbindings.HOST_ID]))

        for network, _ in net_list:
            self.delete_network(network['id'])
            self.assertNetworkDeleted(network['id'])
        self.assertSegmentsDeleted(segment_list)


class BasicL3HARouterTestCases(ml2_test_base.L3HARouterTestFramework,
                               BasicL3HARouterTests):

    def setUp(self):
        cfg.CONF.set_override('tenant_network_types', 'vlan', 'ml2')
        super(BasicL3HARouterTestCases, self).setUp()
        cfg.CONF.set_override('max_l3_agents_per_router', 2)
        self.l3_agent1 = self._register_l3_agent(host=self.host1)
        self.l3_agent2 = self._register_l3_agent(host=self.host2)
        self.l3_agents = [self.l3_agent1, self.l3_agent2]


class BasicHpbL3HARouterTestCases(ml2_test_base.L3HARouterTestFramework,
                                  BasicL3HARouterTests):
    def setUp(self):
        cfg.CONF.set_override('manage_fabric', True, 'ml2_arista')
        cfg.CONF.set_override('tenant_network_types', 'vxlan', 'ml2')
        super(BasicHpbL3HARouterTestCases, self).setUp()
        cfg.CONF.set_override('l3_ha', True)
        cfg.CONF.set_override('max_l3_agents_per_router', 3)
        self.l3_agent1 = self._register_l3_agent(host=self.host1)
        self.l3_agent2 = self._register_l3_agent(host=self.host2)
        self.l3_agent3 = self._register_l3_agent(host=self.host3)
        self.l3_agents = [self.l3_agent1, self.l3_agent2, self.l3_agent3]

        def get_host_physnet(context):
            if context.host == 'host3':
                return self.physnet2
            if context.host == 'host1':
                return self.physnet
            if context.host == 'host2':
                return self.physnet

        ghp = mock.patch.object(self.drv.eapi, 'get_host_physnet').start()
        ghp.side_effect = get_host_physnet


class BasicRouterTestCases(ml2_test_base.L3HARouterTestFramework,
                           BasicRouterTests):

    def setUp(self):
        cfg.CONF.set_override('tenant_network_types', 'vlan', 'ml2')
        super(BasicRouterTestCases, self).setUp()
        self.l3_agent1 = self._register_l3_agent(host=self.host1)
        self.net_dict = [
            {'network': {'name': 'net-%d' % r,
                         'tenant_id': self._tenant_id,
                         'admin_state_up': True,
                         'shared': False,
                         'provider:physical_network': self.physnet,
                         'provider:network_type': 'vlan'}}
            for r in range(1, 3)]
        self.total_segments = 2
        self.l3_agents = [self.l3_agent1]


class BasicHpbRouterTestCases(ml2_test_base.L3HARouterTestFramework,
                              BasicRouterTests):

    def setUp(self):
        cfg.CONF.set_override('manage_fabric', True, 'ml2_arista')
        cfg.CONF.set_override('tenant_network_types', 'vxlan', 'ml2')
        super(BasicHpbRouterTestCases, self).setUp()
        self.l3_agent1 = self._register_l3_agent(host=self.host1)

        def get_host_physnet(context):
            return self.physnet
        ghp = mock.patch.object(self.drv.eapi, 'get_host_physnet').start()
        ghp.side_effect = get_host_physnet
        self.net_dict = [{'network': {'name': 'hpb_net-%d' % r,
                                      'tenant_id': self._tenant_id,
                                      'admin_state_up': True,
                                      'shared': False}}
                         for r in range(1, 3)]
        self.total_segments = 4
        self.l3_agents = [self.l3_agent1]
