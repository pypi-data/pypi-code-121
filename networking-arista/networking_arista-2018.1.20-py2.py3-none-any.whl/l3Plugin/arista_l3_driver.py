# Copyright 2014 Arista Networks, Inc.  All rights reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import hashlib
import socket
import struct

from neutron.plugins.ml2.driver_context import NetworkContext  # noqa
from neutron_lib.callbacks import events
from neutron_lib.callbacks import registry
from neutron_lib.callbacks import resources
from neutron_lib import constants as const
from neutron_lib import context as nctx
from oslo_config import cfg
from oslo_log import log as logging

from networking_arista._i18n import _, _LI
from networking_arista.common import api
from networking_arista.common import db_lib
from networking_arista.common import exceptions as arista_exc

LOG = logging.getLogger(__name__)
cfg.CONF.import_group('l3_arista', 'networking_arista.common.config')

EOS_UNREACHABLE_MSG = _('Unable to reach EOS')
DEFAULT_VLAN = 1
MLAG_SWITCHES = 2
VIRTUAL_ROUTER_MAC = '00:11:22:33:44:55'
IPV4_BITS = 32
IPV6_BITS = 128

# This string-format-at-a-distance confuses pylint :(
# pylint: disable=too-many-format-args
router_in_vrf_v1 = {
    'router': {'create': ['vrf definition {0}',
                          'rd {1}',
                          'exit',
                          'ip routing vrf {0}'],
               'delete': ['no vrf definition {0}']},
    'interface': {'add': ['vlan {0}',
                          'exit',
                          'interface vlan {0}',
                          'vrf forwarding {1}',
                          'ip address {2}'],
                  'remove': ['no interface vlan {0}']}}

router_in_vrf_v2 = {
    'router': {'create': ['vrf instance {0}',
                          'rd {1}',
                          'exit',
                          'ip routing vrf {0}'],
               'delete': ['no vrf instance {0}']},
    'interface': {'add': ['vlan {0}',
                          'exit',
                          'interface vlan {0}',
                          'vrf {1}',
                          'ip address {2}'],
                  'remove': ['no interface vlan {0}']}}

router_in_default_vrf = {
    'router': {'create': [],   # Place holder for now.
               'delete': []},  # Place holder for now.

    'interface': {'add': ['ip routing',
                          'vlan {0}',
                          'exit',
                          'interface vlan {0}',
                          'ip address {2}'],
                  'remove': ['no interface vlan {0}']}}

router_in_default_vrf_v6 = {
    'router': {'create': [],
               'delete': []},

    'interface': {'add': ['ipv6 unicast-routing',
                          'vlan {0}',
                          'exit',
                          'interface vlan {0}',
                          'ipv6 enable',
                          'ipv6 address {2}'],
                  'remove': ['no interface vlan {0}']}}

additional_cmds_for_mlag = {
    'router': {'create': ['ip virtual-router mac-address {0}'],
               'delete': []},

    'interface': {'add': ['ip virtual-router address {0}'],
                  'remove': []}}

additional_cmds_for_mlag_v6 = {
    'router': {'create': [],
               'delete': []},

    'interface': {'add': ['ipv6 virtual-router address {0}'],
                  'remove': []}}

additional_cmds_for_default_route = {
    'add': ['ip route vrf {0} 0.0.0.0/0 {1}'],
    # Remove is used when updating a network to remove default gateway
    # when deleting an interface we don't need to delete the route
    'remove': ['no ip route vrf {0} 0.0.0.0/0']}


class AristaL3Driver(object):
    """Wraps Arista JSON RPC.

    All communications between Neutron and EOS are over JSON RPC.
    EOS - operating system used on Arista hardware
    Command API - JSON RPC API provided by Arista EOS
    """
    def __init__(self):
        self._servers = []
        self._hosts = []
        self._interfaceDict = None
        self._validate_config()
        host = cfg.CONF.l3_arista.primary_l3_host
        self._hosts.append(host)
        self._servers.append(self._make_eapi_client(host))
        self._mlag_configured = cfg.CONF.l3_arista.mlag_config
        self._vrf_syntax_v2_supported = None
        self._router_in_vrf = router_in_vrf_v2
        self._use_vrf = cfg.CONF.l3_arista.use_vrf
        self._vrf_default_route = False
        if self._use_vrf:
            self._vrf_default_route = cfg.CONF.l3_arista.vrf_default_route
            if self._vrf_default_route:
                # only subscribe for events if vrf default route is enabled
                self.subscribe()
        if self._mlag_configured:
            host = cfg.CONF.l3_arista.secondary_l3_host
            self._hosts.append(host)
            self._servers.append(self._make_eapi_client(host))
            self._additionalRouterCmdsDict = additional_cmds_for_mlag['router']
            self._additionalInterfaceCmdsDict = (
                additional_cmds_for_mlag['interface'])
        if self._use_vrf:
            self.routerDict = self._router_in_vrf['router']
            self._update_vrf_commands(keep_alive=False)
            self._interfaceDict = self._router_in_vrf['interface']
        else:
            self.routerDict = router_in_default_vrf['router']
            self._interfaceDict = router_in_default_vrf['interface']
        self._enable_cleanup = cfg.CONF.l3_arista.enable_cleanup
        self._protected_vlans = self._parse_protected_vlans(
            cfg.CONF.l3_arista.protected_vlans)

    def subscribe(self):
        # Subscribe to the events related to networks and subnets
        registry.subscribe(self.update_subnet, resources.SUBNET,
                           events.AFTER_UPDATE)
        registry.subscribe(self.update_network, resources.NETWORK,
                           events.AFTER_UPDATE)

    def update_subnet(self, resource, event, trigger, **kwargs):
        subnet_info = kwargs['subnet']

        if subnet_info['ip_version'] == 6:
            LOG.info('IPv6 networks not supported with L3 plugin')
            return
        ctx = nctx.get_admin_context()
        ml2_db = NetworkContext(self, ctx, {'id': subnet_info['network_id']})
        seg_id = ml2_db.network_segments[0]['segmentation_id']
        router_info = db_lib.get_subnet_gateway_ipv4(subnet_info['id'])
        if router_info:
            router_info['seg_id'] = seg_id
            router_name = self._arista_router_name(router_info['id'],
                                                   router_info['name'])
            self._delete_default_gateway(router_name)
            self.add_router_interface(ctx, router_info)
            self._setup_default_gateway(router_info)

    def _reset_network_default_route(self, network_id):
        router_info = self._prepare_network_default_gateway(network_id)
        if router_info:
            router_name = self._arista_router_name(router_info['id'],
                                                   router_info['name'])
            self._delete_default_gateway(router_name)
            self._add_network_default_gateway(network_id)

    def update_network(self, resource, event, trigger, **kwargs):
        network_info = kwargs['network']
        self._reset_network_default_route(network_info['id'])

    def _prepare_network_default_gateway(self, network_id):
        router_info = db_lib.get_network_gateway_ipv4(network_id)
        if not router_info:
            return

        ip_version = router_info['ip_version']
        if ip_version == 6:
            LOG.info('IPv6 networks not supported with L3 plugin')
            return

        ctx = nctx.get_admin_context()
        ml2_db = NetworkContext(self, ctx, {'id': network_id})
        seg_id = ml2_db.network_segments[0]['segmentation_id']
        router_info['seg_id'] = seg_id
        return router_info

    def _add_network_default_gateway(self, network_id):
        router_info = self._prepare_network_default_gateway(network_id)
        if router_info:
            ctx = nctx.get_admin_context()
            self.add_router_interface(ctx, router_info)
            self._setup_default_gateway(router_info)

    @staticmethod
    def _raise_invalid_protected_vlans(vlan_string):
        msg = '%s is not a valid vlan or vlan range' % vlan_string
        LOG.error(msg)
        raise arista_exc.AristaServicePluginConfigError(msg=msg)

    def _parse_protected_vlans(self, vlan_strings):
        # VLAN 1 is always protected as it exists by default on EOS
        vlans = set([1])
        for vlan_string in vlan_strings:
            vlan_parsed = vlan_string.split(':', 2)

            if len(vlan_parsed) > 2:
                self._raise_invalid_protected_vlans(vlan_string)

            try:
                min_vlan = int(vlan_parsed[0])
            except ValueError:
                self._raise_invalid_protected_vlans(vlan_string)

            try:
                max_vlan = int(vlan_parsed[-1])
            except ValueError:
                self._raise_invalid_protected_vlans(vlan_string)

            if not (const.MIN_VLAN_TAG <= min_vlan
                    <= max_vlan <= const.MAX_VLAN_TAG):
                self._raise_invalid_protected_vlans(vlan_string)
            vlans.update(range(min_vlan, max_vlan + 1))
        return vlans

    @staticmethod
    def _make_eapi_client(host):
        return api.EAPIClient(
            host,
            username=cfg.CONF.l3_arista.primary_l3_host_username,
            password=cfg.CONF.l3_arista.primary_l3_host_password,
            verify=False,
            timeout=cfg.CONF.l3_arista.conn_timeout
        )

    def _supports_vrf_instance(self, version):
        ver_tokens = version.split('.')
        if len(ver_tokens) < 2 or int(ver_tokens[0]) < 4:
            return False
        if int(ver_tokens[0]) == 4 and int(ver_tokens[1]) < 22:
            return False
        return True

    def _check_vrf_syntax_v2_support(self, host, keep_alive=True):
        cmds = ['show version']
        result = None
        try:
            result = self._run_eos_cmds(cmds, host, log_exception=False,
                                        keep_alive=keep_alive,
                                        update_vrf_commands=False)
            LOG.info('show version result %s' % result)
        except Exception:
            # We don't know what exception we got return None
            # At this moment we don't know what command we support for vrf
            # creation
            return None

        return result and self._supports_vrf_instance(result[0].get('version',
                                                                    ''))

    def _update_vrf_commands(self, keep_alive=True):
        # This assumes all switches run the same version. This needs to be
        # updated if we'll support distributed routing
        new_vrf_support = self._check_vrf_syntax_v2_support(
            self._servers[0], keep_alive=keep_alive)

        if new_vrf_support == self._vrf_syntax_v2_supported:
            return

        LOG.info(_LI('Updating VRF command supported: %s'),
                 'vrf instance' if new_vrf_support else 'vrf definition')
        self._vrf_syntax_v2_supported = new_vrf_support
        if self._vrf_syntax_v2_supported is False:
            self._router_in_vrf = router_in_vrf_v1
        else:
            self._router_in_vrf = router_in_vrf_v2
        # we don't need to update self.interfaceDict as it is updated by
        # _select_dicts function before it is used
        self.routerDict = self._router_in_vrf['router']

    def _validate_config(self):
        if cfg.CONF.l3_arista.get('primary_l3_host') == '':
            msg = _('Required option primary_l3_host is not set')
            LOG.error(msg)
            raise arista_exc.AristaServicePluginConfigError(msg=msg)
        if cfg.CONF.l3_arista.get('mlag_config'):
            if cfg.CONF.l3_arista.get('secondary_l3_host') == '':
                msg = _('Required option secondary_l3_host is not set')
                LOG.error(msg)
                raise arista_exc.AristaServicePluginConfigError(msg=msg)
        if cfg.CONF.l3_arista.get('primary_l3_host_username') == '':
            msg = _('Required option primary_l3_host_username is not set')
            LOG.error(msg)
            raise arista_exc.AristaServicePluginConfigError(msg=msg)

    def create_router_on_eos(self, router_name, rdm, server):
        """Creates a router on Arista HW Device.

        :param router_name: globally unique identifier for router/VRF
        :param rdm: A value generated by hashing router name
        :param server: Server endpoint on the Arista switch to be configured
        """
        cmds = []
        rd = "%s:%s" % (rdm, rdm)

        for c in self.routerDict['create']:
            cmds.append(c.format(router_name, rd))

        if self._mlag_configured:
            mac = VIRTUAL_ROUTER_MAC
            for c in self._additionalRouterCmdsDict['create']:
                cmds.append(c.format(mac))

        self._run_config_cmds(cmds, server)

    def delete_router_from_eos(self, router_name, server):
        """Deletes a router from Arista HW Device.

        :param router_name: globally unique identifier for router/VRF
        :param server: Server endpoint on the Arista switch to be configured
        """
        cmds = []
        for c in self.routerDict['delete']:
            cmds.append(c.format(router_name))
        if self._mlag_configured:
            for c in self._additionalRouterCmdsDict['delete']:
                cmds.append(c)

        self._run_config_cmds(cmds, server)

    def _select_dicts(self, ipv):
        if self._use_vrf:
            if ipv == 6:
                msg = (_('IPv6 subnets are not supported with VRFs'))
                LOG.info(msg)

            self._interfaceDict = self._router_in_vrf['interface']
        else:
            if ipv == 6:
                # for IPv6 use IPv6 commands
                self._interfaceDict = router_in_default_vrf_v6['interface']
                self._additionalInterfaceCmdsDict = (
                    additional_cmds_for_mlag_v6['interface'])
            else:
                self._interfaceDict = router_in_default_vrf['interface']
                self._additionalInterfaceCmdsDict = (
                    additional_cmds_for_mlag['interface'])

    def add_interface_to_router(self, segment_id,
                                router_name, fixed_ip, router_ip, mask,
                                server):
        """Adds an interface to existing HW router on Arista HW device.

        :param segment_id: VLAN Id associated with interface that is added
        :param router_name: globally unique identifier for router/VRF
        :param fixed_ip: Fixed IP associated with the port
        :param router_ip: IP address of the router
        :param mask: subnet mask to be used
        :param server: Server endpoint on the Arista switch to be configured
        """

        if not segment_id:
            segment_id = DEFAULT_VLAN
        cmds = []
        for c in self._interfaceDict['add']:
            if self._mlag_configured:
                # In VARP config, use router ID else, use fixed IP.
                # If fixed Ip was not set this will be gateway IP address.
                ip = router_ip
            else:
                ip = fixed_ip + '/' + mask
            cmds.append(c.format(segment_id, router_name, ip))
        if self._mlag_configured:
            for c in self._additionalInterfaceCmdsDict['add']:
                cmds.append(c.format(fixed_ip))

        self._run_config_cmds(cmds, server)

    def delete_interface_from_router(self, segment_id, router_name, server):
        """Deletes an interface from existing HW router on Arista HW device.

        :param segment_id: VLAN Id associated with interface that is added
        :param router_name: globally unique identifier for router/VRF
        :param server: Server endpoint on the Arista switch to be configured
        """

        if not segment_id:
            segment_id = DEFAULT_VLAN
        cmds = []
        for c in self._interfaceDict['remove']:
            cmds.append(c.format(segment_id))

        self._run_config_cmds(cmds, server)

    def create_router(self, context, router):
        """Creates a router on Arista Switch.

        Deals with multiple configurations - such as Router per VRF,
        a router in default VRF, Virtual Router in MLAG configurations
        """
        if router:
            router_name = self._arista_router_name(router['id'],
                                                   router['name'])

            hashed = hashlib.sha256(router_name.encode('utf-8'))
            rdm = str(int(hashed.hexdigest(), 16) % 65536)

            mlag_peer_failed = False
            for s in self._servers:
                try:
                    self.create_router_on_eos(router_name, rdm, s)
                    mlag_peer_failed = False
                except Exception:
                    if self._mlag_configured and not mlag_peer_failed:
                        # In paired switch, it is OK to fail on one switch
                        mlag_peer_failed = True
                    else:
                        msg = (_('Failed to create router %s on EOS') %
                               router_name)
                        LOG.exception(msg)
                        raise arista_exc.AristaServicePluginRpcError(msg=msg)

            if self._vrf_default_route:
                ext_gateway = router.get('external_gateway_info')
                if ext_gateway:
                    network_id = ext_gateway.get('network_id')
                    if network_id:
                        self._add_network_default_gateway(network_id)

    def delete_router(self, context, router_id, router):
        """Deletes a router from Arista Switch."""

        if router:
            router_name = self._arista_router_name(router_id, router['name'])
            mlag_peer_failed = False
            for s in self._servers:
                try:
                    self.delete_router_from_eos(router_name, s)
                    mlag_peer_failed = False
                except Exception:
                    if self._mlag_configured and not mlag_peer_failed:
                        # In paired switch, it is OK to fail on one switch
                        mlag_peer_failed = True
                    else:
                        msg = (_('Failed to create router %s on EOS') %
                               router_name)
                        LOG.exception(msg)
                        raise arista_exc.AristaServicePluginRpcError(msg=msg)

    def update_router(self, context, router_id, original_router, new_router):
        """Updates a router which is already created on Arista Switch.

        """
        if not self._vrf_default_route or not new_router:
            return

        ext_gateway = new_router.get('external_gateway_info')
        if ext_gateway is None:
            # Remove default gateway if it exists
            orig_ext_gateway = original_router.get('external_gateway_info')
            if orig_ext_gateway is None:
                # External gateway did not change
                return
            network_id = orig_ext_gateway['network_id']
            ml2_db = NetworkContext(self, context, {'id': network_id})
            seg_id = ml2_db.network_segments[0]['segmentation_id']
            new_router['seg_id'] = seg_id
            new_router['ip_version'] = 4
            self.remove_router_interface(context, new_router,
                                         delete_gateway=True)
            return

        network_id = ext_gateway.get('network_id')
        if network_id:
            self._reset_network_default_route(network_id)

    def _setup_default_gateway(self, router_info):
        mlag_peer_failed = False
        gip = router_info['gip']
        router_name = self._arista_router_name(router_info['id'],
                                               router_info['name'])

        for s in self._servers:
            try:
                self._setup_switch_default_gateway(router_name, gip, s)
                mlag_peer_failed = False
            except Exception:
                if self._mlag_configured and not mlag_peer_failed:
                    # In paired switch, it is OK to fail on one switch
                    mlag_peer_failed = True
                else:
                    msg = (_('Failed to setup router gateway %s on EOS') %
                           router_name)
                    LOG.exception(msg)
                    raise arista_exc.AristaServicePluginRpcError(msg=msg)

    def _setup_switch_default_gateway(self, router_name, gip, server):
        cmds = [
            c.format(router_name, gip)
            for c in additional_cmds_for_default_route['add']
        ]

        self._run_config_cmds(cmds, server)

    def _delete_default_gateway(self, router_name):
        mlag_peer_failed = False

        for s in self._servers:
            try:
                self._delete_switch_default_gateway(router_name, s)
                mlag_peer_failed = False
            except Exception:
                if self._mlag_configured and not mlag_peer_failed:
                    # In paired switch, it is OK to fail on one switch
                    mlag_peer_failed = True
                else:
                    msg = (_('Failed to delete router gateway %s on EOS') %
                           router_name)
                    LOG.exception(msg)
                    raise arista_exc.AristaServicePluginRpcError(msg=msg)

    def _delete_switch_default_gateway(self, router_name, server):
        cmds = [
            c.format(router_name)
            for c in additional_cmds_for_default_route['remove']
        ]

        self._run_config_cmds(cmds, server)

    def add_router_interface(self, context, router_info):
        """Adds an interface to a router created on Arista HW router.

        This deals with both IPv6 and IPv4 configurations.
        """
        if router_info:
            if router_info['ip_version'] == 6 and self._use_vrf:
                # For the moment we ignore the interfaces to be added
                # on IPv6 subnets.
                LOG.info('Using VRFs. Ignoring IPv6 interface')
                return
            self._select_dicts(router_info['ip_version'])
            cidr = router_info['cidr']
            subnet_mask = cidr.split('/')[1]
            router_name = self._arista_router_name(router_info['id'],
                                                   router_info['name'])
            if self._mlag_configured:
                # For MLAG, we send a specific IP address as opposed to cidr
                # For now, we are using x.x.x.253 and x.x.x.254 as virtual IP
                # unless either collides with the router interface fixed_ip,
                # in which case we use x.x.x.252
                mlag_peer_failed = False
                router_ips = self._get_router_ips(cidr, len(self._servers),
                                                  router_info['ip_version'],
                                                  router_info['fixed_ip'])
                for i, server in enumerate(self._servers):
                    # Get appropriate virtual IP address for this router
                    router_ip = router_ips[i]
                    try:
                        self.add_interface_to_router(router_info['seg_id'],
                                                     router_name,
                                                     router_info['fixed_ip'],
                                                     router_ip, subnet_mask,
                                                     server)
                        mlag_peer_failed = False
                    except Exception:
                        if not mlag_peer_failed:
                            mlag_peer_failed = True
                        else:
                            msg = (_('Failed to add interface to router '
                                     '%s on EOS') % router_name)
                            LOG.exception(msg)
                            raise arista_exc.AristaServicePluginRpcError(
                                msg=msg)

            else:
                for s in self._servers:
                    self.add_interface_to_router(router_info['seg_id'],
                                                 router_name,
                                                 router_info['fixed_ip'],
                                                 None, subnet_mask, s)

    def remove_router_interface(self, context, router_info,
                                delete_gateway=False):
        """Removes previously configured interface from router on Arista HW.

        This deals with both IPv6 and IPv4 configurations.
        """
        if router_info:
            if router_info['ip_version'] == 6 and self._use_vrf:
                # For the moment we ignore the interfaces to be added
                # on IPv6 subnets.
                LOG.info('Using VRFs. Ignoring IPv6 interface')
                return
            router_name = self._arista_router_name(router_info['id'],
                                                   router_info['name'])
            mlag_peer_failed = False
            for s in self._servers:
                try:
                    if delete_gateway:
                        self._delete_switch_default_gateway(router_name, s)
                    self.delete_interface_from_router(router_info['seg_id'],
                                                      router_name, s)
                    if self._mlag_configured:
                        mlag_peer_failed = False
                except Exception:
                    if self._mlag_configured and not mlag_peer_failed:
                        mlag_peer_failed = True
                    else:
                        msg = (_('Failed to remove interface to router '
                                 '%s on EOS') % router_name)
                        LOG.exception(msg)
                        raise arista_exc.AristaServicePluginRpcError(msg=msg)

    def _run_config_cmds(self, commands, server, log_exception=True,
                         keep_alive=True, update_vrf_commands=True):
        """Execute/sends a CAPI (Command API) command to EOS.

        In this method, list of commands is appended with prefix and
        postfix commands - to make is understandble by EOS.

        :param commands : List of command to be executed on EOS.
        :param server: Server endpoint on the Arista switch to be configured
        """
        command_start = ['enable', 'configure']
        command_end = ['exit']
        full_command = command_start + commands + command_end
        self._run_eos_cmds(full_command, server, log_exception, keep_alive,
                           update_vrf_commands)

    def _run_eos_cmds(self, commands, server, log_exception=True,
                      keep_alive=True, update_vrf_commands=True):
        LOG.info(_LI('Executing command on Arista EOS: %s'), commands)

        try:
            # this returns array of return values for every command in
            # full_command list
            ret = server.execute(commands, keep_alive=keep_alive)
            LOG.info(_LI('Results of execution on Arista EOS: %s'), ret)
            return ret
        except arista_exc.AristaServicePluginInvalidCommand:
            msg = (_('VRF creation command unsupported. This request should '
                     'work on next retry.'))
            if log_exception:
                LOG.exception(msg)
            if self._use_vrf and update_vrf_commands:
                # For now we assume that the only command that raises this
                # exception is vrf instance/definition and we need to update
                # the current support
                self._update_vrf_commands()
            raise
        except Exception:
            msg = (_('Error occurred while trying to execute '
                     'commands %(cmd)s on EOS %(host)s') %
                   {'cmd': commands, 'host': server})
            if log_exception:
                LOG.exception(msg)
            raise arista_exc.AristaServicePluginRpcError(msg=msg)

    def _arista_router_name(self, router_id, name):
        """Generate an arista specific name for this router.

        Use a unique name so that OpenStack created routers/SVIs
        can be distinguishged from the user created routers/SVIs
        on Arista HW. Replace spaces with underscores for CLI compatibility
        """
        return '__OpenStack__' + router_id + '-' + name.replace(' ', '_')

    def _get_binary_from_ipv4(self, ip_addr):
        """Converts IPv4 address to binary form."""

        return struct.unpack("!L", socket.inet_pton(socket.AF_INET,
                                                    ip_addr))[0]

    def _get_binary_from_ipv6(self, ip_addr):
        """Converts IPv6 address to binary form."""

        hi, lo = struct.unpack("!QQ", socket.inet_pton(socket.AF_INET6,
                                                       ip_addr))
        return (hi << 64) | lo

    def _get_ipv4_from_binary(self, bin_addr):
        """Converts binary address to Ipv4 format."""

        return socket.inet_ntop(socket.AF_INET, struct.pack("!L", bin_addr))

    def _get_ipv6_from_binary(self, bin_addr):
        """Converts binary address to Ipv6 format."""

        hi = bin_addr >> 64
        lo = bin_addr & 0xFFFFFFFF
        return socket.inet_ntop(socket.AF_INET6, struct.pack("!QQ", hi, lo))

    def _get_router_ips(self, cidr, ip_count, ip_ver, fixed_ip):
        """For a given IP subnet and IP version type, generate IP for router.

        This method takes the network address (cidr) and selects a set of
        IP addresses that should be assigned to virtual router running
        on multiple switches. It uses upper addresses in a subnet address
        as IP for the router. Each instace of the router, on each switch,
        requires uniqe IP address. For example in IPv4 case, on a 255
        subnet, it will pick X.X.X.254 as first addess, X.X.X.253 for next,
        and so on, skipping an address specified as the reserved_ip
        """
        network_addr, prefix = cidr.split('/')
        if ip_ver == 4:
            bits = IPV4_BITS
            ip = self._get_binary_from_ipv4(network_addr)
        elif ip_ver == 6:
            bits = IPV6_BITS
            ip = self._get_binary_from_ipv6(network_addr)

        mask = (pow(2, bits) - 1) << (bits - int(prefix))

        network_addr = ip & mask

        router_ips = list()
        ip_idx = 0
        while len(router_ips) < ip_count:
            start_ip = MLAG_SWITCHES + ip_idx
            router_ip = pow(2, bits - int(prefix)) - start_ip

            router_ip = network_addr | router_ip
            if ip_ver == 4:
                router_ip = self._get_ipv4_from_binary(router_ip)
            else:
                router_ip = self._get_ipv6_from_binary(router_ip)
            ip_idx += 1
            if router_ip != fixed_ip.lower():
                router_ips.append(router_ip + '/' + prefix)
        return router_ips
