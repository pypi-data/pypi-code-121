import time
from threading import Thread
from .base import BasePoint, BaseDriver, PointTableDict

import OpenOPC
import platform

'''
https://github.com/joseamaita/openopc120/blob/master/README.md
pip install OpenOPC-Python3x==1.3.1
步骤：
    1： 安转 python-3.6.5.exe（32位）
    2： 安转对应python版本的pywin32 pywin32-223.win32-py3.6.exe
    3:  安转Pyro4 pip install Pyro4
    4： 下载压缩包 https://github.com/joseamaita/openopc120
    5： 解压并注册 C:\OpenOPC34\lib>regsvr32 gbda_aut.dll     #invalid class
    6:  安转OpenOPC库 https://pypi.org/simple/openopc-python3x/ 到对应目录下安转 easy_install *.egg
    7： 安装服务 python OpenOPCService.py install
    8： 启动服务net start zzzOpenOPCService
    9： 修改OpenOPC.py文件
    10：OpenOPC.py 第574行修改 if include_error and tag not in error_msgs:
    
    pip install OpenOPC-Python3x
    安转 OPenOPCService服务：
    1： 打包OPenOPCService.py   pyinstaller -F --hidden-import=win32timezone --hidden-import=json --hidden-import=Pyro4 OPenOPCService.py
    2:  安装服务  OPenOPCService.exe install
    3： 启动服务  OPenOPCService.exe start
    4:  将OPCServerName 填入环境变量中的OPC_SERVER中， OPC_GATE_HOST 改成本机IP

替换queue  将multiprocessing导入的Queue换成queue模块导入的Queue
src/OpenOPC.py
@@ -16,7 +16,7 @@
 import socket
 import re
 import Pyro4.core
-from multiprocessing import Queue
+from queue import Queue
 
 __version__ = '1.2.0'

替换map 为zip   change map() to zip() in opc.properties and make it can return the co…
src/OpenOPC.py
@@ -933,7 +933,7 @@ def iproperties(self, tags, id=None):
                count, property_id, descriptions, datatypes = self._opc.QueryAvailableProperties(tag)

                # Remove bogus negative property id (not sure why this sometimes happens)
-               tag_properties = map(None, property_id, descriptions)
+               tag_properties = list(zip(property_id, descriptions))
                property_id = [p for p, d in tag_properties if p > 0]
                descriptions = [d for p, d in tag_properties if p > 0]

@@ -973,9 +973,9 @@ def iproperties(self, tags, id=None):
                   else:
                      tag_properties = [values]
                else:
-                  tag_properties = map(None, property_id, values)
+                  tag_properties = list(zip(property_id, values))
             else:
-               tag_properties = map(None, property_id, descriptions, values)
+               tag_properties = list(zip(property_id, descriptions, values))
                tag_properties.insert(0, (0, 'Item ID (virtual property)', tag))

             if include_name:    tag_properties.insert(0, (0, tag))
             
Due to picklingError with datetime
import pywintypes
pywintypes.datetime = pywintypes.TimeType
'''

'''
    安装OpenOPC-1.3.1.win32-py2.7.exe
    兼容旧项目
    OPCTag,OPC类型，OPC服务名，倍率，OPC组名, OPC地址（IP IP:端口）,OPC连接号

'''

if platform.system().lower() == 'windows':
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

    def __init__(self, server: str, host: str, group: str, read_limit: int, update_rate: int, point_dict: dict, call_back_func=None):
        Thread.__init__(self)

        #param#########
        self.server = server
        self.host = host
        self.group = group

        self.read_limit = read_limit
        self.update_rate = update_rate
        self.point_dict = point_dict
        self.call_back_func = call_back_func
        ##############

        self.opcda_client = None
        self.opcda_ip: str = ''
        self.opcda_port: int = 6677
        self.opcda_com: bool = True

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
            self.close_opcda_client()
        except Exception as e:
            raise e

    def reset(self):
        self.opcda_client = None

    def get_opcda_client(self):
        try:
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

                    if self.opcda_com is True:
                        self.opcda_client = OpenOPC.client()
                        self.opcda_client.connect(self.server, self.opcda_ip)
                    else:
                        self.opcda_client = OpenOPC.open_client(self.opcda_ip, self.opcda_port)
                        self.opcda_client.connect(self.server)
        except Exception as e:
            raise e
        return self.opcda_client

    def close_opcda_client(self):
        try:
            if self.opcda_client:
                self.opcda_client.remove(self.opcda_client.groups())
                self.opcda_client.close()
        except Exception as e:
            print('ERROR: close_opcda_client(%s)' % e.__str__())
        self.reset()

    def run(self):
        pass

    #
    def update_values(self, values: list, point_tags: dict):
        result_success = {}
        result_error = {}
        if len(values) > 0:
            for value in values:
                if len(value) >= 4:
                    (tag, value, status, time) = value
                    names = point_tags.get(tag, [])
                    for name in names:
                        if status == 'Good':
                            result_success[name] = value
                        else:
                            result_error[name] = value
        return result_success, result_error

    def read_values(self, dict_point):
        result_dict = {}
        try:
            if self.get_opcda_client():
                point_tags: dict = {}
                for point_name in dict_point.keys():
                    point_tag = dict_point[point_name].get_point_tag
                    if point_tag not in point_tags.keys():
                        point_tags[point_tag] = []
                    if point_name not in point_tags[point_tag]:
                        point_tags[point_tag].append(point_name)
                    if len(point_tags) >= self.read_limit:
                        values = self.opcda_client.read(list(point_tags.keys()), group=self.group, update=self.update_rate)
                        result_success, result_error = self.update_values(values, point_tags)
                        result_dict.update(result_success)
                        point_tags = {}

                if len(point_tags) >0:
                    values = self.opcda_client.read(list(point_tags.keys()), group=self.group)
                    result_success, result_error = self.update_values(values, point_tags)
                    result_dict.update(result_success)
        except Exception as e:
            raise e
        return result_dict

    def scrap_value(self):
        result_dict = {}
        try:
            if self.get_opcda_client():
                if self.add_group is False:
                    result_dict = self.read_values(self.point_dict)
                    self.add_group = True
                else:
                    values = self.opcda_client.read(group=self.group)
                    result_success, result_error = self.update_values(values, self.point_tags)
                    result_dict.update(result_success)
        except Exception as e:
            raise e
        return result_dict

    def write_values(self, dict_point):
        result_dict = {}
        try:
            if self.get_opcda_client():
                set_values = []
                point_tags: dict = {}
                for point_name, point_value in dict_point.items():
                    if point_name in self.point_dict.keys():
                        point_tag = self.point_dict[point_name].get_point_tag
                        if point_tag not in point_tags.keys():
                            point_tags[point_tag] = []
                        if point_name not in point_tags[point_tag]:
                            point_tags[point_tag].append(point_name)
                        set_values.append((point_tag, point_value))

                if len(set_values) > 0:
                    values = self.opcda_client.write(set_values)
                    for tag, status in values:
                        names = point_tags.get(tag, [])
                        for name in names:
                            if status == 'Success':
                                result_dict[name] = True
        except Exception as e:
            raise e
        return result_dict

    #search###
    def search_servers(self):
        servers = []
        try:
            if self.get_opcda_client():
                servers = self.opcda_client.servers()
        except Exception as e:
            raise e
        return servers

    def change_type(self, type: int):
        try:
            return vt[type]
        except:
            pass
        return type

    def search_points(self, path: str='*', include_property: bool=False):
        search_point = {}
        try:
            if self.get_opcda_client():
                points = self.opcda_client.list(paths=path, recursive=True) #flat=True
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

            self.opcda_read_limit = self.dict_config.get('read_limit', 1000)
            self.opcda_update_rate = self.dict_config.get('update_rate', 500)

            #csv
            for point_name in self.dict_point.keys():
                self.dict_opcda_point[point_name] = OPCDAPoint(bool(str(self.dict_point[point_name]['point_writable'])), str(self.dict_point[point_name]['point_name']), str(self.dict_point[point_name]['point_tag']), str(self.dict_point[point_name]['point_type']), str(self.dict_point[point_name]['point_description']))

            #create_engine
            close_delay = 0
            if self.opcda_engine != None:
                self.opcda_engine.exit()
                del self.opcda_engine
                self.opcda_engine = None
                close_delay = 2

            self.opcda_engine = OPCDAEngine(self.opcda_server, self.opcda_host, self.opcda_group, self.opcda_read_limit, self.opcda_update_rate, self.dict_opcda_point)
            self.opcda_engine.start()

            time.sleep(close_delay)  # delay on closed socket(This prevents a fast reconnect by the client)
        except Exception as e:
            raise e

    # ping
    def ping_target(self):
        try:
            if self.opcda_engine:
                return self.opcda_engine.ping_target()
        except Exception as e:
            print(e.__str__())
        return False

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
            opcda_point_dict = {}
            for point_name in dict_point.keys():
                if point_name in self.dict_opcda_point.keys():
                    opcda_point_dict[point_name] = self.dict_opcda_point[point_name]

            if len(opcda_point_dict) > 0 and self.opcda_engine:
                result_dict = self.opcda_engine.read_values(opcda_point_dict)
        except Exception as e:
            raise e
        return result_dict

    def _scrap_points(self) -> dict:
        result_dict = {}
        try:
            if self.opcda_engine:
                result_dict = self.opcda_engine.scrap_value()
        except Exception as e:
            raise e
        return result_dict

    # set
    def set_points(self, dict_point: dict) -> dict:
        result_dict = {}
        try:
            opcda_point_dict = {}
            for point_name in dict_point.keys():
                if point_name in self.dict_opcda_point.keys():
                    opcda_point_dict[point_name] = dict_point[point_name]

            if len(opcda_point_dict) > 0 and self.opcda_engine:
                result_dict = self.opcda_engine.write_values(opcda_point_dict)
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