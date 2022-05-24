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
from oslo_config import cfg

from neutron.tests import base
from neutron.tests.unit import testlib_api
from neutron_lib.api.definitions import portbindings

from networking_arista.common import exceptions as arista_exc
from networking_arista.ml2.rpc import arista_eapi
from networking_arista.tests.unit import utils


def setup_valid_config():
    utils.setup_arista_wrapper_config(cfg)


class AristaRPCWrapperInvalidConfigTestCase(base.BaseTestCase):
    """Negative test cases to test the Arista Driver configuration."""

    def setUp(self):
        super(AristaRPCWrapperInvalidConfigTestCase, self).setUp()
        self.setup_invalid_config()  # Invalid config, required options not set

    def setup_invalid_config(self):
        utils.setup_arista_wrapper_config(cfg, host='', user='')

    def test_raises_exception_on_wrong_configuration(self):
        self.assertRaises(arista_exc.AristaConfigError,
                          arista_eapi.AristaRPCWrapperEapi)


class NegativeRPCWrapperTestCase(testlib_api.SqlTestCase):
    """Negative test cases to test the RPC between Arista Driver and EOS."""

    def setUp(self):
        super(NegativeRPCWrapperTestCase, self).setUp()
        setup_valid_config()

    def test_exception_is_raised_on_json_server_error(self):
        drv = arista_eapi.AristaRPCWrapperEapi()

        drv.api_request = mock.MagicMock(
            side_effect=Exception('server error')
        )
        with mock.patch.object(arista_eapi.LOG, 'error') as log_err:
            self.assertRaises(arista_exc.AristaRpcError,
                              drv._run_openstack_cmds, [])
            log_err.assert_called_once_with(mock.ANY)


class GetPhysnetTestCase(base.BaseTestCase):
    """Test cases to validate parsing of topology output to find physnets"""

    def setUp(self):
        super(GetPhysnetTestCase, self).setUp()
        setup_valid_config()

    def _test_get_host_physnet(self, nova_fqdn, topo_host_fqdn,
                               topo_switch_fqdn, bridge_map_fqdn, use_fqdn,
                               use_fqdn_physnet):
        cfg.CONF.set_override('use_fqdn', use_fqdn, "ml2_arista")
        cfg.CONF.set_override('use_fqdn_physnet', use_fqdn_physnet,
                              "ml2_arista")
        context = mock.MagicMock()
        nova_host1 = 'host1.full.name' if nova_fqdn else 'host1'
        nova_host2 = 'host2.full.name' if nova_fqdn else 'host2'
        topo_host1 = 'host1.full.name' if topo_host_fqdn else 'host1'
        topo_host2 = 'host2.full.name' if topo_host_fqdn else 'host2'
        topo_switch1 = 'switch1.full.name' if topo_switch_fqdn else 'switch1'
        topo_switch2 = 'switch2.full.name' if topo_switch_fqdn else 'switch2'
        bridge_map_switch1 = ('switch1.full.name' if bridge_map_fqdn
                              else 'switch1')
        bridge_map_switch2 = ('switch2.full.name' if bridge_map_fqdn
                              else 'switch2')
        context.host = nova_host1
        topology = [{'neighbors':
                     {'%s-et1' % topo_host1:
                      {'fromPort':
                       {'name': 'et1',
                        'hostname': topo_host1,
                        'hostid': '00:00:00:00:00:00'},
                       'toPort': [
                           {'name': 'Ethernet1',
                            'hostname': topo_switch1,
                            'hostid': '00:00:00:00:00:01'}]},
                      '%s-et1' % topo_host2:
                      {'fromPort':
                       {'name': 'et1',
                        'hostname': topo_host2,
                        'hostid': '00:00:00:00:00:02'},
                       'toPort': [
                           {'name': 'Ethernet1',
                            'hostname': topo_switch2,
                            'hostid': '00:00:00:00:00:03'}]}}}]
        drv = arista_eapi.AristaRPCWrapperEapi()
        drv._run_eos_cmds = mock.MagicMock()
        drv._run_eos_cmds.return_value = topology
        self.assertEqual(drv.get_host_physnet(context), bridge_map_switch1)
        context.host = nova_host2
        self.assertEqual(drv.get_host_physnet(context), bridge_map_switch2)

    def _test_get_baremetal_physnet(self, topo_switch_fqdn, bridge_map_fqdn,
                                    use_fqdn_physnet):
        cfg.CONF.set_override('use_fqdn_physnet', use_fqdn_physnet,
                              "ml2_arista")
        context = mock.MagicMock()
        topo_switch1 = 'switch1.full.name' if topo_switch_fqdn else 'switch1'
        topo_switch2 = 'switch2.full.name' if topo_switch_fqdn else 'switch2'
        bridge_map_switch1 = ('switch1.full.name' if bridge_map_fqdn
                              else 'switch1')
        bridge_map_switch2 = ('switch2.full.name' if bridge_map_fqdn
                              else 'switch2')
        context.host = 'host1'
        context.current = {portbindings.PROFILE: {
            'local_link_information': [{'switch_id': '00:00:00:00:00:00'}]}}
        topology = [{'hosts':
                     {'00:00:00:00:00:00': {'name': '00:00:00:00:00:00',
                                            'hostname': topo_switch1},
                      '00:00:00:00:00:01': {'name': '00:00:00:00:00:01',
                                            'hostname': topo_switch2}}}]
        drv = arista_eapi.AristaRPCWrapperEapi()
        drv._run_eos_cmds = mock.MagicMock()
        drv._run_eos_cmds.return_value = topology
        self.assertEqual(drv.get_baremetal_physnet(context),
                         bridge_map_switch1)
        context.host = 'host2'
        context.current = {portbindings.PROFILE: {
            'local_link_information': [{'switch_id': '00:00:00:00:00:01'}]}}
        self.assertEqual(drv.get_baremetal_physnet(context),
                         bridge_map_switch2)

    def test_get_host_physnet(self):
        for nova_fqdn in (True, False):
            for topo_host_fqdn in (True, False):
                for topo_switch_fqdn in (True, False):
                    for bridge_map_fqdn in (True, False):
                        if bridge_map_fqdn and not topo_switch_fqdn:
                            # Topology has less info than bridge map.
                            # This isn't supported
                            continue
                        use_fqdn = True
                        if nova_fqdn and not topo_host_fqdn:
                            use_fqdn = False
                        use_fqdn_physnet = True
                        if topo_switch_fqdn and not bridge_map_fqdn:
                            use_fqdn_physnet = False
                        self._test_get_host_physnet(nova_fqdn,
                                                    topo_host_fqdn,
                                                    topo_switch_fqdn,
                                                    bridge_map_fqdn,
                                                    use_fqdn,
                                                    use_fqdn_physnet)

    def test_get_baremetal_physnet(self):
        for topo_switch_fqdn in (True, False):
            for bridge_map_fqdn in (True, False):
                if bridge_map_fqdn and not topo_switch_fqdn:
                    # Topology has less info than bridge map.
                    # This isn't supported.
                    continue
                use_fqdn_physnet = True
                if topo_switch_fqdn and not bridge_map_fqdn:
                    use_fqdn_physnet = False
                self._test_get_baremetal_physnet(topo_switch_fqdn,
                                                 bridge_map_fqdn,
                                                 use_fqdn_physnet)
