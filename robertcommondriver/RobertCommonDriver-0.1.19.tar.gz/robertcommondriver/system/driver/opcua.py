import json
import time
import logging
from datetime import datetime
from threading import Thread
from .base import BasePoint, BaseDriver, PointTableDict

from opcua import Client,ua
from opcua.common.ua_utils import val_to_string

'''
pip install opcua==0.98.13
'''

#OPCUA Point
class OPCUAPoint(BasePoint):

    def __init__(self, point_writable:bool, point_name:str, point_node_id:str, point_description:str=''):
        super().__init__('opcua', point_writable, point_name, point_description)
        self.point_node_id = point_node_id

    @property
    def get_point_node_id(self):
        return self.point_node_id

class OPCUAEngine(Thread):

    def __init__(self, end_point:str, security_string:str, authentication:dict,  subscript_add:int, subscript_interval:int, point_dict: dict, call_back_func=None):
        Thread.__init__(self)

        #param#########
        self.end_point = end_point
        self.security_string = security_string
        self.authentication = authentication
        self.subscript_add = subscript_add
        self.subscript_interval = subscript_interval
        self.point_dict = point_dict
        self.call_back_func = call_back_func
        ##############

        self.opcua_client = None
        self.opcua_node_dict = {}       #nodeid:pointname
        self.opcua_connect_status = False
        self.opcua_subscribe = None
        self.opcua_sub_hand_list = []
        self.opcua_value_dict = {}
        self.opcua_thread_exit = False

    def exit(self):
        try:
            self.opcua_thread_exit = True
            self.close_opcua_client()
        except Exception as e:
            pass

    def reset(self):
        self.opcua_subscribe = None
        self.opcua_node_dict = {}
        self.opcua_sub_hand_list = []
        self.opcua_client = None
        self.opcua_connect_status = False
        self.opcua_value_dict = {}

    def get_opcua_client(self):
        try:
            if self.opcua_client == None:
                if len(self.end_point) > 0:
                    self.opcua_client = Client(self.end_point)  #

                    #set security_string
                    if len(self.security_string) > 0:
                        #client.set_security_string("Basic256,Sign,certificate-example.der,private-key-example.pem")
                        #Policy,Mode,certificate,private_key[,server_private_key]
                        #Basic128Rsa15 or Basic256  Sign or SignAndEncrypt  certificate, private_key and server_private_key are paths to .pem or .der files
                        self.opcua_client.set_security_string(self.security_string)

                    #set auth  Anonymous/UserName/Certificate
                    if len(self.authentication) > 0:
                        if 'type' in self.authentication.keys():
                            if self.authentication['type'] == 'UserName':
                                self.opcua_client.set_user(self.authentication['user'])
                                self.opcua_client.set_password(self.authentication['password'])
                            elif self.authentication['type'] == 'Certificate':
                                # client.load_client_certificate("server_cert.pem")
                                # client.load_private_key("mykey.pem")
                                self.opcua_client.load_client_certificate(self.authentication['client_certificate'])
                                self.opcua_client.load_private_key(self.authentication['private_key'])

                    if self.opcua_client:
                        self.opcua_client.secure_channel_timeout = 10000
                        self.opcua_client.session_timeout = 10000

                        self.opcua_client.connect()
                        self.opcua_connect_status = True

                        self.opcua_client.load_type_definitions()
        except Exception as e:
            logging.error(f"opcua({self.end_point}) connect fail({e.__str__()})")
        return self.opcua_client

    def close_opcua_client(self):
        try:
            if self.opcua_subscribe:
                while (len(self.opcua_sub_hand_list) > 0):
                    sub_handle = self.opcua_sub_hand_list.pop(0)
                    self.opcua_subscribe.unsubscribe(sub_handle)
                self.opcua_subscribe.delete()

            #close
            if self.opcua_client and self.opcua_connect_status == True:
                self.opcua_client.disconnect()

        except Exception as e:
            logging.error(f"opcua({self.end_point}) close fail({e.__str__()})")
        self.reset()

    def _chunk_list(self, list_object: list, list_number: int):
        for i in range(0, len(list_object), list_number):
            yield list_object[i:i + list_number]

    def _get_subscript_node(self):
        opcua_node_list = []
        for point_name in self.point_dict.keys():
            node = self.opcua_client.get_node(self.point_dict[point_name].get_point_node_id)
            if node:
                node_id = str(node.nodeid.Identifier)
                if node_id not in self.opcua_node_dict.keys():
                    self.opcua_node_dict[node_id] = []
                    opcua_node_list.append(node)
                self.opcua_node_dict[node_id].append(point_name)

        group_count = int(len(opcua_node_list) / self.subscript_add)
        group_count = group_count if len(opcua_node_list) % self.subscript_add == 0 else group_count + 1
        return self._chunk_list(opcua_node_list, group_count)

    def create_subscript(self):
        if self.get_opcua_client():
            sub = SubHandler(self)
            self.opcua_subscribe = self.opcua_client.create_subscription(self.subscript_interval, sub)

    def add_subscript_node(self, node_id_list):
        opc_sub_handle = self.opcua_subscribe.subscribe_data_change(node_id_list)
        self.opcua_sub_hand_list.append(opc_sub_handle)

    def change_data(self, node, value, data):
        try:
            if data.monitored_item.Value.StatusCode.is_good():
                if value != None:
                    self.opcua_value_dict[str(node.nodeid.Identifier)] = [str(val_to_string(value)), datetime.utcnow()]
        except Exception as e:
            logging.error(f"opcua({self.end_point}) change data fail({e.__str__()})")

    #create
    def create_subscripts(self):
        try:
            if len(self.point_dict) > 0:
                if self.opcua_subscribe == None:
                    if len(self.point_dict) > 0:
                        self.create_subscript()

                if self.opcua_subscribe:
                    #add point
                    if len(self.point_dict) > 0:
                        if len(self.opcua_sub_hand_list) <= 0:
                            opcua_sub_node_list = self._get_subscript_node()
                            for sub_node_list in opcua_sub_node_list:
                                self.add_subscript_node(sub_node_list)
                            time.sleep(0.1)

                self.ping_target()
        except Exception as e:
            self.close_opcua_client()

    def run(self):
        try:
            while self.opcua_thread_exit == False:
                self.create_subscripts()
                time.sleep(2)
        except Exception as e:
            print(e.__str__())

    #
    def read_values(self, dict_point):
        result_dict = {}
        try:
            if self.get_opcua_client():
                for point_name in dict_point.keys():
                    node = self.opcua_client.get_node(dict_point[point_name].get_point_node_id)
                    if node:
                        result_dict[point_name] = node
                nodes = result_dict.values()
                if len(nodes) > 0:
                    results = self.opcua_client.get_values(nodes)
                    result_dict = dict(zip(result_dict.keys(), [val_to_string(result) for result in results]))
        except Exception as e:
            raise e
        return result_dict

    def scrap_value(self):
        result_dict = {}
        for node_id in self.opcua_value_dict.keys():
            if node_id in self.opcua_node_dict.keys():
                points = self.opcua_node_dict[node_id]
                for point_name in points:
                    result_dict[point_name] = self.opcua_value_dict[node_id][0]
        return result_dict

    #search###
    def search_points(self, call_back_func=None):
        search_point = {}
        try:
            self.call_back_func = call_back_func
            if self.get_opcua_client():
                self.loop_group_list(self.opcua_client, self.opcua_client.get_root_node(), 'Root', search_point)
                return search_point
        except Exception as e:
            raise e
        return search_point

    def loop_group_list(self, opcua_client, parent_node, param_path, search_point):
        try:
            if opcua_client and parent_node != None:
                for node in parent_node.get_children():
                    nodeAttrs = node.get_attributes([
                                                 ua.AttributeIds.DisplayName,
                                                 ua.AttributeIds.Description,
                                                 ua.AttributeIds.NodeId,
                                                 ua.AttributeIds.NodeClass,
                                                 ua.AttributeIds.DataType,
                                                 ua.AttributeIds.Value])
                    name, desc, nid, nclass, dtype, val = [attr.Value.Value for attr in nodeAttrs]
                    if nclass == ua.NodeClass.Variable:     #leaf
                        point_name = ('%s.%s' % (param_path, name.to_string())).replace('.', '_').replace(':', '_').replace('/', '_')
                        search_point[point_name] = {'point_name': point_name, 'point_writable': True, 'point_node_id': nid.to_string(), 'point_node_path': '%s.%s' % (param_path, name.to_string()), 'point_value': str(val_to_string(val)), 'point_description': '' if desc == None else desc.to_string()}
                        if self.call_back_func:
                            self.call_back_func(point_name)
                    else:                                   #branch  Ojecet
                        if name.to_string() != 'Types' and name.to_string() != 'Views':
                            self.loop_group_list(opcua_client, node, '%s.%s' % (param_path, name.to_string()), search_point)
        except Exception as e:
            logging.error(f"opcua({self.end_point}) loop ({param_path}) fail({e.__str__()})")

    def ping_target(self):
        if self.get_opcua_client():
            return self.opcua_client.get_node(ua.ObjectIds.Server_ServerStatus_State).get_value() == 0
        return False

class SubHandler(object):

    def __init__(self, obj):
        self.obj = obj

    def datachange_notification(self, node, val, data):
        try:
            if self.obj:
                self.obj.change_data(node, val, data)
        except Exception as e:
            raise e

    def event_notification(self, event):
        print('New event %s' % str(event))    #'New event %s' % str(event)

    def status_change_notification(self, status):
        """
        called for every status change notification from server
        """
        print(status)

#OPCUA Driver
class OPCUADriver(BaseDriver):

    def __init__(self, dict_config: dict, dict_point: PointTableDict):
        super().__init__(dict_config, dict_point)

        self.dict_opcua_point = {}
        self.opcua_engine = None

        self.configure()

    def __del__(self):
        super().__del__()

    def configure(self):
        try:
            #{'endpoint': '', 'security': 'Basic128Rsa15,SignAndEncrypt,file/opcua/certificate-example.der,file/opcua/private-key-example.pem', 'auth': {'UserName': [], 'Certificate': []}}

            #config
            self.opcua_endpoint = str(self.dict_config.get("endpoint"))
            self.opcua_security = str(self.dict_config.get("security", ''))
            self.opcua_auth =  self.dict_config.get('auth', {'type': 'Anonymous', 'user': '', 'password': '', 'client_certificate': '', 'private_key': ''})
            if isinstance(self.opcua_auth, str):
                self.opcua_auth = json.loads(self.opcua_auth)
            self.opcua_subscript_add = self.dict_config.get('subscript_add', 1000)
            self.opcua_subscript_interval = self.dict_config.get('subscript_interval', 1000)

            #csv
            for point_name in self.dict_point.keys():
                self.dict_opcua_point[point_name] = OPCUAPoint(bool(str(self.dict_point[point_name]['point_writable'])),str(self.dict_point[point_name]['point_name']),str(self.dict_point[point_name]['point_node_id']))

            #create_engine
            close_delay = 0
            if self.opcua_engine != None:
                self.opcua_engine.exit()
                del self.opcua_engine
                self.opcua_engine = None
                close_delay = 2

            self.opcua_engine = OPCUAEngine(self.opcua_endpoint, self.opcua_security, self.opcua_auth, self.opcua_subscript_add, self.opcua_subscript_interval, self.dict_opcua_point)
            self.opcua_engine.start()

            time.sleep(close_delay)  # delay on closed socket(This prevents a fast reconnect by the client)
        except Exception as e:
            raise e

    # ping
    def ping_target(self):
        try:
            if self.opcua_engine:
                return self.opcua_engine.ping_target()
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
            opcua_point_dict = {}
            for point_name in dict_point.keys():
                if point_name in self.dict_opcua_point.keys():
                    opcua_point_dict[point_name] = self.dict_opcua_point[point_name]

            if len(opcua_point_dict) > 0 and self.opcua_engine:
                result_dict = self.opcua_engine.read_values(opcua_point_dict)
        except Exception as e:
            raise e
        return result_dict

    def _scrap_points(self) -> dict:
        result_dict = {}
        try:
            if self.opcua_engine:
                result_dict = self.opcua_engine.scrap_value()
        except Exception as e:
            raise e
        return result_dict

    def set_points(self, dict_point: dict) -> dict:
        set_result_dict = {}
        try:
            pass
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
            search_point = self.opcua_engine.search_points(call_back_func)
        except Exception as e:
            raise e
        return search_point

    ###########