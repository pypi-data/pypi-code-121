import logging
import time
import os
import sys
import re

import Pyro4.core
from typing import Optional, Callable
from datetime import datetime
from threading import Thread, Event, Lock
from .base import BasePoint, BaseDriver, PointTableDict

'''
    链接：
        https://github.com/joseamaita/openopc120
    注册dll:
        C:\OpenOPC34\lib>regsvr32 gbda_aut.dll
    环境变量：
        OPC_DA_CLASS
        OPC_DA_CLIENT
        OPC_DA_SERVER
'''

'''
    pip install Pyro4==4.81

    安装OpenOPC-1.3.1.win32-py2.7.exe
    兼容旧项目
    OPCTag,OPC类型，OPC服务名，倍率，OPC组名, OPC地址（IP IP:端口）,OPC连接号

'''

if os.name == 'nt':
    import pywintypes
    import pythoncom
    import win32com.client
    pywintypes.datetime = pywintypes.TimeType
    vt = dict([(pythoncom.__dict__[vtype], vtype) for vtype in pythoncom.__dict__.keys() if vtype[:2] == "VT"])

    # Allow gencache to create the cached wrapper objects
    win32com.client.gencache.is_readonly = False

    # Under p2exe the call in gencache to __init__() does not happen
    # so we use Rebuild() to force the creation of the gen_py folder
    win32com.client.gencache.Rebuild(verbose=0)

# OPC Constants
OPC_CLASS = 'Matrikon.OPC.Automation;Graybox.OPC.DAWrapper;HSCOPC.Automation;RSI.OPCAutomation;OPC.Automation'
OPC_SERVER = 'Hci.TPNServer;HwHsc.OPCServer;opc.deltav.1;AIM.OPC.1;Yokogawa.ExaopcDAEXQ.1;OSI.DA.1;OPC.PHDServerDA.1;Aspen.Infoplus21_DA.1;National Instruments.OPCLabVIEW;RSLinx OPC Server;KEPware.KEPServerEx.V4;Matrikon.OPC.Simulation;Prosys.OPC.Simulation;CCOPC.XMLWrapper.1;OPC.SimaticHMI.CoRtHmiRTm.1'
OPC_PORT = 8804

def get_sessions(host='localhost', port=OPC_PORT):
    """Return sessions in OpenOPC Gateway Service as GUID:host hash"""
    server_obj = Pyro4.Proxy("PYRO:opc@{0}:{1}".format(host, port))
    return server_obj.get_clients()

def close_session(guid, host='localhost', port=OPC_PORT):
    server_obj = Pyro4.Proxy("PYRO:opc@{0}:{1}".format(host, port))
    return server_obj.force_close(guid)

def close_all_sessions(host='localhost', port=OPC_PORT):
    """Return sessions in OpenOPC Gateway Service as GUID:host hash"""
    server_obj = Pyro4.Proxy("PYRO:opc@{0}:{1}".format(host, port))
    return server_obj.close_all_sessions()

def open_client(host='localhost', port=OPC_PORT):
    """Connect to the specified OpenOPC Gateway Service"""
    server_obj = Pyro4.Proxy("PYRO:opc@{0}:{1}".format(host, port))
    return server_obj.create_client()

def get_info(host='localhost', port=OPC_PORT):
    """Connect to the specified OpenOPC Gateway Service"""
    server_obj = Pyro4.Proxy("PYRO:opc@{0}:{1}".format(host, port))
    return server_obj.get_info()

def restart(host='localhost', port=OPC_PORT):
    """Connect to the specified OpenOPC Gateway Service"""
    server_obj = Pyro4.Proxy("PYRO:opc@{0}:{1}".format(host, port))
    return server_obj.restart()

@Pyro4.expose  # needed for 4.55
class OPCClient():

    class GroupEvents:
        def __init__(self):
            self.client = None

        def set_client(self, client):
            self.client = client

        def OnDataChange(self, TransactionID, NumItems, ClientHandles, ItemValues, Qualities, TimeStamps):
            self.client.parse_data_change_value('OnDataChange', TransactionID, NumItems, ClientHandles, ItemValues,
                                                Qualities, TimeStamps)

        def OnAsyncReadComplete(self, TransactionID, NumItems, ClientHandles, ItemValues, Qualities, TimeStamps,
                                Errors):
            self.client.parse_data_change_value('OnAsyncReadComplete', TransactionID, NumItems, ClientHandles,
                                                ItemValues, Qualities, TimeStamps, Errors)

        def OnAsyncWriteComplete(self, TransactionID, NumItems, ClientHandles, Errors):
            self.client.parse_data_change_value('OnAsyncWriteComplete', TransactionID, NumItems, ClientHandles, None,
                                                None, None, Errors)

        def OnAsyncCancelComplete(self, CancelID):
            # Not working, not in VB either
            pass

    class ServerEvents:

        def __init__(self):
            self.client = None

        def set_client(self, client):
            self.client = client

        def OnServerShutDown(self, Reason):
            if self.client:
                self.client.server_shut_down(Reason)

    def __init__(self, opc_class=None, client_name=None):
        """Instantiate OPC automation class"""
        pythoncom.CoInitializeEx(pythoncom.COINIT_MULTITHREADED)

        ##default const########
        self.default_opc_client = 'OPCDA_CLIENT'
        self.default_data_source_cache = 1
        self.default_data_source_device = 2
        self.default_opc_status = (0, 'Running', 'Failed', 'NoConfig', 'Suspended', 'Test')
        self.default_browser_type = (0, 'Hierarchical', 'Flat')
        self.default_access_rights = (0, 'Read', 'Write', 'Read/Write')
        self.default_opc_quality = ('Bad', 'Uncertain', 'Unknown', 'Good')

        ############
        self.opc_client = None
        self.opc_class = opc_class if opc_class is not None else os.environ.get('OPC_DA_CLASS', OPC_CLASS)
        self.opc_client_name = client_name if client_name is not None else os.getenv('OPC_DA_CLIENT', self.default_opc_client)
        self._get_opc_client()
        self.opc_server = None
        self.opc_host = None
        self.opc_port = None
        self.opc_connected = False
        self.last_read = time.time()
        self.opc_data_change = time.time()
        self.last_used = time.time()

        self.opc_groups = {}        #组
        self.opc_group_tags = {}    # group: tag: clienid
        self.opc_group_hooks = {}   #组事件
        self.opc_group_server_handles = {}  #组ServerID
        self.opc_group_tag_values = {}  #组ID值
        self.opc_group_transaction_id = {}  #订阅ID对应事件
        self.opc_client_handle = 0
        self.opc_client_handle_value = {}    #handle: value
        self.opc_async_timeout = 10

        self.opc_open_guid = None
        self.opc_open_server = None
        self.opc_open = None
        self.opc_transaction_id = 0
        self.opc_prev_serv_time = None

    def __del__(self):
        pythoncom.CoUninitialize()
        self.close(True)

    def _get_opc_client(self):
        opc_class_list = self.opc_class.split(';')
        for i, c in enumerate(opc_class_list):
            try:
                self.opc_client = win32com.client.gencache.EnsureDispatch(c, 0)
                server_event = win32com.client.WithEvents(self.opc_client, self.ServerEvents)
                server_event.set_client(self)
                self.opc_class = c
                break
            except pythoncom.com_error as err:
                if i == len(opc_class_list) - 1:
                    raise Exception(f"EnsureDispatch '{c}' fail: {self._get_error_str(err)}")

    def format_time(self, timestamp: float):
        try:
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(timestamp)))
        except:
            pass
        return timestamp

    def get_opc_info(self) -> dict:
        info = {}
        info['guid'] = self.guid()
        info['server'] = self.opc_server
        info['status'] = self.opc_connected
        info['group'] = {}
        for opc_group, tags  in self.opc_group_tags.items():
            info['group'][opc_group] = len(tags)
        info['data_change'] = self.format_time(self.opc_data_change)
        info['last_used'] = self.format_time(self.last_used)
        return info

    def is_connected(self):
        return self.opc_connected

    def server_shut_down(self, reason):
        self.opc_connected = False
        print(f"Server Shutdown({reason}) at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    ###base tool function
    def _exceptional(self, func, alt_return=None, alt_exceptions=(Exception,), final=None, catch=None):
        """Turns exceptions into an alternative return value"""

        def __exceptional(*args, **kwargs):
            try:
                try:
                    return func(*args, **kwargs)
                except alt_exceptions:
                    return alt_return
                except:
                    if catch: return catch(sys.exc_info(), lambda: func(*args, **kwargs))
                    raise
            finally:
                if final: final()

        return __exceptional

    def _wild2regex(self, content: str):
        """Convert a Unix wildcard glob into a regular expression"""
        return content.replace('.', '\.').replace('*', '.*').replace('?', '.').replace('!', '^')

    def _type_check(self, tags):
        """Perform a type check on a list of tags"""

        if type(tags) in (list, tuple):
            single = False
        elif tags == None:
            tags = []
            single = False
        else:
            tags = [tags]
            single = True

        if len([t for t in tags if type(t) not in (str, bytes)]) == 0:
            valid = True
        else:
            valid = False

        return tags, single, valid

    def _quality_str(self, quality_bits):
        """Convert OPC quality bits to a descriptive string"""

        quality = (quality_bits >> 6) & 3
        return self.default_opc_quality[quality]

    def _connect(self, opc_server_list: list, opc_host: str='localhost'):
        #pythoncom.CoInitializeEx(pythoncom.COINIT_MULTITHREADED)
        for s in opc_server_list:
            try:
                self.opc_client.Connect(s, opc_host)
            except pythoncom.com_error as err:
                if len(opc_server_list) == 1:
                    raise Exception(f"Connect: {s} fail({self._get_error_str(err)})")

            self.opc_client.ClientName = self.opc_client_name
            self.opc_connected = True
            break

    #连接
    def connect(self, opc_server: Optional[str]=None, opc_host: str='localhost') -> bool:
        """Connect to the specified OPC server"""
        self.last_used = time.time()
        if self.opc_server == opc_server and self.opc_host == opc_host and self.opc_connected:
            return False
        else:
            if opc_server == None:
                if self.opc_server == None:
                    opc_server = os.environ.get('OPC_DA_SERVER', OPC_SERVER)
                else:
                    opc_server = self.opc_server
                    opc_host = self.opc_host

            opc_server_list = opc_server.split(';')
            self.opc_connected = False

            self._connect(opc_server_list, opc_host)

            if not self.opc_connected:
                raise Exception('Connect: Cannot connect to any of the servers in the OPC_SERVER list')

            # With some OPC servers, the next OPC call immediately after Connect() will occationally fail.  Sleeping for 1/100 second seems to fix this.
            time.sleep(0.01)

            self.opc_server = opc_server
            self.opc_host = opc_host

            # On reconnect we need to remove the old group names from OpenOPC's internal cache since they are now invalid
            self._reset()

            logging.info(f"connect opc({self.get_opc_info()}) success")
        return self.opc_connected

    def _reset(self):
        self.opc_groups = {}
        self.opc_group_tags = {}  # group: tag: clienid
        self.opc_group_hooks = {}  # 组事件
        self.opc_group_server_handles = {}  # 组ServerID
        self.opc_group_tag_values = {}  # 组ID值
        self.opc_group_transaction_id = {}  # 订阅ID对应组号
        self.opc_client_handle = 0
        self.opc_client_handle_value = {}  # handle: value

    def guid(self):
        return self.opc_open_guid

    def _disconnect(self):
        try:
            if self.opc_client:
                #pythoncom.CoInitializeEx(pythoncom.COINIT_MULTITHREADED)
                self.opc_client.Disconnect()
        except Exception as e:
            logging.error(f"close fail({e.__str__()})")

    def close(self, del_object: bool=True):
        """Close"""
        logging.info(f"close opc({self.get_opc_info()})")
        opc_connected = self.opc_connected
        try:
            self.opc_connected = False
            self.remove_groups(self.groups(), opc_connected)
            if opc_connected is True:
                self._disconnect()
        except pythoncom.com_error as err:
            raise Exception(f"Disconnect: {self._get_error_str(err)}")
        except Exception as e:
            logging.error(f"close fail({e.__str__()})")
        finally:
            # Remove this object from the open gateway service
            if self.opc_open_server and del_object:
                self.opc_open_server.release_client(self.opc_open)
                self.opc_open = None

    def groups(self) -> list:
        """Return a list of active tag groups"""
        self.last_used = time.time()
        return list(self.opc_groups.keys())

    def _remove_group(self, group_name: str):
        try:
            if self.opc_client:
                #pythoncom.CoInitializeEx(pythoncom.COINIT_MULTITHREADED)
                self.opc_client.OPCGroups.Remove(group_name)
        except pythoncom.com_error as err:
            raise Exception(f"Remove Group: {self._get_error_str(err)}")

    def remove_groups(self, groups: list, connect_status: bool = True):
        """Remove the specified tag group(s)"""
        try:
            for group in groups:
                if group in self.opc_groups.keys():
                    if connect_status is True:
                        self._remove_group(group)
                    del self.opc_groups[group]

                if group in self.opc_group_hooks.keys():
                    self.opc_group_hooks[group].close()

                if group in self.opc_group_tags.keys():
                    del self.opc_group_tags[group]

                if group in self.opc_group_server_handles.keys():
                    del self.opc_group_server_handles[group]
        except pythoncom.com_error as err:
            raise Exception(f'Remove Groups: {self._get_error_str(err)}')

    #
    def add_group(self, group_name: str, update_rate: int = 1000) -> bool:
        self.last_used = time.time()
        if group_name not in self.opc_groups.keys():
            try:
                #pythoncom.CoInitializeEx(pythoncom.COINIT_MULTITHREADED)
                opc_groups = self.opc_client.OPCGroups
                opc_group = opc_groups.Add(group_name)
                opc_group.IsSubscribed = 1
                opc_group.IsActive = 1
                opc_group.DeadBand = 0
                opc_group.UpdateRate = update_rate
                self.opc_groups[group_name] = opc_group
                group_event = win32com.client.WithEvents(opc_group, self.GroupEvents)
                group_event.set_client(self)
                self.opc_group_hooks[group_name] = group_event
            except pythoncom.com_error as err:
                raise Exception(f"Add Group: {self._get_error_str(err)}")
        return True

    #检测有效性
    def check_items(self, group_name: str, item_tags: list) -> list:
        if group_name in self.opc_groups.keys():
            opc_items = self.opc_groups[group_name].OPCItems
            item_tags.insert(0, 0)
            errors = []
            try:
                #pythoncom.CoInitializeEx(pythoncom.COINIT_MULTITHREADED)
                errors = opc_items.Validate(len(item_tags) - 1, item_tags)
            except pythoncom.com_error as err:
                raise Exception(f"Valid Items fail: {self._get_error_str(err)}")
            return errors
        raise Exception(f"Check Items fail")

    def _add_items(self, group_name: str, client_handles: list, valid_tags: list):
        if group_name in self.opc_groups.keys():
            opc_items = self.opc_groups[group_name].OPCItems
            try:
                #pythoncom.CoInitializeEx(pythoncom.COINIT_MULTITHREADED)
                client_handles.insert(0, 0)
                valid_tags.insert(0, 0)
                return opc_items.AddItems(len(client_handles) - 1, valid_tags, client_handles)
            except:
                pass
        return [], []

    def _check_item_exist(self, group_name: str, item_tag: str):
        if group_name in self.opc_group_tags.keys():
            if item_tag in self.opc_group_tags[group_name].keys():
                return True
        return False

    def add_items(self, group_name: str, item_tags: list):
        self.last_used = time.time()
        if group_name in self.opc_groups.keys():
            tags, single, valid = self._type_check(item_tags)
            if not valid:
                raise TypeError("iread(): 'tags' parameter must be a string or a list of strings")

            new_tags = []
            for item_tag in item_tags:
                if self._check_item_exist(group_name, item_tag) is False:
                    new_tags.append(item_tag)

            valid_tags = []
            client_handles = []
            error_msgs = {}

            if group_name not in self.opc_group_tags.keys():
                self.opc_group_tags[group_name] = {}

            if len(new_tags) > 0:
                errors = self.check_items(group_name, new_tags.copy())

                for i, item_tag in enumerate(new_tags):
                    if errors[i] == 0:
                        valid_tags.append(item_tag)
                        self.opc_client_handle = self.opc_client_handle + 1
                        self.opc_group_tags[group_name][item_tag] = self.opc_client_handle
                        client_handles.append(self.opc_client_handle)
                    else:
                        error_msgs[item_tag] = self.opc_client.GetErrorString(errors[i])

                if len(valid_tags) > 0:
                    server_handles, errors = self._add_items(group_name, client_handles.copy(), valid_tags.copy())
                    if len(server_handles) > 0:
                        valid_tags_tmp = []
                        server_handles_tmp = []

                        if group_name not in self.opc_group_server_handles.keys():
                            self.opc_group_server_handles[group_name] = {}

                        for i, tag in enumerate(valid_tags):
                            if errors[i] == 0:
                                valid_tags_tmp.append(tag)
                                server_handles_tmp.append(server_handles[i])
                                self.opc_group_server_handles[group_name][tag] = server_handles[i]
                            else:
                                error_msgs[tag] = self.opc_client.GetErrorString(errors[i])
                        return True if len(valid_tags_tmp) > 0 else False, valid_tags_tmp, error_msgs  #只要有一个点添加成功即为正确
                    return False, [], dict.fromkeys(item_tags, 'add item fail')   #添加点失败
                return False, [], error_msgs    #点都不正确
            return True, [], {}    #无需额外添加点
        return False, [], dict.fromkeys(item_tags, 'group not exist')    #组不存在

    def _remove_items(self, group_name: str, server_handles: list):
        if group_name in self.opc_groups.keys():
            #pythoncom.CoInitializeEx(pythoncom.COINIT_MULTITHREADED)
            opc_items = self.opc_groups[group_name].OPCItems
            try:
                return opc_items.AddItems(len(server_handles) - 1, server_handles)
            except pythoncom.com_error as err:
                raise Exception(f"Remove Items: {self._get_error_str(err)}")

    def remove_items(self, group_name: str, item_tags: list):
        self.last_used = time.time()
        if group_name in self.opc_groups.keys():
            tags, single, valid = self._type_check(item_tags)
            if not valid:
                raise TypeError("iread(): 'tags' parameter must be a string or a list of strings")

            new_tags = []
            for item_tag in item_tags:
                if self._check_item_exist(group_name, item_tag) is True:
                    new_tags.append(item_tag)

            if len(new_tags) > 0:
                server_handles = []

                for item_tag in new_tags:
                    if item_tag in self.opc_group_server_handles[group_name].keys():
                        server_handles.append(self.opc_group_server_handles[group_name][item_tag])

                if len(server_handles) > 0:
                    server_handles.insert(0, 0)
                    self._remove_items(group_name, server_handles)

                for item_tag in new_tags:
                    if item_tag in self.opc_group_server_handles[group_name].keys():
                        del self.opc_group_server_handles[group_name][item_tag]
                    if item_tag in self.opc_group_tags[group_name].keys():
                        del self.opc_group_tags[group_name][item_tag]

    def _update_client_value(self, client_handle: int, value, qualitie, timestamp, error, now_str):
        self.opc_client_handle_value[client_handle] = [value if type(value) != pywintypes.TimeType else str(value), self._quality_str(qualitie), str(timestamp), error, now_str]

    def _parse_value(self, group_name: str, item_tags: list, values: list, errors: list, qualities: list, timestamps: list):
        if group_name in self.opc_group_tags.keys():
            now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            for i, item_tag in enumerate(item_tags):
                if item_tag in self.opc_group_tags[group_name].keys():
                    client_handle = self.opc_group_tags[group_name][item_tag]
                    self._update_client_value(client_handle, values[i], qualities[i], timestamps[i], self.opc_client.GetErrorString(errors[i]) if errors[i] != 0 else '', now_str)

    def parse_data_change_value(self, action: str, transaction_id: int, item_num: int, client_handles: list, values: list, qualities: list, timestamps: list, errors: Optional[list] = None):
        #print(f"{action} {transaction_id} {item_num}")
        if action in ['OnDataChange', 'OnAsyncReadComplete']:
            now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            for i in range(item_num):
                error = ''
                if errors is not None and i < len(errors) and errors[i] != 0:
                    error = self.opc_client.GetErrorString(errors[i])
                self._update_client_value(client_handles[i], values[i], qualities[i], timestamps[i], error, now_str)
        if transaction_id == 0:
            self.opc_data_change = time.time()
        if transaction_id > 0:
            if transaction_id in self.opc_group_transaction_id.keys():
                self.opc_group_transaction_id[transaction_id].set() #激活事件

    def sync_read(self, group_name: str, data_source: int, server_handles: dict):
        if group_name in self.opc_groups.keys():
            opc_group = self.opc_groups[group_name]
            try:
                #pythoncom.CoInitializeEx(pythoncom.COINIT_MULTITHREADED)
                item_tags = list(server_handles.keys())
                server_handles_ = list(server_handles.values())
                server_handles_.insert(0,0)
                values, errors, qualities, timestamps = opc_group.SyncRead(data_source, len(server_handles_) - 1, server_handles_)
                self._parse_value(group_name, item_tags, values, errors, qualities, timestamps)
            except pythoncom.com_error as err:
                raise Exception(f"SyncRead: {self._get_error_str(err)}")
        else:
            raise Exception(f"SyncRead: group {group_name} not exist")

    def async_read(self, group_name: str, server_handles: dict):
        if group_name in self.opc_groups.keys():
            opc_group = self.opc_groups[group_name]
            try:
                #pythoncom.CoInitializeEx(pythoncom.COINIT_MULTITHREADED)
                self.opc_transaction_id = self.opc_transaction_id + 1
                event = Event()
                self.opc_group_transaction_id[self.opc_transaction_id] = event

                server_handles_ = list(server_handles.values())
                server_handles_.insert(0, 0)
                opc_group.AsyncRead(len(server_handles_) - 1, server_handles_, pythoncom.Missing, self.opc_transaction_id)
                if not event.wait(self.opc_async_timeout):
                    raise Exception(f"AsyncRead: Timeout")
            except pythoncom.com_error as err:
                raise Exception(f"AsyncRead: {self._get_error_str(err)}")
            finally:
                del self.opc_group_transaction_id[self.opc_transaction_id]
        else:
            raise Exception(f"AsyncRead: group {group_name} not exist")

    def async_refresh(self, group_name: str, data_source: int):
        if group_name in self.opc_groups.keys():
            opc_group = self.opc_groups[group_name]
            try:
                #pythoncom.CoInitializeEx(pythoncom.COINIT_MULTITHREADED)
                self.opc_transaction_id = self.opc_transaction_id + 1
                event = Event()
                self.opc_group_transaction_id[self.opc_transaction_id] = event
                opc_group.AsyncRefresh(data_source, self.opc_transaction_id)
                if not event.wait(self.opc_async_timeout):
                    raise Exception(f"AsyncRefresh: Timeout")
            except pythoncom.com_error as err:
                raise Exception(f"AsyncRefresh: {self._get_error_str(err)}")
            finally:
                del self.opc_group_transaction_id[self.opc_transaction_id]
        else:
            raise Exception(f"AsyncRefresh: group {group_name} not exist")

    def _read(self, group_name: str, item_tags: list = [], action: str = '', source: str = 'cache') -> dict:
        results = {}
        if group_name in self.opc_groups.keys():
            if action == '':    #订阅变化数据
                pass
            elif action in ['sync', 'async']:    #sync同步读取
                data_source = self.default_data_source_cache if source =='cache' else self.default_data_source_device
                server_handles = {}
                for item_tag in item_tags:
                    if item_tag in self.opc_group_server_handles[group_name].keys():
                        server_handles[item_tag] = self.opc_group_server_handles[group_name][item_tag]
                if len(server_handles) > 0:
                    if action == 'sync':
                        self.sync_read(group_name, data_source, server_handles)
                    elif action == 'async':
                        self.async_read(group_name, server_handles)
            elif action == 'refresh':    #async异步读取
                data_source = self.default_data_source_cache if source == 'cache' else self.default_data_source_device
                self.async_refresh(group_name, data_source)

            #返回值
            for item_tag in item_tags:
                if item_tag in self.opc_group_tags[group_name].keys():
                    client_handle = self.opc_group_tags[group_name][item_tag]
                    if client_handle in self.opc_client_handle_value.keys():
                        results[item_tag] = self.opc_client_handle_value[client_handle]
        return results

    def read(self, group_name: str, item_tags: Optional[list] = [], action: str = '', source: str = 'cache', size: int = 100, interval: float = 0.1) -> dict:
        self.last_used = time.time()
        results = {}
        if self.opc_connected is True:
            if len(item_tags) > 0:
                result, success, errors = self.add_items(group_name, item_tags)
                if len(errors) > 0:
                    results.update(errors)
                if len(success) > 0:
                    action = 'sync'

            valid_item_tags = []
            if len(item_tags) > 0:
                for item_tag in item_tags:
                    if self._check_item_exist(group_name, item_tag) is True:
                        valid_item_tags.append(item_tag)
            else:
                if group_name in self.opc_group_tags.keys():
                    for item_tag in self.opc_group_tags[group_name].keys():
                        valid_item_tags.append(item_tag)

            #
            if action == 'refresh':    #async异步刷新
                results.update(self._read(group_name, valid_item_tags, action, source))
            else:
                item_tags_groups = self.split_to_list(valid_item_tags, size)
                for item_tags in item_tags_groups:
                    results.update(self._read(group_name, item_tags, action, source))
                    time.sleep(interval)
        else:
            raise Exception(f"{self.opc_server} not connected")
        return results

    def split_to_list(self, values, size: int):
        if isinstance(values, dict):
            results = [{}]
            for k, v in values.items():
                if len(results[-1]) >= size:
                    results.append({k: v})
                else:
                    results[-1][k] = v
            return results
        elif isinstance(values, list):
            return [values[i:i + size] for i in range(0, len(values), size)]
        return values

    def sync_write(self, group_name: str, server_handles: list, item_values: list, item_tags: list):
        results = {}
        if group_name in self.opc_groups.keys():
            opc_group = self.opc_groups[group_name]
            try:
                #pythoncom.CoInitializeEx(pythoncom.COINIT_MULTITHREADED)
                server_handles.insert(0, 0)
                item_values.insert(0, 0)
                errors = opc_group.SyncWrite(len(server_handles) - 1, server_handles, item_values)
                for i, item_tag in enumerate(item_tags):
                    if errors[i] == 0:
                        results[item_tag] = True
                    else:
                        results[item_tag] = False
            except pythoncom.com_error as err:
                raise Exception(f'SyncWrite: {self._get_error_str(err)}')
        else:
            for item_tag in item_tags:
                results[item_tag] = False
        return results

    def async_write(self, group_name: str, server_handles: list, item_values: list, item_tags: list):
        results = {}
        if group_name in self.opc_groups.keys():
            opc_group = self.opc_groups[group_name]
            try:
                server_handles.insert(0, 0)
                item_values.insert(0, 0)
                self.opc_transaction_id = self.opc_transaction_id + 1
                event = Event()
                self.opc_group_transaction_id[self.opc_transaction_id] = event
                #pythoncom.CoInitializeEx(pythoncom.COINIT_MULTITHREADED)
                opc_group.AsyncWrite(len(server_handles) - 1, server_handles, item_values, pythoncom.Missing, self.opc_transaction_id)
                for item_tag in item_tags:
                    results[item_tag] = True
                if not event.wait(self.opc_async_timeout):
                    raise Exception(f"AsyncWrite: Timeout")
            except pythoncom.com_error as err:
                raise Exception(f'AsyncWrite: {self._get_error_str(err)}')
            finally:
                del self.opc_group_transaction_id[self.opc_transaction_id]
        else:
            for item_tag in item_tags:
                results[item_tag] = False

    def _write(self, group_name: str, items_values: dict, action: str = 'sync'):
        results = {}
        if group_name in self.opc_groups.keys():
            if action in ['sync', 'async']:  # sync同步读取
                server_handles = []
                item_tags = []
                values = []
                for item_tag in items_values.keys():
                    if item_tag in self.opc_group_server_handles[group_name].keys():
                        item_tags.append(item_tag)
                        server_handles.append(self.opc_group_server_handles[group_name][item_tag])
                        values.append(items_values[item_tag])

                if len(server_handles) > 0:
                    if action == 'sync':
                        results.update(self.sync_write(group_name, server_handles.copy(), values.copy(), item_tags.copy()))
                    elif action == 'async':
                        results.update(self.async_write(group_name, server_handles.copy(), values.copy(), item_tags.copy()))
        return results

    def write(self, group_name: str, items_values: dict, action: str = 'sync', size: int = 100, interval: float = 0.1) -> dict:
        self.last_used = time.time()
        results = {}
        if self.opc_connected is True:
            if len(items_values) > 0:
                result, success, errors = self.add_items(group_name, list(items_values.keys()))
                if len(errors) > 0:
                    results.update(dict.fromkeys(list(errors.keys), False))
                if len(success) > 0:
                    action = 'sync'

            valid_item_values = {}
            if len(items_values) > 0:
                for item_tag in items_values.keys():
                    if self._check_item_exist(group_name, item_tag) is True:
                        valid_item_values[item_tag] = items_values[item_tag]
                    else:
                        results[item_tag] = False
            #
            item_tags_values = self.split_to_list(valid_item_values, size)
            for item_tags_value in item_tags_values:
                results.update(self._write(group_name, item_tags_value, action))
                time.sleep(interval)
        else:
            raise Exception(f"{self.opc_server} not connected")
        return results

    def _properties(self, tags: list, id=None):
        """Iterable version of properties()"""
        try:
            #pythoncom.CoInitializeEx(pythoncom.COINIT_MULTITHREADED)

            tags, single_tag, valid = self._type_check(tags)
            if not valid:
                raise TypeError("properties(): 'tags' parameter must be a string or a list of strings")

            try:
                id.remove(0)
                include_name = True
            except:
                include_name = False

            if id != None:
                descriptions = []

                if isinstance(id, list) or isinstance(id, tuple):
                    property_id = list(id)
                    single_property = False
                else:
                    property_id = [id]
                    single_property = True

                for i in property_id:
                    descriptions.append('Property id %d' % i)
            else:
                single_property = False

            for tag in tags:

                if id == None:
                    count, property_id, descriptions, datatypes = self.opc_client.QueryAvailableProperties(tag)

                    # Remove bogus negative property id (not sure why this sometimes happens)
                    tag_properties = list(map(lambda x, y: (x, y), property_id, descriptions))
                    property_id = [p for p, d in tag_properties if p > 0]
                    descriptions = [d for p, d in tag_properties if p > 0]

                property_id.insert(0, 0)
                values, errors = self.opc_client.GetItemProperties(tag, len(property_id) - 1, property_id)

                property_id.pop(0)
                values = [str(v) if type(v) == pywintypes.TimeType else v for v in values]

                # Replace variant id with type strings
                try:
                    i = property_id.index(1)
                    values[i] = vt[values[i]]
                except:
                    pass

                # Replace quality bits with quality strings
                try:
                    i = property_id.index(3)
                    values[i] = self._quality_str(values[i])
                except:
                    pass

                # Replace access rights bits with strings
                try:
                    i = property_id.index(5)
                    values[i] = self.default_access_rights[values[i]]
                except:
                    pass

                if id != None:
                    if single_property:
                        if single_tag:
                            tag_properties = values
                        else:
                            tag_properties = [values]
                    else:
                        tag_properties = list(map(lambda x, y: (x, y), property_id, values))
                else:
                    tag_properties = list(map(lambda x, y, z: (x, y, z), property_id, descriptions, values))
                    tag_properties.insert(0, (0, 'Item ID (virtual property)', tag))

                if include_name:    tag_properties.insert(0, (0, tag))
                if not single_tag:  tag_properties = [tuple([tag] + list(p)) for p in tag_properties]

                for p in tag_properties: yield p

        except pythoncom.com_error as err:
            raise Exception(f"properties: {self._get_error_str(err)}")

    def properties(self, tags: list, id=None):
        """Return list of property tuples (id, name, value) for the specified tag(s) """
        self.last_used = time.time()
        props = self._properties(tags, id)

        return list(props)

    def _list_items(self, paths: str = '*', recursive: bool = False, flat: bool = False, include_type: bool = False):
        """Iterable version of list()"""
        try:

            #pythoncom.CoInitializeEx(pythoncom.COINIT_MULTITHREADED)

            try:
                browser = self.opc_client.CreateBrowser()
            # For OPC servers that don't support browsing
            except:
                return

            paths, single, valid = self._type_check(paths)
            if not valid:
                raise TypeError("list(): 'paths' parameter must be a string or a list of strings")

            if len(paths) == 0: paths = ['*']
            nodes = {}
            for path in paths:
                if flat:
                    browser.MoveToRoot()
                    browser.Filter = ''
                    browser.ShowLeafs(True)
                    pattern = re.compile('^%s$' % self._wild2regex(path), re.IGNORECASE)
                    matches = filter(pattern.search, browser)
                    if include_type:  matches = [(x, node_type) for x in matches]
                    for node in matches: yield node
                    continue

                queue = []
                queue.append(path)

                while len(queue) > 0:
                    tag = queue.pop(0)

                    browser.MoveToRoot()
                    browser.Filter = ''
                    pattern = None

                    path_str = '/'
                    path_list = tag.replace('.', '/').split('/')
                    path_list = [p for p in path_list if len(p) > 0]
                    found_filter = False
                    path_postfix = '/'

                    for i, p in enumerate(path_list):
                        if found_filter:
                            path_postfix += p + '/'
                        elif p.find('*') >= 0:
                            pattern = re.compile('^%s$' % self._wild2regex(p), re.IGNORECASE)
                            found_filter = True
                        elif len(p) != 0:
                            pattern = re.compile('^.*$')
                            browser.ShowBranches()

                            # Branch node, so move down
                            if len(browser) > 0:
                                try:
                                    browser.MoveDown(p)
                                    path_str += p + '/'
                                except:
                                    if i < len(path_list) - 1: return
                                    pattern = re.compile('^%s$' % self._wild2regex(p), re.IGNORECASE)

                            # Leaf node, so append all remaining path parts together
                            # to form a single search expression
                            else:
                                p =  '.'.join(path_list[i:])
                                pattern = re.compile('^%s$' % self._wild2regex(p), re.IGNORECASE)
                                break

                    browser.ShowBranches()

                    if len(browser) == 0:
                        browser.ShowLeafs(False)
                        lowest_level = True
                        node_type = 'Leaf'
                    else:
                        lowest_level = False
                        node_type = 'Branch'

                    matches = filter(pattern.search, browser)

                    if not lowest_level and recursive:
                        queue += [path_str + x + path_postfix for x in matches]
                    else:
                        if lowest_level:  matches = [self._exceptional(browser.GetItemID, x)(x) for x in matches]
                        if include_type:  matches = [(x, node_type) for x in matches]
                        for node in matches:
                            if not node in nodes: yield node
                            nodes[node] = True

        except pythoncom.com_error as err:
            raise Exception(f"list: {self._get_error_str(err)}")

    def list_items(self, paths: str = '*', recursive: bool = False, flat: bool = False, include_type: bool = False):
        """Return list of item nodes at specified path(s) (tree browser)"""
        self.last_used = time.time()
        nodes = self._list_items(paths, recursive, flat, include_type)
        return list(nodes)

    def servers(self, opc_host='localhost'):
        """Return list of available OPC servers"""
        self.last_used = time.time()
        try:
            #pythoncom.CoInitializeEx(pythoncom.COINIT_MULTITHREADED)
            servers = self.opc_client.GetOPCServers(opc_host)
            servers = [s for s in servers if s != None]
            return servers
        except pythoncom.com_error as err:
            raise Exception(f"servers: {self._get_error_str(err)}")

    def info(self):
        """Return list of (name, value) pairs about the OPC server"""
        self.last_used = time.time()
        try:
            #pythoncom.CoInitializeEx(pythoncom.COINIT_MULTITHREADED)

            info_list = []

            if self.opc_open_server:
                mode = 'OpenOPC'
            else:
                mode = 'DCOM'

            info_list += [('Protocol', mode)]

            if mode == 'OpenOPC':
                info_list += [('Gateway Host', '%s:%s' % (self.opc_host, self.opc_port))]
                info_list += [('Gateway Version', '1.2.0')]
            info_list += [('Class', self.opc_class)]
            info_list += [('Client Name', self.opc_client.ClientName)]
            info_list += [('OPC Host', self.opc_host)]
            info_list += [('OPC Server', self.opc_client.ServerName)]
            info_list += [('State', self.default_opc_status[self.opc_client.ServerState])]
            info_list += [('Version', '%d.%d (Build %d)' % (self.opc_client.MajorVersion, self.opc_client.MinorVersion, self.opc_client.BuildNumber))]

            try:
                browser = self.opc_client.CreateBrowser()
                browser_type = self.default_browser_type[browser.Organization]
            except:
                browser_type = 'Not Supported'

            info_list += [('Browser', browser_type)]
            info_list += [('Start Time', str(self.opc_client.StartTime))]
            info_list += [('Current Time', str(self.opc_client.CurrentTime))]
            info_list += [('Vendor', self.opc_client.VendorInfo)]

            return info_list

        except pythoncom.com_error as err:
            raise Exception(f"info: {self._get_error_str(err)}")

    def ping(self):
        """Check if we are still talking to the OPC server"""
        self.last_used = time.time()
        try:
            # Convert OPC server time to milliseconds
            if self.opc_connected is True:
                opc_serv_time = self.opc_client.CurrentTime
                if opc_serv_time == self.opc_prev_serv_time:
                    return False
                else:
                    self.opc_prev_serv_time = opc_serv_time
                    return True
        except pythoncom.com_error:
            pass
        return False

    def _get_error_str(self, err):
        """Return the error string for a OPC or COM error code"""

        hr, msg, exc, arg = err.args

        if exc == None:
            error_str = str(msg)
        else:
            scode = exc[5]

            try:
                opc_err_str = str(self.opc_client.GetErrorString(scode)).strip('\r\n')
            except:
                opc_err_str = None

            try:
                com_err_str = str(pythoncom.GetScodeString(scode)).strip('\r\n')
            except:
                com_err_str = None

            # OPC error codes and COM error codes are overlapping concepts,
            # so we combine them together into a single error message.

            if opc_err_str == None and com_err_str == None:
                error_str = str(scode)
            elif opc_err_str == com_err_str:
                error_str = opc_err_str
            elif opc_err_str == None:
                error_str = com_err_str
            elif com_err_str == None:
                error_str = opc_err_str
            else:
                error_str = '%s (%s)' % (opc_err_str, com_err_str)

        return error_str

#OPCDA Point
class OPCDAPoint(BasePoint):

    def __init__(self, point_writable: bool, point_name: str, point_tag: str, point_type: str, point_description: str=''):
        super().__init__('opcda', point_writable, point_name, point_description)
        self.point_tag = point_tag
        self.point_type = point_type
        self.point_description = point_description

    @property
    def get_point_tag(self):
        return self.point_tag

    @property
    def get_point_type(self):
        return self.point_type

    @property
    def get_point_description(self):
        return self.point_description

class OPCDAEngine(Thread):

    def __init__(self, server: str, host: str, action: str, group: str, read_limit: int, update_rate: int, point_dict: dict, call_back_func=None):
        Thread.__init__(self)

        #param#########
        self.server = server
        self.host = host
        self.group = group
        self.action = action

        self.read_limit = read_limit
        self.update_rate = update_rate
        self.point_dict = point_dict
        self.call_back_func = call_back_func
        ##############

        self.opcda_client = None
        self.opcda_ip: str = ''
        self.opcda_port: int = OPC_PORT
        self.opcda_com: bool = True
        self.opcda_thread_exit = False

        self.point_tags: dict = {}
        self.add_group: bool = False

        for point_name in self.point_dict.keys():
            point_tag = self.point_dict[point_name].get_point_tag
            if point_tag not in self.point_tags.keys():
                self.point_tags[point_tag] = []
            if point_name not in self.point_tags[point_tag]:
                self.point_tags[point_tag].append(point_name)

    def __del__(self):
        try:
            self.exit()
        except Exception as e:
            raise e

    def exit(self):
        try:
            self.opcda_thread_exit = True
            self.close_opcda_client(self.opcda_client)
        except Exception as e:
            raise e

    def reset(self):
        self.opcda_client = None
        self.add_group = False

    def get_opcda_client(self, auto_connect: bool = True):
        if self.opcda_client == None:
            if len(self.host) > 0:
                host_info = self.host.split(':')
                if len(host_info) == 1:
                    self.opcda_ip = host_info[0]
                    self.opcda_com = True
                elif len(host_info) == 2:
                    self.opcda_ip = host_info[0]
                    self.opcda_port = int(float(host_info[1]))
                    self.opcda_com = False

                opcda_client = None
                try:
                    if self.opcda_com is True:
                        opcda_client = OPCClient()
                    else:
                        opcda_client = open_client(self.opcda_ip, self.opcda_port)
                except Exception as e:
                    self.close_opcda_client(opcda_client)
                    raise e
                self.opcda_client = opcda_client

        if self.opcda_client is not None:
            if auto_connect is True:
                try:
                    if self.opcda_client.connect(self.server, self.opcda_ip) is True:   #重连
                        self.add_group = False
                except Exception as e:
                    self.close_opcda_client(self.opcda_client)
                    raise e
        return self.opcda_client

    def close_opcda_client(self, opcda_client):
        try:
            if opcda_client:
                opcda_client.close()
            opcda_client = None
        except Exception as e:
            print(f'ERROR: close_opcda_client({e.__str__()})')
        self.reset()

    def run(self):
        while self.opcda_thread_exit is False:
            if self.opcda_client is not None and self.opcda_client.is_connected() is True:
                pythoncom.PumpWaitingMessages()
                continue
            time.sleep(0.1)

    #
    def update_values(self, values: dict, point_tags: dict):
        result_success = {}
        result_error = {}
        if len(values) > 0:
            for tag, value in values.items():
                if isinstance(value, list):
                    if len(value) >= 4:
                        (v, status, time, error, update) = value
                        names = point_tags.get(tag, [])
                        for name in names:
                            if status == 'Good':
                                result_success[name] = v
                            else:
                                result_error[name] = f"[{status}] {error}"
                else:
                    result_error[tag] = str(value)
        return result_success, result_error

    def add_opcda_group(self):
        if self.get_opcda_client():
            if self.add_group is False:
                self.add_group = self.opcda_client.add_group(self.group, self.update_rate)
        return self.add_group

    def read_values(self, dict_point):
        result_dict = {}
        result_error = {}
        try:
            if self.add_opcda_group() is True:
                point_tags: dict = {}
                for point_name in dict_point.keys():
                    point_tag = dict_point[point_name].get_point_tag
                    if point_tag not in point_tags.keys():
                        point_tags[point_tag] = []
                    if point_name not in point_tags[point_tag]:
                        point_tags[point_tag].append(point_name)

                    if len(point_tags) >= self.read_limit:
                        values = self.opcda_client.read(self.group, list(point_tags.keys()), self.action)
                        result_success, result_error = self.update_values(values, point_tags)
                        result_dict.update(result_success)
                        result_error.update(result_error)
                        point_tags = {}
                        time.sleep(0.1)

                if len(point_tags) >0:
                    values = self.opcda_client.read(self.group, list(point_tags.keys()), self.action)
                    result_success, result_error = self.update_values(values, point_tags)
                    result_dict.update(result_success)
                    result_error.update(result_error)
        except Exception as e:
            raise e
        return result_dict, result_error

    def scrap_value(self):
        result_dict = {}
        result_error = {}
        try:
            if self.add_opcda_group() is True:
                if self.add_group is True:
                    result_dict, result_error = self.read_values(self.point_dict)
        except Exception as e:
            raise e
        return result_dict, result_error

    def write_values(self, dict_point):
        result_dict = {}
        try:
            if self.add_opcda_group() is True:
                set_values = {}
                point_tags: dict = {}
                for point_name, point_value in dict_point.items():
                    if point_name in self.point_dict.keys():
                        point_tag = self.point_dict[point_name].get_point_tag
                        if point_tag not in point_tags.keys():
                            point_tags[point_tag] = []
                        if point_name not in point_tags[point_tag]:
                            point_tags[point_tag].append(point_name)
                        set_values[point_tag] = point_value

                if len(set_values) > 0:
                    values = self.opcda_client.write(self.group, set_values)
                    for tag, status in values.items():
                        names = point_tags.get(tag, [])
                        for name in names:
                            result_dict[name] = status
        except Exception as e:
            raise e
        return result_dict

    #search###
    def search_servers(self):
        servers = []
        try:
            if self.get_opcda_client(False):
                servers = self.opcda_client.servers()
        except Exception as e:
            raise e
        return servers

    def search_points(self, path: str='*', include_property: bool=False):
        search_point = {}
        try:
            if self.get_opcda_client():
                points = self.opcda_client.list_items(paths=path, flat=True) #flat=True
                for point in points:
                    search_point[point] = {'point_writable': True, 'point_name': point, 'point_tag': point, 'point_type': '', 'point_description': '', 'point_value': ''}
                    if include_property is True:
                        properties = self.opcda_client.properties(tags=[point])
                        for property in properties:
                            if len(property) >= 3:
                                if property[2] == 'Item Canonical DataType':
                                    search_point[point]['point_type'] = str(property[3])
                                elif property[2] == 'Item Value':
                                    search_point[point]['point_value'] = str(property[3])
                                elif property[2] == 'Item Description':
                                    search_point[point]['point_description'] = property[3]

        except Exception as e:
            raise e
        return search_point

    def ping_target(self):
        if self.get_opcda_client():
            return self.opcda_client.ping()
        return False

#OPCDA Driver
class OPCDADriver(BaseDriver):

    def __init__(self, dict_config: dict, dict_point: PointTableDict):
        super().__init__(dict_config, dict_point)

        self.dict_opcda_point = {}
        self.opcda_engine = None

        self.configure()

    def __del__(self):
        super().__del__()

    def configure(self):
        try:
            #config
            self.opcda_server = str(self.dict_config.get("server", ''))
            self.opcda_host = str(self.dict_config.get("host", 'localhost'))
            self.opcda_group = str(self.dict_config.get("group", 'opcda'))
            self.opcda_action = str(self.dict_config.get("action", ''))
            self.enable = str(self.dict_config.get("enabled", "true")).lower() == 'true'  # enable

            self.opcda_read_limit = self.dict_config.get('read_limit', 1000)
            self.opcda_update_rate = self.dict_config.get('update_rate', 500)

            #csv
            for point_name in self.dict_point.keys():
                self.dict_opcda_point[point_name] = OPCDAPoint(bool(str(self.dict_point[point_name]['point_writable'])), str(self.dict_point[point_name]['point_name']), str(self.dict_point[point_name]['point_tag']), str(self.dict_point[point_name]['point_type']), str(self.dict_point[point_name]['point_description']))

            #create_engine
            close_delay = 2
            self.exit()

            self.opcda_engine = OPCDAEngine(self.opcda_server, self.opcda_host, self.opcda_action, self.opcda_group, self.opcda_read_limit, self.opcda_update_rate, self.dict_opcda_point)
            self.opcda_engine.start()

            time.sleep(close_delay)  # delay on closed socket(This prevents a fast reconnect by the client)
        except Exception as e:
            raise e

    def exit(self):
        if self.opcda_engine != None:
            self.opcda_engine.exit()
            del self.opcda_engine
            self.opcda_engine = None

    # ping
    def ping_target(self):
        try:
            if self.opcda_engine:
                return self.opcda_engine.ping_target()
        except Exception as e:
            print(e.__str__())
        return False

    def get_points(self, dict_point: dict = {}) -> tuple:
        try:
            if len(dict_point) == 0:
                return self._scrap_points()
            else:
                return self._get_points(dict_point)
        except Exception as e:
            raise e

    def _get_points(self, dict_point: dict) -> tuple:
        result_success = {}
        result_error = {}
        try:
            opcda_point_dict = {}
            for point_name in dict_point.keys():
                if point_name in self.dict_opcda_point.keys():
                    opcda_point_dict[point_name] = self.dict_opcda_point[point_name]
                else:
                    result_error[point_name] = 'not exist'
            if len(opcda_point_dict) > 0 and self.opcda_engine:
                result_success, _result_error = self.opcda_engine.read_values(opcda_point_dict)
                if len(_result_error) > 0:
                    result_error.update(_result_error)
        except Exception as e:
            raise e
        return result_success, result_error

    def _scrap_points(self) -> tuple:
        result_success = {}
        result_error = {}
        try:
            if self.opcda_engine:
                result_success, result_error = self.opcda_engine.scrap_value()
        except Exception as e:
            raise e
        return result_success, result_error

    # set
    def set_points(self, dict_point: dict) -> dict:
        result_dict = {}
        try:
            opcda_point_dict = {}
            for point_name in dict_point.keys():
                if point_name in self.dict_opcda_point.keys():
                    opcda_point_dict[point_name] = dict_point[point_name]
                else:
                    result_dict[point_name] = False

            if len(opcda_point_dict) > 0 and self.opcda_engine:
                result_dict.update(self.opcda_engine.write_values(opcda_point_dict))
        except Exception as e:
            raise e
        return result_dict

    def reset_config(self, dict_config: dict):
        super().reset_config(dict_config)
        self.configure()

    def reset_point(self, dict_point: dict):
        super().reset_point(dict_point)
        self.configure()

    def search_points(self, path: str='*', include_property: bool=False) -> dict:
        search_point = {}
        try:
            search_point = self.opcda_engine.search_points(path, include_property)
        except Exception as e:
            raise e
        return search_point

    def search_servers(self):
        return self.opcda_engine.search_servers()

    ###########