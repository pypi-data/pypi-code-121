import json
import logging
import time
from typing import Union
from threading import Thread
from .base import BasePoint, BaseDriver, PointTableDict
from pysnmp.hlapi import *

'''
pip install pysnmp==4.4.12
'''

'''
    config
    {
        "device_host": "192.168.1.200:161",
        "cmd_timeout": 3,
        "cmd_retries": 3,
        "cmd_interval": 0.3,
        "multi_read": 20,
        "context_name": "",
        "context_id": "",
        "root_oid": "1.3",
        "enabled": true,
        "auth": {
            "v1": {"read_community": "public", "write_community": "private"},
            "v2": {"read_community": "public", "write_community": "private"},
            "v3": {"use_name": "", "security_level": 0, "auth_key": "", "priv_key": "", "auth_protocol": 0, "priv_protocol": 0}
        }
    }

'''


# SNMP Point
class SNMPPoint(BasePoint):

    def __init__(self, point_writable: bool, point_name: str, point_oid: str, point_description: str = ''):
        super().__init__('snmp', point_writable, point_name, point_description)
        self.point_oid = point_oid

    @property
    def get_point_oid(self):
        return self.point_oid


class SNMPEngine(Thread):

    def __init__(self, control_mode: str, snmp_transport: UdpTransportTarget,
                 snmp_auth: Union[CommunityData, UsmUserData], snmp_context: ContextData, cmd_interval: float,
                 limit: int, point_dict: dict, root_oid: str = '1.3', call_back_func=None):
        Thread.__init__(self)

        # param#########
        self.control_mode = control_mode
        self.cmd_interval = cmd_interval
        self.limit = limit
        self.snmp_auth = snmp_auth
        self.snmp_transport = snmp_transport
        self.snmp_context = snmp_context
        self.snmp_root_oid = root_oid
        self.point_dict = point_dict
        self.call_back_func = call_back_func
        ##############

        self.snmp_client = None
        self.snmp_oids = {}
        self.snmp_values = {}
        self.snmp_search = {}
        self.snmp_set_result = {}
        self.objects = [[]]

    def _sort_point_by_device(self):
        try:
            if len(self.point_dict) > 0:
                new_point_list = []

                for point_name in self.point_dict.keys():
                    point = self.point_dict[point_name]
                    self.snmp_oids[point.get_point_oid] = point_name
                    new_point_list.append([point.get_point_oid, point_name, point])

                new_point_list.sort(key=lambda t: (t[0], t[1]))

                for point in new_point_list:
                    if len(self.objects[-1]) >= self.limit:
                        self.objects.append([])
                    self.objects[-1].append(ObjectType(ObjectIdentity(point[0])))
                return True
        except Exception as e:
            raise e
        return False

    def _update_point_value(self):
        try:
            self.snmp_values = {}

            if self._ping_target() == True:
                for object in self.objects:
                    self._send_read_mutil(object)
        except Exception as e:
            raise e

    def _send_read_mutil(self, objects: list):
        try:
            if len(objects) > 0:
                var_binds = tuple(objects)
                error_indication, error_status, error_index, var_binds = next(
                    getCmd(SnmpEngine(),
                           self.snmp_auth,
                           self.snmp_transport,
                           self.snmp_context,
                           *var_binds)
                )
                if error_indication:
                    raise Exception(str(error_indication))
                elif error_status:
                    raise Exception(
                        f"{error_status.prettyPrint()} at {error_index and var_binds[int(error_index) - 1][0] or '?'}")
                else:
                    for var_bind in var_binds:
                        snmp_oid = str(var_bind[0])
                        value = var_bind[1].prettyPrint()
                        name = self.snmp_oids.get(snmp_oid)
                        if name is not None:
                            self.snmp_values[name] = value
        except Exception as e:
            logging.error(f"snmp({self.snmp_transport.transportAddr}) read({objects}) fail({e.__str__()})")
        time.sleep(self.cmd_interval)

    def run(self):
        try:
            self._sort_point_by_device()

            if self.control_mode == 'write':
                self._set_point_value()
            elif self.control_mode == 'scan':
                self.scan()
            else:
                self._update_point_value()

        except Exception as e:
            raise e

    # search###
    def scan(self):
        self.snmp_search = {}
        try:
            for (error_indication, error_status, error_index, var_binds) in bulkCmd(SnmpEngine(),
                                                                                    self.snmp_auth,
                                                                                    self.snmp_transport,
                                                                                    self.snmp_context,
                                                                                    0, 25,
                                                                                    ObjectType(ObjectIdentity(
                                                                                        self.snmp_root_oid)),
                                                                                    lookupMib=False,
                                                                                    lexicographicMode=False,
                                                                                    ignoreNonIncreasingOid=True):
                if error_indication:
                    if self.call_back_func:
                        self.call_back_func(f"error_indication: {error_indication}")
                    raise Exception(str(error_indication))
                elif error_status:
                    if self.call_back_func:
                        self.call_back_func(
                            f"error_status: {error_status.prettyPrint()} at {error_index and var_binds[int(error_index) - 1][0] or '?'}")
                    raise Exception(
                        f"{error_status.prettyPrint()} at {error_index and var_binds[int(error_index) - 1][0] or '?'}")
                else:
                    for var_bind in var_binds:
                        name = var_bind[0].prettyPrint()
                        value = var_bind[1].prettyPrint()
                        type = var_bind[1].__class__.__name__
                        self.snmp_search[name] = {'name': name, 'value': value, 'type': type}
                        if self.call_back_func:
                            self.call_back_func(
                                f"recv {len(self.snmp_search)} name: {name} type: {type} value: {value}")
        except Exception as e:
            logging.error(f"snmp({self.snmp_transport.transportAddr}) scan fail({e.__str__()})")

    def _ping_target(self):
        return True

    def get_values(self):
        return self.snmp_values

    def get_set_result(self):
        return self.snmp_set_result

    def _set_point_value(self):
        pass

    def get_points(self):
        return self.snmp_search


# SNMP Driver
class SNMPDriver(BaseDriver):

    def __init__(self, dict_config: dict, dict_point: PointTableDict):
        super().__init__(dict_config, dict_point)

        self.dict_snmp_point = {}

        ##snmp connect param ##########################
        self.snmp_auth = None
        self.snmp_transport = None
        self.snmp_context = None
        self.snmp_multi_read = 20
        self.snmp_cmd_interval = 0.3
        self.snmp_send_timeout = 3
        self.snmp_send_retries = 2
        self.snmp_root_oid = '1.3'
        ###########################

        self.configure()

    def __del__(self):
        super().__del__()

    def exit(self):
        pass

    def configure(self):
        try:
            # config
            self.snmp_transport = UdpTransportTarget((self.dict_config.get("device_host").split(':')[0],
                                                      int(self.dict_config.get("device_host").split(':')[1])),
                                                     timeout=self.dict_config.get('cmd_timeout', 3),
                                                     retries=self.dict_config.get('cmd_retries', 3))

            context_name = self.dict_config.get("context_name", '')
            context_id = self.dict_config.get("context_id", '')

            if len(context_name) != '' and len(context_id) == '':
                self.snmp_context = ContextData(contextName=context_name)
            elif len(context_name) == '' and len(context_id) != '':
                self.snmp_context = ContextData(contextEngineId=OctetString(hexValue=context_id))
            elif len(context_name) != '' and len(context_id) != '':
                self.snmp_context = ContextData(contextName=context_name,
                                                contextEngineId=OctetString(hexValue=context_id))
            else:
                self.snmp_context = ContextData()

            auth = self.dict_config.get('auth', {})
            if isinstance(auth, str):
                auth = json.loads(auth)

            if 'v1' in auth.keys():
                self.snmp_auth = CommunityData(auth.get('v1', {}).get('read_community'),
                                               auth.get('v1', {}).get('read_community'), mpModel=0)
            elif 'v2' in auth.keys():
                self.snmp_auth = CommunityData(auth.get('v2', {}).get('read_community'),
                                               auth.get('v2', {}).get('read_community'), mpModel=1)
            elif 'v3' in auth.keys():
                security_level = auth.get('v3', {}).get('security_level')
                use_name = auth.get('v3', {}).get('use_name')
                if security_level == 0:  # no auth, no priv
                    self.snmp_auth = UsmUserData(userName=use_name)
                elif security_level == 1:  # auth, no priv
                    auths = {0: usmNoAuthProtocol,
                             1: usmHMACMD5AuthProtocol,
                             2: usmHMACSHAAuthProtocol,
                             3: usmHMAC128SHA224AuthProtocol,
                             4: usmHMAC192SHA256AuthProtocol,
                             5: usmHMAC256SHA384AuthProtocol,
                             6: usmHMAC384SHA512AuthProtocol}
                    self.snmp_auth = UsmUserData(userName=use_name, authKey=auth.get('v3', {}).get('auth_key'),
                                                 authProtocol=auths.get(auth.get('v3', {}).get('auth_protocol')))
                elif security_level == 2:  # auth, priv
                    auths = {0: usmNoAuthProtocol,
                             1: usmHMACMD5AuthProtocol,
                             2: usmHMACSHAAuthProtocol,
                             3: usmHMAC128SHA224AuthProtocol,
                             4: usmHMAC192SHA256AuthProtocol,
                             5: usmHMAC256SHA384AuthProtocol,
                             6: usmHMAC384SHA512AuthProtocol}

                    privs = {0: usmNoPrivProtocol,
                             1: usmDESPrivProtocol,
                             2: usm3DESEDEPrivProtocol,
                             3: usmAesCfb128Protocol,
                             4: usmAesCfb192Protocol,
                             5: usmAesCfb256Protocol}
                    self.snmp_auth = UsmUserData(userName=use_name, authKey=auth.get('v3', {}).get('auth_key'),
                                                 authProtocol=auths.get(auth.get('v3', {}).get('auth_protocol')),
                                                 privKey=auth.get('v3', {}).get('priv_key'),
                                                 privProtocol=privs.get(auth.get('v3', {}).get('priv_protocol')))

            self.snmp_multi_read = self.dict_config.get("multi_read", 20)
            self.snmp_cmd_interval = self.dict_config.get("cmd_interval", 0.3)
            self.snmp_root_oid = self.dict_config.get("root_oid", "1.3")

            # csv
            for point_name in self.dict_point.keys():
                self.dict_snmp_point[point_name] = SNMPPoint(
                    bool(str(self.dict_point[point_name]['point_writable'])),
                    str(self.dict_point[point_name]['point_name']), str(self.dict_point[point_name]['point_oid']))

        except Exception as e:
            raise e

    # ping
    def ping_target(self):
        return True

    def get_points(self, dict_point: dict = {}) -> dict:
        result_dict = {}
        try:
            if len(dict_point) == 0:
                result_dict = self._scrap_points()
            else:
                result_dict = self._get_points(dict_point)
        except Exception as e:
            raise e
        return result_dict

    def _get_points(self, dict_point: dict) -> dict:
        result_dict = {}
        try:
            snmp_point_dict = {}
            for point_name in dict_point.keys():
                if point_name in self.dict_snmp_point.keys():
                    snmp_point_dict[point_name] = self.dict_snmp_point[point_name]

            if len(snmp_point_dict) > 0:
                result_dict = self._read_snmp_values(snmp_point_dict)
        except Exception as e:
            raise e
        return result_dict

    def _scrap_points(self) -> dict:
        result_dict = {}
        try:
            result_dict = self._read_snmp_values(self.dict_snmp_point)
        except Exception as e:
            raise e
        return result_dict

    def set_points(self, dict_point: dict) -> dict:
        set_result_dict = {}
        try:
            snmp_point_dict = {}
            for point_name in dict_point.keys():
                if point_name in self.dict_snmp_point.keys():
                    snmp_point = self.dict_snmp_point[point_name]
                    snmp_point.set_point_set_value(dict_point[point_name])
                    snmp_point_dict[point_name] = snmp_point

            if len(snmp_point_dict) > 0:
                result_dict = self._write_snmp_values(snmp_point_dict)
        except Exception as e:
            raise e
        return set_result_dict

    def reset_config(self, dict_config: dict):
        super().reset_config(dict_config)
        self.configure()

    def reset_point(self, dict_point: dict):
        super().reset_point(dict_point)
        self.configure()

    def search_points(self, call_back_func=None) -> dict:
        search_point = {}
        try:
            snmp_client = SNMPEngine('scan', self.snmp_transport, self.snmp_auth, self.snmp_context,
                                         self.snmp_cmd_interval, self.snmp_multi_read, {}, self.snmp_root_oid,
                                         call_back_func)
            snmp_client.setDaemon(True)
            snmp_client.start()
            snmp_client.join()
            search_point.update(snmp_client.get_points())
        except Exception as e:
            raise e
        return search_point

    def _read_snmp_values(self, snmp_points: dict) -> dict:
        result_dict = {}
        try:
            snmp_client = SNMPEngine('read', self.snmp_transport, self.snmp_auth, self.snmp_context,
                                         self.snmp_cmd_interval, self.snmp_multi_read, snmp_points)
            snmp_client.setDaemon(True)
            snmp_client.start()
            snmp_client.join()
            result_dict.update(snmp_client.get_values())
        except Exception as e:
            raise e
        return result_dict

    def _write_snmp_values(self, snmp_points: dict) -> dict:
        result_dict = {}
        try:
            snmp_client = SNMPEngine('write', self.snmp_transport, self.snmp_auth, self.snmp_context,
                                         self.snmp_cmd_interval, self.snmp_multi_read, snmp_points)
            snmp_client.setDaemon(True)
            snmp_client.start()
            snmp_client.join()
            result_dict.update(snmp_client.get_set_result())
        except Exception as e:
            raise e
        return result_dict

    ###########