import logging
import re
import serial
import time
import socket
import struct
from typing import Callable
from threading import Thread

import modbus_tk
import modbus_tk.modbus_tcp as modbus_tcp
import modbus_tk.modbus_rtu as modbus_rtu

from .base import BasePoint, BaseDriver, PointTableDict

'''
    pip install modbus-tk==1.1.2
'''

#ModbusPoint
class ModbusPoint(BasePoint):

    def __init__(self, point_writable:bool, point_name:str,point_device_address:str, point_slave_id:int,point_fun_code:int, point_address:int, point_data_type:int,point_data_length:int, point_scale:float, point_description:str=''):
        super().__init__('modbus', point_writable, point_name, point_description)

        self.point_device_address = point_device_address    #device address
        self.point_slave_id = point_slave_id        #slave id
        self.point_fun_code = point_fun_code        #fun code
        self.point_address = point_address          #address
        self.point_data_type = point_data_type      #data type
        self.point_data_length = point_data_length  #data length
        self.point_scale = point_scale              #scale
        self.point_set_value = 0

    # get device address
    @property
    def get_point_device_address(self):
        return self.point_device_address

    # get slave id
    @property
    def get_point_slave_id(self):
        return self.point_slave_id

    # get fun code
    @property
    def get_point_fun_code(self):
        return self.point_fun_code

    # get data type
    @property
    def get_point_data_type(self):
        return self.point_data_type

    # get data length
    @property
    def get_point_data_length(self):
        return self.point_data_length

    # 获取倍率
    @property
    def get_point_scale(self):
        if self.point_scale == 0:
            return 1
        return self.point_scale

    # get address
    @property
    def get_point_address(self):
        return self.point_address

    #get set value
    @property
    def get_point_set_value(self):
        return self.point_set_value

    def set_point_set_value(self, point_set_value):
        self.point_set_value = point_set_value

# modbus data type
class ModbusType:
    E_MODBUS_SIGNED = 0
    E_MODBUS_UNSIGNED = 1
    E_MODBUS_BITE = 2
    E_MODBUS_LONG = 3
    E_MODBUS_LONG_INVERSE = 4
    E_MODBUS_FLOAT = 5
    E_MODBUS_FLOAT_INVERSE = 6
    E_MODBUS_DOUBLE = 7
    E_MODBUS_DOUBLE_INVERSE = 8
    E_MODBUS_STRING = 9
    E_MODBUS_STRING_INVERSE = 10
    E_MODBUS_POWERLINK = 11  # 11 powerLink
    E_MODBUS_HEX = 12

# modbus read/write unit
class ModbusReadUnit:
    def __init__(self, modbus_id:int, modbus_start:int, modbus_end:int, modbus_fun:int, modbus_multi_read:int):
        self.modbus_id = modbus_id
        self.modbus_start = modbus_start
        self.modbus_end = modbus_end
        self.modbus_fun = modbus_fun
        self.modbus_multi_read = modbus_multi_read

        self.full_flag = False
        self.modbus_point_list = []

    def set_full_flag(self):
        self.full_flag = True

    @property
    def get_full_flag(self):
        return self.full_flag

    @property
    def get_modbus_id(self):
        return self.modbus_id

    @property
    def get_modbus_start(self):
        return self.modbus_start

    @property
    def get_modbus_end(self):
        return self.modbus_end

    @property
    def get_modbus_fun(self):
        return self.modbus_fun

    @property
    def get_modbus_multi_read(self):
        return self.modbus_multi_read

    def set_modbus_end(self, modbus_start, modbus_end):
        self.modbus_end = modbus_end
        self.add_modbus_point_list(modbus_start, modbus_end)

    def add_modbus_point_list(self, modbus_start, modbus_end):
        self.modbus_point_list.append([modbus_start, modbus_end])

    def get_modbus_point_list(self):
        return self.modbus_point_list

class ModbusEngine(Thread):

    def __init__(self, control_mode:str,device_address:str, dict_point:dict, modbus_time_out:int, modbus_multi_read:int, modbus_cmd_interval:float, callbacks: dict = {}):
        Thread.__init__(self)

        self.control_mode = control_mode            #read/write
        self.device_address = device_address
        self.dict_point = dict_point

        ##modbus connect param ##########################
        self.modbus_time_out = modbus_time_out
        self.modbus_multi_read = modbus_multi_read
        self.modbus_cmd_interval = modbus_cmd_interval
        ###########################

        self.dict_value = {}
        self.new_point_list = []
        self.modbus_reead_unit_list = {}
        self.modbus_value_dict = {}
        self.modbus_client = None
        self.modbus_set_result_dict = {}

        self.callbacks = callbacks

    def set_call_result(self, call_method: str, **kwargs):
        if isinstance(self.callbacks, dict):
            call_method = self.callbacks.get(call_method)
            if isinstance(call_method, Callable):
                call_method(**kwargs)

    def _check_ip(self, ip: str):
        try:
            p = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
            if p.match(ip):
                return True
        except Exception as e:
            raise e
        return False

    def _get_modbus_info(self, device_address: str) -> dict:
        modbus_info = {}
        try:
            if len(device_address) > 0:
                if device_address.find('/dev/tty') == 0:  # linux
                    info_list = device_address.split('|')
                    if len(info_list) == 1:  # port
                        modbus_info = {'type': 'rtu', 'port': str(info_list[0]), 'baudrate': 9600, 'parity': 'N','bytesize': 8, 'stopbits': 1, 'xonxoff': 0}
                    elif len(info_list) == 2:  # port/baudrate
                        modbus_info = {'type': 'rtu', 'port': str(info_list[0]), 'baudrate': int(str(info_list[1])),'parity': 'N', 'bytesize': 8, 'stopbits': 1, 'xonxoff': 0}
                    elif len(info_list) == 3:  # port/baudrate/parity
                        modbus_info = {'type': 'rtu', 'port': str(info_list[0]), 'baudrate': int(str(info_list[1])),'parity': str(info_list[2]), 'bytesize': 8, 'stopbits': 1, 'xonxoff': 0}
                else:
                    info_list = device_address.split('/')
                    if len(info_list) == 1:  # IP or port
                        if self._check_ip(info_list[0]) == True:
                            modbus_info = {'type': 'tcp', 'host': str(info_list[0]), 'port': 502}
                        else:
                            modbus_info = {'type': 'rtu', 'port': str(info_list[0])}
                    elif len(info_list) == 2:  # IP/port   port/baudrate
                        if self._check_ip(info_list[0]) == True:
                            modbus_info = {'type': 'tcp', 'host': str(info_list[0]), 'port': int(str(info_list[1]))}
                        else:
                            modbus_info = {'type': 'rtu', 'port': str(info_list[0]),'baudrate': int(str(info_list[1])), 'bytesize': 8, 'parity': 'N','stopbits': 1, 'xonxoff': 0}
                    elif len(info_list) == 3:  # port/baudrate/parity
                        modbus_info = {'type': 'rtu', 'port': str(info_list[0]), 'baudrate': int(str(info_list[1])),'parity': str(info_list[2]), 'bytesize': 8, 'stopbits': 1, 'xonxoff': 0}
        except Exception as e:
            raise e
        return modbus_info

    def _get_modbus_client(self):
        try:
            if self.modbus_client == None:
                modbus_info = self._get_modbus_info(self.device_address)
                if 'type' in modbus_info.keys():
                    modbus_type = modbus_info['type']
                    if modbus_type == 'tcp':
                        self.modbus_client = modbus_tcp.TcpMaster(host=modbus_info['host'], port=modbus_info['port'])
                        self.modbus_client.set_timeout(self.modbus_time_out)
                    else:
                        modbus_com = modbus_info['port']  # com5 或/dev/tty0
                        if modbus_com.find('/dev/tty') == 0:
                            self.modbus_client = modbus_rtu.RtuMaster(
                                serial.Serial(port=modbus_com, baudrate=modbus_info['baudrate'],bytesize=modbus_info['bytesize'], parity=modbus_info['parity'],stopbits=modbus_info['stopbits'], xonxoff=modbus_info['xonxoff']))
                            self.modbus_client.set_timeout(self.modbus_time_out)
                        else:
                            self.modbus_client = modbus_rtu.RtuMaster(
                                serial.Serial(port=modbus_com, baudrate=modbus_info['baudrate'],bytesize=modbus_info['bytesize'], parity=modbus_info['parity'],stopbits=modbus_info['stopbits'], xonxoff=modbus_info['xonxoff']))

                        self.modbus_client.set_timeout(self.modbus_time_out)
                        self.modbus_client.set_verbose(True)
        except Exception as e:
            raise e
        return self.modbus_client

    def _release_modbus_client(self):
        try:
            if self.modbus_client:
                self.modbus_client.close()
            self.modbus_client = None
        except Exception as e:
            raise e

    def _sort_point_by_device(self):
        try:
            if len(self.dict_point) > 0:
                self.new_point_list = []

                # First create a new point by type and number of bits
                for point_name in self.dict_point.keys():
                    point = self.dict_point[point_name]
                    self.new_point_list.append([point.get_point_slave_id, point.get_point_address, point.get_point_fun_code,point.get_point_data_type, point.get_point_data_length])

                # Sort by device (device address first, function code `followed by address)
                self.new_point_list.sort(key=lambda t: (t[0], t[2], t[1]))

                for point in self.new_point_list:
                    # modbusID, modbusStart, modbusEnd, modbusFun, modbusMultiRead, modbusErrPoint, modbusUndateInderval, modebusLastUpdate
                    modbus_unit = ModbusReadUnit(int(point[0]), int(point[1]), int(point[1]) + int(point[4]) - 1 if int(point[3]) != ModbusType.E_MODBUS_BITE else int(point[1]), int(point[2]), self.modbus_multi_read)
                    if self._combine_read_unit_v1(modbus_unit) == False:
                        key_name = '%u_%u_%u' % (modbus_unit.get_modbus_id, modbus_unit.get_modbus_fun, modbus_unit.get_modbus_start)
                        modbus_unit.add_modbus_point_list(int(point[1]), int(point[1]) + int(point[4]) - 1)
                        self.modbus_reead_unit_list[key_name] = modbus_unit
                return True
        except Exception as e:
            raise e
        return False

    def _combine_read_unit_v1(self, modbus_unit):
        try:
            found_flag = False
            key_name = ''
            for key_name in self.modbus_reead_unit_list:
                if self.modbus_reead_unit_list[key_name].get_modbus_id == modbus_unit.get_modbus_id and self.modbus_reead_unit_list[key_name].get_modbus_fun == modbus_unit.get_modbus_fun and self.modbus_reead_unit_list[key_name].get_full_flag == False:
                    found_flag = True
            if found_flag == True:
                if modbus_unit.get_modbus_start == (self.modbus_reead_unit_list[key_name].get_modbus_end + 1):
                    if self.modbus_reead_unit_list[key_name].get_modbus_end - self.modbus_reead_unit_list[key_name].get_modbus_start + 1 >= self.modbus_multi_read:  # 超过连读上限
                        self.modbus_reead_unit_list[key_name].set_full_flag()
                    else:
                        self.modbus_reead_unit_list[key_name].set_modbus_end(modbus_unit.get_modbus_start, modbus_unit.get_modbus_end)
                        return True
                elif  modbus_unit.get_modbus_start == self.modbus_reead_unit_list[key_name].get_modbus_end:
                    self.modbus_reead_unit_list[key_name].set_modbus_end(modbus_unit.get_modbus_start,modbus_unit.get_modbus_end)
                    return True
        except Exception as e:
            raise e
        return False

    def ping_target(self):
        return True

    def _update_point_value(self):
        try:
            self.modbus_value_dict = {}

            for modbus_unit in self.modbus_reead_unit_list.keys():
                self._send_read_mutil(self.modbus_reead_unit_list[modbus_unit])
        except Exception as e:
            raise e

    def _send_read_mutil(self, modbus_unit):
        try:
            if modbus_unit.get_modbus_id >= 0 and modbus_unit.get_modbus_start >= 0 and modbus_unit.get_modbus_end >= modbus_unit.get_modbus_start and modbus_unit.get_modbus_fun > 0 and modbus_unit.get_modbus_fun < 17:
                self._send_read_cmd(modbus_unit.get_modbus_id, modbus_unit.get_modbus_start,modbus_unit.get_modbus_end, modbus_unit.get_modbus_fun)
            time.sleep(self.modbus_cmd_interval)
        except Exception as e:
            raise e

    # slaveID+funcode+address -> key
    def _generate_key(self, slave_id:int, fun_code:int, address:int) -> str:
        try:
            if fun_code == modbus_tk.defines.READ_HOLDING_REGISTERS or fun_code == modbus_tk.defines.WRITE_MULTIPLE_REGISTERS or fun_code == modbus_tk.defines.READ_WRITE_MULTIPLE_REGISTERS:
                fun_code = modbus_tk.defines.READ_HOLDING_REGISTERS
            elif fun_code == modbus_tk.defines.WRITE_SINGLE_COIL or fun_code == modbus_tk.defines.WRITE_MULTIPLE_COILS:
                fun_code = modbus_tk.defines.READ_COILS
            return '%d_%d_%d' % (slave_id, fun_code, address)
        except Exception as e:
            raise e
        return ''

    def _send_read_cmd(self, slave_id:int, add_start:int, add_end:int, fun_code:int):
        try:
            if self._get_modbus_client() != None:
                if fun_code == modbus_tk.defines.READ_HOLDING_REGISTERS or fun_code == modbus_tk.defines.WRITE_MULTIPLE_REGISTERS or fun_code == modbus_tk.defines.READ_WRITE_MULTIPLE_REGISTERS:
                    fun_code = modbus_tk.defines.READ_HOLDING_REGISTERS
                elif fun_code == modbus_tk.defines.WRITE_SINGLE_COIL or fun_code == modbus_tk.defines.WRITE_MULTIPLE_COILS:
                    fun_code = modbus_tk.defines.READ_COILS

                value_list = self._get_modbus_client().execute(slave_id, fun_code, add_start, add_end - add_start + 1)
                self.set_call_result('debug_log', content=f"modbus({self.device_address}) read ({slave_id}-{fun_code}-[{add_start}-{add_end}]) response {add_end-add_start+1}/{len(value_list)} [{value_list}]")
                if len(value_list) > 0:
                    for index in range(0, len(value_list)):
                        self.modbus_value_dict[self._generate_key(slave_id, fun_code, add_start + index)] = value_list[index]
                    return True
        except modbus_tk.exceptions.ModbusError as e:  # read
            logging.error(f"modbus({self.device_address}) read ({slave_id}-{fun_code}-[{add_start}-{add_end}]) fail({e.__str__()})")
        except (ConnectionRefusedError, ConnectionResetError) as e:  # connect
            logging.error(f"modbus({self.device_address}) read ({slave_id}-{fun_code}-[{add_start}-{add_end}]) fail({e.__str__()})")
            self.modbus_client = None
        except socket.timeout as e:  # timeout
            logging.error(f"modbus({self.device_address}) read ({slave_id}-{fun_code}-[{add_start}-{add_end}]) fail({e.__str__()})")
            self.modbus_client = None
        except (modbus_tk.modbus_tcp.ModbusInvalidMbapError) as e:  # Invalid
            logging.error(f"modbus({self.device_address}) read ({slave_id}-{fun_code}-[{add_start}-{add_end}]) fail({e.__str__()})")
        except Exception as e:  # other
            logging.error(f"modbus({self.device_address}) read ({slave_id}-{fun_code}-[{add_start}-{add_end}]) fail({e.__str__()})")
        time.sleep(1)
        return False

    def run(self):
        try:
            if self.control_mode == 'write':    #write mode
                self._set_point_value()
                self._release_modbus_client()
            else:
                self._sort_point_by_device()
                self._update_point_value()
                self._get_point_value_set()
                self._release_modbus_client()
        except Exception as e:
            raise e

    def _get_point_value_set(self):
        try:
            if len(self.modbus_value_dict) > 0:
                self.dict_value = {}
                for point_name in self.dict_point.keys():
                    modbus_point = self.dict_point[point_name]
                    point_value = self.get_value(modbus_point)
                    if point_value != None:
                        self.dict_value[point_name] = point_value
        except Exception as e:
            raise e

    def get_value(self, modbus_point):
        try:
            value_list = []
            has_fault = False
            if modbus_point.get_point_data_type == ModbusType.E_MODBUS_BITE:
                key_name = self._generate_key(modbus_point.get_point_slave_id, modbus_point.get_point_fun_code,modbus_point.get_point_address)
                if key_name != '':
                    if key_name in self.modbus_value_dict.keys():
                        value = self.modbus_value_dict[key_name]
                        value_list.append(value)
                    else:
                        has_fault = True
            elif modbus_point.get_point_data_type == ModbusType.E_MODBUS_POWERLINK:
                pass
            else:
                data_range = modbus_point.get_point_data_length
                if data_range <= 0:
                    data_range = 1
                for index in range(0, data_range):
                    key_name = self._generate_key(modbus_point.get_point_slave_id, modbus_point.get_point_fun_code, modbus_point.get_point_address + index)
                    if key_name != '':
                        if key_name in self.modbus_value_dict.keys():
                            value = self.modbus_value_dict[key_name]
                            value_list.append(value)
                        else:
                            has_fault = True
                            break
            if has_fault == False:
                return self._get_value_by_data_type_and_range(modbus_point, value_list)
        except Exception as e:
            logging.error(f"modbus({self.device_address}) get({modbus_point.get_point_name}) fail({e.__str__()})")
        return None

    def _get_value_by_data_type_and_range(self, modbus_point, value_list):
        try:
            if len(value_list) > 0:
                if modbus_point.get_point_data_type == ModbusType.E_MODBUS_SIGNED:
                    wValue = self._analyze_signed(value_list[0])
                    if wValue != None:
                        return self._conver_value_multi(wValue, modbus_point)
                elif modbus_point.get_point_data_type == ModbusType.E_MODBUS_UNSIGNED:
                    wValue = self._analyze_unsigned(value_list[0])
                    if wValue != None:
                        return self._conver_value_multi(wValue, modbus_point)
                elif modbus_point.get_point_data_type == ModbusType.E_MODBUS_HEX:
                    return None
                elif modbus_point.get_point_data_type == ModbusType.E_MODBUS_BITE:
                    return self._analyze_bite(value_list[0], modbus_point.get_point_data_length)
                elif modbus_point.get_point_data_type == ModbusType.E_MODBUS_LONG:
                    if len(value_list) >= 2:
                        dwValue = self._analyze_long(value_list[0], value_list[1])
                        if dwValue != None:
                            return self._conver_value_multi(dwValue, modbus_point)
                elif modbus_point.get_point_data_type == ModbusType.E_MODBUS_LONG_INVERSE:
                    if len(value_list) >= 2:
                        dwValue = self._analyze_long_inverse(value_list[0], value_list[1])
                        if dwValue != None:
                            return self._conver_value_multi(dwValue, modbus_point)
                elif modbus_point.get_point_data_type == ModbusType.E_MODBUS_FLOAT:
                    if len(value_list) >= 2:
                        dwValue = self._analyze_float(value_list[0], value_list[1])
                        if dwValue != None:
                            return self._conver_value_multi(dwValue, modbus_point)
                elif modbus_point.get_point_data_type == ModbusType.E_MODBUS_FLOAT_INVERSE:
                    if len(value_list) >= 2:
                        dwValue = self._analyze_float_inverse(value_list[0], value_list[1])
                        if dwValue != None:
                            return self._conver_value_multi(dwValue, modbus_point)
                elif modbus_point.get_point_data_type == ModbusType.E_MODBUS_DOUBLE:
                    if len(value_list) >= 4:
                        dwValue = self._analyze_double(value_list[0], value_list[1], value_list[2], value_list[3])
                        if dwValue != None:
                            return self._conver_value_multi(dwValue, modbus_point)
                elif modbus_point.get_point_data_type == ModbusType.E_MODBUS_DOUBLE_INVERSE:
                    if len(value_list) >= 4:
                        dwValue = self._analyze_double_inverse(value_list[0], value_list[1], value_list[2], value_list[3])
                        if dwValue != None:
                            return self._conver_value_multi(dwValue, modbus_point)
                elif modbus_point.get_point_data_type == ModbusType.E_MODBUS_STRING:
                    dwValue = self._analyze_string(value_list)
                    if dwValue != None:
                        return '%s' % dwValue
                elif modbus_point.get_point_data_type == ModbusType.E_MODBUS_STRING_INVERSE:
                    dwValue = self._analyze_string_inverse(value_list)
                    if dwValue != None:
                        return '%s' % dwValue
                elif modbus_point.get_point_data_type == ModbusType.E_MODBUS_POWERLINK:
                    return None
                else:
                    return None
        except Exception as e:
            raise e
        return None

    def _conver_value_multi(self, modbus_value, modbus_point):
        try:
            if modbus_point.get_point_scale == 0:
                return None
            elif modbus_point.get_point_scale == 1:
                return modbus_value
            else:
                dValue = modbus_value / modbus_point.get_point_scale
                return '%.2f' % dValue
        except Exception as e:
            raise e
        return None

    def _analyze_signed(self, data):
        try:
            return struct.unpack('h', struct.pack('H', data))[0]
        except Exception as e:
            raise e
        return None

    def _analyze_unsigned(self, data):
        try:
            return data
        except Exception as e:
            raise e
        return None

    def _analyze_hex(self, data):
        try:
            return data
        except Exception as e:
            raise e
        return None

    def _analyze_bite(self, data, index):
        try:
            return data & (1 << index) and 1 or 0
        except Exception as e:
            raise e
        return None

    def _analyze_long_inverse(self, data, data_high):
        try:
            return struct.unpack('i', struct.pack('HH', data_high, data))[0]
        except Exception as e:
            raise e
        return None

    def _analyze_long(self, data, data_high):
        try:
            return struct.unpack('i', struct.pack('HH', data, data_high))[0]
        except Exception as e:
            raise e
        return None

    def _analyze_float_inverse(self, data, data_high):
        try:
            return struct.unpack('f', struct.pack('HH', data_high, data))[0]
        except Exception as e:
            raise e
        return None

    def _analyze_float(self, data, data_high):
        try:
            return struct.unpack('f', struct.pack('HH', data, data_high))[0]
        except Exception as e:
            raise e
        return None

    def _analyze_double_inverse(self, data, data1, data2, data3):
        try:
            return struct.unpack('d', struct.pack('HHHH', data3, data2, data1, data))[0]
        except Exception as e:
            raise e
        return None

    def _analyze_double(self, data, data1, data2, data3):
        try:
            return struct.unpack('d', struct.pack('HHHH', data, data1, data2, data3))[0]
        except Exception as e:
            raise e
        return None

    def _analyze_string_inverse(self, value_list):
        try:
            length = len(value_list)
            str = bytearray(length * 2)
            for i in range(length):
                str[2 * i] = value_list[length - i - 1]
                str[2 * i + 1] = value_list[length - i - 1][1]
            format = '%ds' % (length * 2)
            return struct.unpack(format, str)[0]
        except Exception as e:
            raise e
        return None

    def _analyze_string(self, value_list):
        try:
            length = len(value_list)
            str = bytearray(length * 2)
            for i in range(length):
                str[2 * i] = value_list[i][0]
                str[2 * i + 1] = value_list[i][1]
            format = '%ds' % (length * 2)
            return struct.unpack(format, str)[0]
        except Exception as e:
            raise e
        return None

    def get_modbus_values(self):
        return self.dict_value

    def get_modbus_set_result(self):
        return self.modbus_set_result_dict

    def _set_point_value(self):
        try:
            self.modbus_set_result_dict = {}

            for point_name in self.dict_point.keys():
                modbus_point = self.dict_point[point_name]
                point_value = modbus_point.get_point_set_value
                self.modbus_set_result_dict[point_name] = self._set_write_cmd(modbus_point, point_value)
        except Exception as e:
            raise e

    def _set_write_cmd(self, modbus_point, point_value):
        set_result = False
        try:
            fun_code = modbus_tk.defines.WRITE_SINGLE_REGISTER
            if modbus_point.get_point_data_type == ModbusType.E_MODBUS_BITE:
                fun_code = modbus_tk.defines.WRITE_SINGLE_COIL
            else:
                if modbus_point.get_point_data_length <= 1:
                    fun_code = modbus_tk.defines.WRITE_SINGLE_REGISTER
                else:
                    fun_code = modbus_tk.defines.WRITE_MULTIPLE_REGISTERS

            if self._get_modbus_client() != None:
                slave_id = modbus_point.get_point_slave_id
                add_start = modbus_point.get_point_address
                output_value = self._convert_value_to_vector(modbus_point, point_value)
                if output_value:
                    set_result = self._send_write_cmd(slave_id, fun_code, add_start, output_value)
                    self.set_call_result('debug_log', content=f"modbus({self.device_address}) write ({slave_id}-{fun_code}-{add_start}-[{point_value}]]) response [{set_result}]")
                    time.sleep(self.modbus_cmd_interval)
        except Exception as e:
            logging.error(f"modbus({self.device_address}) set({modbus_point.get_point_name}) fail({e.__str__()})")
        return set_result

    def _convert_value_to_vector(self, modbus_point, point_value):
        value_list = None
        try:
            if modbus_point.get_point_data_type == ModbusType.E_MODBUS_SIGNED:
                value_list = struct.unpack('H', struct.pack('h', int(float(str(point_value)))))
                if value_list:
                    return value_list[0]
            elif modbus_point.get_point_data_type == ModbusType.E_MODBUS_UNSIGNED:
                value_list = struct.unpack('H', struct.pack('H', int(float(str(point_value)))))
                if value_list:
                    return value_list[0]
            elif modbus_point.get_point_data_type == ModbusType.E_MODBUS_HEX:
                return None
            elif modbus_point.get_point_data_type == ModbusType.E_MODBUS_BITE:
                return None
            elif modbus_point.get_point_data_type == ModbusType.E_MODBUS_LONG or modbus_point.get_point_data_type == ModbusType.E_MODBUS_LONG_INVERSE:
                value_list = struct.unpack('HH', struct.pack('L', int(float(str(point_value)))))
                if modbus_point.get_point_data_type == ModbusType.E_MODBUS_LONG_INVERSE:
                    value_list = list(value_list)
                    value_list.reverse()
                return value_list
            elif modbus_point.get_point_data_type == ModbusType.E_MODBUS_FLOAT or modbus_point.get_point_data_type == ModbusType.E_MODBUS_FLOAT_INVERSE:
                value_list = struct.unpack('HH', struct.pack('f', float(str(point_value))))
                if modbus_point.get_point_data_type == ModbusType.E_MODBUS_FLOAT_INVERSE:
                    value_list = list(value_list)
                    value_list.reverse()
                return value_list
            elif modbus_point.get_point_data_type == ModbusType.E_MODBUS_DOUBLE or modbus_point.get_point_data_type == ModbusType.E_MODBUS_DOUBLE_INVERSE:
                value_list = struct.unpack('HHHH', struct.pack('d', float(str(point_value))))
                if modbus_point.get_point_data_type == ModbusType.E_MODBUS_DOUBLE_INVERSE:
                    value_list = list(value_list)
                    value_list.reverse()
                return value_list
            else:
                return None
        except Exception as e:
            raise e
        return None

    def _send_write_cmd(self, slave_id, fun_code, add_start, output_value):
        try:
            if output_value and self._get_modbus_client() != None:
                value_list = self._get_modbus_client().execute(slave_id, fun_code, add_start,output_value=output_value)
                if len(value_list) == 2 and value_list[0] == add_start:
                    return True
        except modbus_tk.exceptions.ModbusError as e:  # read
            logging.error(f"modbus({self.device_address}) write ({slave_id}-{fun_code}-[{add_start}-{output_value}]) fail({e.__str__()})")
        except (ConnectionRefusedError, ConnectionResetError) as e:  # connect
            logging.error(f"modbus({self.device_address}) write ({slave_id}-{fun_code}-[{add_start}-{output_value}]) fail({e.__str__()})")
            self.modbus_client = None
        except socket.timeout as e:  # timeout
            logging.error(f"modbus({self.device_address}) write ({slave_id}-{fun_code}-[{add_start}-{output_value}]) fail({e.__str__()})")
            self.modbus_client = None
        except (modbus_tk.modbus_tcp.ModbusInvalidMbapError) as e:  # Invalid
            logging.error(f"modbus({self.device_address}) write ({slave_id}-{fun_code}-[{add_start}-{output_value}]) fail({e.__str__()})")
        except Exception as e:  # other
            logging.error(f"modbus({self.device_address}) write ({slave_id}-{fun_code}-[{add_start}-{output_value}]) fail({e.__str__()})")
        self._release_modbus_client()
        time.sleep(1)
        return False

#Modbus driver
class ModbusDriver(BaseDriver):

    #初始化函数
    def __init__(self, dict_config: dict, dict_point: PointTableDict):
        super().__init__(dict_config, dict_point)

        ##modbus connect param ##########################
        self.modbus_time_out = 5
        self.modbus_multi_read = 100
        self.modbus_cmd_interval = 0.3
        self.enable = True
        ###########################

        self.dict_modbus_point = {}

        self.configure()

    def __del__(self):
        super().__del__()

    def exit(self):
        pass

    def configure(self):
        # config
        self.modbus_time_out = int(str(self.dict_config.get("timeout", "5")))
        self.modbus_multi_read = int(str(self.dict_config.get("multi_read", "100")))
        self.modbus_cmd_interval = float(str(self.dict_config.get("cmd_interval", "0.3")))
        self.enable = str(self.dict_config.get("enabled", "true")).lower() == 'true'

        # csv
        for point_name in self.dict_point.keys():
            self.dict_modbus_point[point_name] = ModbusPoint(bool(str(self.dict_point[point_name]['point_writable'])),
                                                                 str(self.dict_point[point_name]['point_name']),
                                                                 str(self.dict_point[point_name]['point_device_address']),
                                                                 int(str(self.dict_point[point_name]['point_slave_id'])),
                                                                 int(str(self.dict_point[point_name]['point_fun_code'])),
                                                                 int(str(self.dict_point[point_name]['point_address'])),int(str(self.dict_point[point_name]['point_data_type'])),int(str(self.dict_point[point_name]['point_data_length'])), 1)

    # ping
    def ping_target(self) -> bool:
        return True

    def get_points(self, dict_point: dict = {}) -> dict:
        result_dict = {}
        if len(dict_point) == 0:
            result_dict = self._scrap_points()
        else:
            result_dict = self._get_points(dict_point)
        return result_dict

    def _get_points(self, dict_point: dict) -> dict:
        result_dict = {}
        modbus_device_dict = {}
        for point_name in dict_point.keys():
            if point_name in self.dict_modbus_point.keys():
                modbus_point = self.dict_modbus_point[point_name]
                device_address = modbus_point.get_point_device_address
                if device_address not in modbus_device_dict.keys():
                    modbus_device_dict[device_address] = {}
                modbus_device_dict[device_address][point_name] = modbus_point

        if len(modbus_device_dict) > 0:
            result_dict = self._read_modbus_values(modbus_device_dict)
        return result_dict

    def _scrap_points(self) -> dict:
        result_dict = {}
        modbus_device_dict = {}
        for point_name in self.dict_modbus_point.keys():
            modbus_point = self.dict_modbus_point[point_name]
            device_address = modbus_point.get_point_device_address
            if device_address not in modbus_device_dict.keys():
                modbus_device_dict[device_address] = {}
            modbus_device_dict[device_address][point_name] = modbus_point

        if len(modbus_device_dict) > 0:
            result_dict = self._read_modbus_values(modbus_device_dict)
        return result_dict

    def set_points(self, dict_point: dict) -> dict:
        set_result_dict = {}
        modbus_device_dict = {}
        for point_name in dict_point.keys():
            if point_name in self.dict_modbus_point.keys():
                modbus_point = self.dict_modbus_point[point_name]
                device_address = modbus_point.get_point_device_address
                if device_address not in modbus_device_dict.keys():
                    modbus_device_dict[device_address] = {}
                point_value = dict_point[point_name]
                if modbus_point.get_point_scale != 1 and modbus_point.get_point_scale != 0:
                    point_value =  '%.2f' % (point_value * modbus_point.get_point_scale)
                modbus_point.set_point_set_value(point_value)
                modbus_device_dict[device_address][point_name] = modbus_point

        if len(modbus_device_dict) > 0:
            set_result_dict = self._write_modbus_values(modbus_device_dict)
        return set_result_dict

    def reset_config(self, dict_config: dict):
        super().reset_config(dict_config)
        self.configure()

    def reset_point(self, dict_point: dict):
        super().reset_point(dict_point)
        self.configure()

    def search_points(self, call_back_func=None) -> dict:
        search_point = {}
        return search_point

    def _read_modbus_values(self, modbus_device_dict:dict) -> dict:
        result_dict = {}
        modbus_client_thread = []
        for device_address in modbus_device_dict.keys():
            modbus_client = ModbusEngine('read', device_address, modbus_device_dict[device_address], self.modbus_time_out, self.modbus_multi_read, self.modbus_cmd_interval, self.callbacks)
            modbus_client.setDaemon(True)
            modbus_client.start()
            modbus_client_thread.append(modbus_client)

        for modbus_client in modbus_client_thread:
            modbus_client.join()
            result_dict.update(modbus_client.get_modbus_values())
        return result_dict

    def _write_modbus_values(self, modbus_device_dict: dict) -> dict:
        result_dict = {}
        modbus_client_thread = []
        for device_address in modbus_device_dict.keys():
            modbus_client = ModbusEngine('write', device_address, modbus_device_dict[device_address],self.modbus_time_out, self.modbus_multi_read,self.modbus_cmd_interval, self.callbacks)
            modbus_client.setDaemon(True)
            modbus_client.start()
            modbus_client_thread.append(modbus_client)

        # 等待完成
        for modbus_client in modbus_client_thread:
            modbus_client.join()
            result_dict.update(modbus_client.get_modbus_set_result())
        return result_dict