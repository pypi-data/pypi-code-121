'''
pip install python-snap7==0.10

Note：
    windows:
        snap7.dll is added to the python installation directory or any directory in the system environment

    linux install dll 
        https://blog.csdn.net/ludlee/article/details/88169504

20190708
    #define daveP 0x80    		/* direct peripheral access */
    #define daveInputs 0x81     S7AreaPE  
    #define daveOutputs 0x82    S7AreaPA
    #define daveFlags 0x83      S7AreaMK
    #define daveDB 0x84	       S7AreaDB /* data blocks */

DB Address：
    V   daveDB      1
    I/E daveInputs  0
    Q   daveOutputs 0
    M/F daveFlags   0
    T   daveTimer200    0
    C/Z daveCounter200  0
    S   daveSysFlags    0
    A   daveAnaOut/daveAnaIn    0
    P   daveP       0
Point：
    DB2,REAL10,VT_R4,192.168.0.2,1,3
    I0.6
'''
import logging

import snap7
import ctypes
import struct
import time
from snap7.snap7types import S7DataItem, S7WLByte

from threading import Thread
from .base import BasePoint, BaseDriver, PointTableDict

'''
    pip install python-snap7==0.10
'''

# Sample Point
class SiemensS7Point(BasePoint):

    def __init__(self, point_writable: bool, point_name: str, point_device_address: str, point_rack: int,
                 point_slot: int, point_address: str, point_scale: float, point_description: str = ''):
        super().__init__('plcs7', point_writable, point_name, point_description)

        self.point_device_address = point_device_address
        self.point_rack = point_rack  # rack
        self.point_slot = point_slot  # slot
        self.point_address = point_address
        self.point_scale = point_scale
        self.point_set_value = 0

    @property
    def get_point_device_address(self):
        return self.point_device_address

    @property
    def get_point_rack(self):
        return self.point_rack

    @property
    def get_point_slot(self):
        return self.point_slot

    @property
    def get_point_address(self):
        return self.point_address

    @property
    def get_plc_area_id(self):
        if self.point_address.find('DB') == 0:  # DB
            return 0x84
        else:
            if self.point_address.find('V') == 0:
                return 0x84
            elif self.point_address.find('I') == 0 or self.point_address.find('E') == 0:
                return 0x81
            elif self.point_address.find('Q') == 0:
                return 0x82
            elif self.point_address.find('M') == 0 or self.point_address.find('F') == 0:
                return 0x83
        return 0x84

    @property
    def get_plc_db(self):
        if self.point_address.find('DB') == 0:
            area_info = self.point_address.split(',')
            if len(area_info) == 2:
                db_info = area_info[0]
                if len(db_info) > 2:
                    return int(float(db_info[2:]))
        else:
            if self.point_address.find('V') == 0:
                return 1
        return 0

    @property
    def get_plc_data_type(self):
        if self.point_address.find('DB') == 0:
            area_info = self.point_address.split(',')
            if len(area_info) == 2:
                data_info = area_info[1]  # REAL10
                if data_info.find('INT') == 0:
                    return 'VT_I2'
                elif data_info.find('DINT') == 0:
                    return 'VT_I4'
                elif data_info.find('REAL') == 0:
                    return 'VT_R4'
                elif data_info.find('BOOL') == 0:
                    return 'VT_BOOL'
        else:
            type_letter = self.point_address[1:2]
            if type_letter == 'B':
                pos = self.point_address.find('.')
                if pos > 0:
                    return 'VT_BOOL'
                else:
                    return 'VT_I1'
            elif type_letter == 'W':
                return 'VT_I2'
            elif type_letter == 'D':
                return 'VT_I4'
        return 'VT_BOOL'

    @property
    def get_plc_data_length(self):
        if self.point_address.find('DB') == 0:
            area_info = self.point_address.split(',')
            if len(area_info) == 2:
                data_info = area_info[1]  # REAL10
                if data_info.find('INT') == 0:
                    return 2
                elif data_info.find('DINT') == 0:
                    return 4
                elif data_info.find('REAL') == 0:
                    return 4
                elif data_info.find('BOOL') == 0:
                    return 1
        else:
            type_letter = self.point_address[1:2]
            if type_letter == 'B':
                return 1
            elif type_letter == 'W':
                return 2
            elif type_letter == 'D':
                return 4
        return 1

    @property
    def get_plc_data_start(self):
        if self.point_address.find('DB') == 0:
            area_info = self.point_address.split(',')
            if len(area_info) == 2:
                data_info = area_info[1]  # REAL10
                if data_info.find('INT') == 0:
                    return int(float(data_info[3:]))
                elif data_info.find('DINT') == 0:
                    return int(float(data_info[4:]))
                elif data_info.find('REAL') == 0:
                    return int(float(data_info[4:]))
                elif data_info.find('BOOL') == 0:  # BOOL25.1
                    pos = data_info.find('.')
                    if pos >= 4:
                        return int(float(data_info[4:pos]))
        else:
            data_info = self.point_address[1:]
            type_letter = data_info[0:1]
            if type_letter in ['D', 'B', 'W']:
                data_info = data_info[1:]
            pos = data_info.find('.')
            if pos > 0:
                return int(float(data_info[:pos]))
            else:
                return int(float(data_info))
        return 0

    @property
    def get_plc_data_address(self):
        if self.point_address.find('DB') == 0:
            area_info = self.point_address.split(',')
            if len(area_info) == 2:
                data_info = area_info[1]  # REAL10
                if data_info.find('INT') == 0:
                    return int(float(data_info[3:]))
                elif data_info.find('DINT') == 0:
                    return int(float(data_info[4:]))
                elif data_info.find('REAL') == 0:
                    return int(float(data_info[4:]))
                elif data_info.find('BOOL') == 0:  # BOOL25.1
                    pos = data_info.find('.')
                    if pos >= 4:
                        return int(float(data_info[pos + 1:]))
        else:
            data_info = self.point_address[1:]
            type_letter = data_info[0:1]
            if type_letter in ['D', 'B', 'W']:
                data_info = data_info[1:]
            pos = data_info.find('.')
            if pos > 0:
                return int(float(data_info[pos + 1:]))
            else:
                return int(float(data_info))
        return 0

    @property
    def get_point_scale(self):
        if self.point_scale == 0:
            return 1
        return self.point_scale

    @property
    def get_point_set_value(self):
        return self.point_set_value

    def set_point_set_value(self, point_set_value):
        self.point_set_value = point_set_value


# SiemensS7
class SiemensS7Engine(Thread):

    def __init__(self, control_mode: str, device_address: str, dict_point: dict, multi_read: int, cmd_interval: float,
                 send_timeout: int, rec_timeout: int):
        Thread.__init__(self)

        self.control_mode = control_mode  # read/write
        self.device_address = device_address
        self.dict_point = dict_point
        self.rack = -1
        self.slot = -1

        ##modbus connect param ##########################
        self.multi_read = multi_read
        self.cmd_interval = cmd_interval
        self.send_timeout = send_timeout  # ms
        self.rec_timeout = rec_timeout  # ms
        ###########################

        self.dict_value = {}
        self.plc_value_dict = {}
        self.new_point_list = []
        self.plc_s7_data_item_list = []
        self.plc_s7_data_item_dict = {}
        self.plc_client = None
        self.set_result_dict = {}

    def _close_plc(self):
        try:
            if self.plc_client:
                self.plc_client.disconnect()
                self.plc_client.destroy()
        except Exception as e:
            logging.error(f"plc({self.device_address}) close fail({e.__str__()})")
        self.plc_client = None

    def _get_plc_info(self, device_address: str) -> dict:
        plc_info = {}
        try:
            if len(device_address) > 0:
                server_ist = device_address.split('/')
                if len(server_ist) == 1:  # IP
                    if self.slot == -1 and self.rack == -1:
                        plc_info = {'host': server_ist[0], 'port': 102, 'rack': self.rack, 'slot': self.slot,
                                    'type': 'plc200'}
                    else:
                        plc_info = {'host': server_ist[0], 'port': 102, 'rack': self.rack, 'slot': self.slot,
                                    'type': ''}
                elif len(server_ist) == 2:  # IP/port
                    if self.slot == -1 and self.rack == -1:
                        plc_info = {'host': server_ist[0], 'port': int(float(server_ist[1])), 'rack': self.rack,
                                    'slot': self.slot, 'type': 'plc200'}
                    else:
                        plc_info = {'host': server_ist[0], 'port': int(float(server_ist[1])), 'rack': self.rack,
                                    'slot': self.slot, 'type': ''}
        except Exception as e:
            raise e
        return plc_info

    def _get_client(self):
        try:
            if self.plc_client:
                if self.plc_client.get_connected() == False:
                    self._close_plc()

            if self.plc_client == None:
                plc_info = self._get_plc_info(self.device_address)
                if 'type' in plc_info.keys():
                    plc_type = plc_info['type']

                    self.plc_client = snap7.client.Client()
                    if self.plc_client:
                        if self.send_timeout > 0:
                            self.plc_client.set_param(snap7.snap7types.SendTimeout, self.send_timeout)
                        if self.rec_timeout > 0:
                            self.plc_client.set_param(snap7.snap7types.RecvTimeout, self.rec_timeout)

                    if plc_type == 'plc200':
                        self.plc_client.connect200(plc_info['host'], plc_info['port'])
                    else:
                        self.plc_client.connect(plc_info['host'], plc_info['rack'], plc_info['slot'], plc_info['port'])
        except Exception as e:
            logging.error(f"plc({self.device_address}) connect fail({e.__str__()})")
            self._close_plc()
        return self.plc_client

    def _sort_point_by_device(self):
        try:
            if len(self.dict_point) > 0:
                self.new_point_list = []

                for point_name in self.dict_point.keys():
                    point = self.dict_point[point_name]
                    self.rack = point.get_point_rack
                    self.slot = point.get_point_slot

                    self.new_point_list.append(
                        [point.get_plc_area_id, point.get_plc_db, point.get_plc_data_start, point.get_plc_data_length,
                         point])

                self.new_point_list.sort(key=lambda t: (t[0], t[1], t[2]))

                for point in self.new_point_list:
                    item = S7DataItem()
                    item.Area = ctypes.c_int32(point[0])
                    item.WordLen = ctypes.c_int32(S7WLByte)
                    item.Result = ctypes.c_int32(0)
                    item.DBNumber = ctypes.c_int32(point[1])
                    item.Start = ctypes.c_int32(point[2])
                    item.Amount = ctypes.c_int32(point[3])  # reading a REAL, 4 bytes

                    # create buffers to receive the data
                    # use the Amount attribute on each item to size the buffer

                    buffer = ctypes.create_string_buffer(item.Amount)

                    # cast the pointer to the buffer to the required type
                    pBuffer = ctypes.cast(ctypes.pointer(buffer), ctypes.POINTER(ctypes.c_uint8))
                    item.pData = pBuffer

                    s7_key = '%u_%u_%u_%u' % (item.Area, item.DBNumber, item.Start, item.Amount)
                    if s7_key not in self.plc_s7_data_item_dict.keys():
                        self.plc_s7_data_item_list.append(item)
                        self.plc_s7_data_item_dict[s7_key] = []

                    self.plc_s7_data_item_dict[s7_key].append(point[4])
                return True
        except Exception as e:
            raise e
        return False

    def _ping_target(self):
        return True

    def _update_point_value(self):
        try:
            self.plc_value_dict = {}

            if self._ping_target() == True:
                if len(self.plc_s7_data_item_list) > 0:
                    if self._get_client() != None:
                        multi_item_list = []
                        for s7Item in self.plc_s7_data_item_list:
                            multi_item_list.append(s7Item)
                            if len(multi_item_list) >= self.multi_read:
                                self._send_read_mutil(multi_item_list)
                                multi_item_list = []

                        if len(multi_item_list) > 0:
                            self._send_read_mutil(multi_item_list)
        except Exception as e:
            raise e

    def _send_read_mutil(self, s7_item_list):
        try:
            if len(s7_item_list) > 0 and self.plc_client:
                s7_item_byref = (S7DataItem * len(s7_item_list))()
                for index in range(0, len(s7_item_list)):
                    s7_item_byref[index] = s7_item_list[index]

                result, s7_data_items = self.plc_client.read_multi_vars(s7_item_byref)
                for s7_item in s7_data_items:
                    if s7_item.Result:
                        raise Exception(str(s7_item.Result))
                    else:
                        self._conver_data_value(s7_item)
        except Exception as e:
            logging.error(f"plc({self.device_address}) read fail({e.__str__()})")
        time.sleep(self.cmd_interval)

    def _conver_data_value(self, s7_item):
        try:
            s7_key = '%u_%u_%u_%u' % (s7_item.Area, s7_item.DBNumber, s7_item.Start, s7_item.Amount)
            if s7_key in self.plc_s7_data_item_dict.keys():
                plc_point_list = self.plc_s7_data_item_dict[s7_key]
                for plc_point in plc_point_list:
                    plc_data_type = plc_point.get_plc_data_type
                    plc_data_index = plc_point.get_plc_data_start - s7_item.Start
                    if plc_data_type == 'VT_BOOL':
                        plc_data_address = plc_point.get_plc_data_address
                        wValue = snap7.util.get_bool(s7_item.pData, plc_data_index, plc_data_address)
                        if wValue == True:
                            wValue = '1'
                        else:
                            wValue = '0'
                        self.plc_value_dict[plc_point.get_point_name] = str(wValue)
                    elif plc_data_type == 'VT_I1':
                        iValue = struct.unpack('>b', ctypes.string_at(s7_item.pData, s7_item.Amount))[0]
                        self.plc_value_dict[plc_point.get_point_name] = str(iValue)
                    elif plc_data_type == 'VT_UI1':
                        iValue = struct.unpack('>B', ctypes.string_at(s7_item.pData, s7_item.Amount))[0]
                        self.plc_value_dict[plc_point.get_point_name] = str(iValue)
                    elif plc_data_type == 'VT_I2':
                        iValue = struct.unpack('>h', ctypes.string_at(s7_item.pData, s7_item.Amount))[0]
                        self.plc_value_dict[plc_point.get_point_name] = str(iValue)
                    elif plc_data_type == 'VT_UI2':
                        iValue = struct.unpack('>H', ctypes.string_at(s7_item.pData, s7_item.Amount))[0]
                        self.plc_value_dict[plc_point.get_point_name] = str(iValue)
                    elif plc_data_type == 'VT_I4':
                        lValue = struct.unpack('>i', ctypes.string_at(s7_item.pData, s7_item.Amount))[0]
                        self.plc_value_dict[plc_point.get_point_name] = str(lValue)
                    elif plc_data_type == 'VT_UI4':
                        lValue = struct.unpack('>I', ctypes.string_at(s7_item.pData, s7_item.Amount))[0]
                        self.plc_value_dict[plc_point.get_point_name] = str(lValue)
                    elif plc_data_type == 'VT_I8':
                        lValue = struct.unpack('>l', ctypes.string_at(s7_item.pData, s7_item.Amount))[0]
                        self.plc_value_dict[plc_point.get_point_name] = str(lValue)
                    elif plc_data_type == 'VT_UI8':
                        lValue = struct.unpack('>L', ctypes.string_at(s7_item.pData, s7_item.Amount))[0]
                        self.plc_value_dict[plc_point.get_point_name] = str(lValue)
                    elif plc_data_type == 'VT_R4':
                        fValue = struct.unpack('>f', ctypes.string_at(s7_item.pData, s7_item.Amount))[0]
                        self.plc_value_dict[plc_point.get_point_name] = str(fValue)
                    elif plc_data_type == 'VT_R8':
                        fValue = struct.unpack('>d', ctypes.string_at(s7_item.pData, s7_item.Amount))[0]
                        self.plc_value_dict[plc_point.get_point_name] = str(fValue)
                    else:
                        pass
        except Exception as e:
            raise e

    def _conver_set_data_value(self, reading, plc_point, value):
        try:
            plc_data_type = plc_point.get_plc_data_type
            if plc_data_type == 'VT_BOOL':
                plc_data_address = plc_point.get_plc_data_address
                snap7.util.set_bool(reading, 0, plc_data_address, int(str(value)))
            elif plc_data_type == 'VT_I1':
                reading = bytearray(1)
                reading[0:1] = struct.unpack('B', struct.pack('>b', int(str(value))))
            elif plc_data_type == 'VT_UI1':
                reading = bytearray(1)
                reading[0:1] = struct.unpack('B', struct.pack('>B', int(str(value))))
            elif plc_data_type == 'VT_I2':
                reading = bytearray(2)
                reading[0:2] = struct.unpack('2B', struct.pack('>h', int(str(value))))
            elif plc_data_type == 'VT_UI2':
                reading = bytearray(2)
                reading[0:2] = struct.unpack('2B', struct.pack('>H', int(str(value))))
            elif plc_data_type == 'VT_I4':
                reading = bytearray(4)
                reading[0:4] = self._byte_trans_data_format_4(struct.unpack('4B', struct.pack('>i', int(str(value)))),
                                                              'abcd')
            elif plc_data_type == 'VT_UI4':
                reading = bytearray(4)
                reading[0:4] = self._byte_trans_data_format_4(struct.unpack('4B', struct.pack('>I', int(str(value)))),
                                                              'abcd')
            elif plc_data_type == 'VT_I8':
                reading = bytearray(8)
                reading[0:8] = self._byte_trans_data_format_8(struct.unpack('8B', struct.pack('>l', int(str(value)))),
                                                              'abcd')
            elif plc_data_type == 'VT_UI8':
                reading = bytearray(8)
                reading[0:8] = self._byte_trans_data_format_8(struct.unpack('8B', struct.pack('>L', int(str(value)))),
                                                              'abcd')
            elif plc_data_type == 'VT_R4':
                reading = bytearray(4)
                reading[0:4] = self._byte_trans_data_format_4(struct.unpack('4B', struct.pack('<f', float(str(value)))),
                                                              'abcd')
            elif plc_data_type == 'VT_R8':
                reading = bytearray(8)
                reading[0:8] = self._byte_trans_data_format_8(struct.unpack('8B', struct.pack('>d', float(str(value)))),
                                                              'abcd')
            else:
                pass
        except Exception as e:
            raise e
        return reading

    #
    def _byte_trans_data_format_4(self, value, data_format='abcd'):
        buffer = bytearray(4)
        if data_format == 'abcd':
            buffer[0] = value[3]
            buffer[1] = value[2]
            buffer[2] = value[1]
            buffer[3] = value[0]
        elif data_format == 'bacd':
            buffer[0] = value[2]
            buffer[1] = value[3]
            buffer[2] = value[0]
            buffer[3] = value[1]
        elif data_format == 'cdab':
            buffer[0] = value[1]
            buffer[1] = value[0]
            buffer[2] = value[3]
            buffer[3] = value[2]
        elif data_format == 'dcba':
            buffer[0] = value[0]
            buffer[1] = value[1]
            buffer[2] = value[2]
            buffer[3] = value[3]
        return buffer

    def _byte_trans_data_format_8(self, value, data_format='abcd'):
        buffer = bytearray(4)
        if data_format == 'abcd':
            buffer[0] = value[7]
            buffer[1] = value[6]
            buffer[2] = value[5]
            buffer[3] = value[4]
            buffer[4] = value[3]
            buffer[5] = value[2]
            buffer[6] = value[1]
            buffer[7] = value[0]
        elif data_format == 'badc':
            buffer[0] = value[6]
            buffer[1] = value[7]
            buffer[2] = value[4]
            buffer[3] = value[5]
            buffer[4] = value[2]
            buffer[5] = value[3]
            buffer[6] = value[0]
            buffer[7] = value[1]
        elif data_format == 'cdab':
            buffer[0] = value[1]
            buffer[1] = value[0]
            buffer[2] = value[3]
            buffer[3] = value[2]
            buffer[4] = value[5]
            buffer[5] = value[4]
            buffer[6] = value[7]
            buffer[7] = value[6]
        elif data_format == 'dcba':
            buffer[0] = value[0]
            buffer[1] = value[1]
            buffer[2] = value[2]
            buffer[3] = value[3]
            buffer[4] = value[4]
            buffer[5] = value[5]
            buffer[6] = value[6]
            buffer[7] = value[7]
        return buffer

    def run(self):
        try:
            self._sort_point_by_device()

            if self.control_mode == 'write':
                self._set_point_value()
                self._close_plc()
            else:
                self._update_point_value()
                self._close_plc()
        except Exception as e:
            raise e

    def get_values(self):
        return self.plc_value_dict

    def get_set_result(self):
        return self.set_result_dict

    def _set_point_value(self):
        try:
            self.set_result_dict = {}
            if self._get_client() != None:
                for point_name in self.dict_point.keys():
                    plc_point = self.dict_point[point_name]
                    point_value = plc_point.get_point_set_value
                    if self._ping_target() == True:
                        self.set_result_dict[point_name] = self._set_write_cmd(plc_point, point_value)
                    else:
                        self.set_result_dict[point_name] = False
        except Exception as e:
            raise e

    def _set_write_cmd(self, plc_point, point_value):
        set_result = False
        try:
            if self.plc_client:
                reading = bytearray(1)
                if plc_point.get_plc_data_type == 'VT_BOOL':
                    reading = self.plc_client.read_area(plc_point.get_plc_area_id, plc_point.get_plc_db,
                                                        plc_point.get_plc_data_start, plc_point.get_plc_data_length)
                reading = self._conver_set_data_value(reading, plc_point, point_value)
                set_result = self.plc_client.write_area(plc_point.get_plc_area_id, plc_point.get_plc_db,
                                                        plc_point.get_plc_data_start, reading)
        except Exception as e:
            logging.error(f"plc({self.device_address}) write({plc_point.get_point_name}) fail({e.__str__()})")
        return set_result


# Sample Driver
class SiemensS7Driver(BaseDriver):

    def __init__(self, dict_config: dict, dict_point: PointTableDict):
        super().__init__(dict_config, dict_point)

        ##siemenss7 connect param ##########################
        self.siemenss7_multi_read = 100
        self.siemenss7_cmd_interval = 0.3
        self.siemenss7_send_timeout = 15
        self.siemenss7_rec_timeout = 3500  # ms
        ###########################

        self.dict_siemenss7_point = {}

        self.configure()

    def __del__(self):
        super().__del__()

    def exit(self):
        pass

    def configure(self):
        try:
            # config
            self.siemenss7_multi_read = int(self.dict_config.get("multi_read", "20"))
            self.siemenss7_cmd_interval = float(self.dict_config.get("cmd_interval", "0.3"))
            self.siemenss7_send_timeout = int(self.dict_config.get("send_timeout", "15"))
            self.siemenss7_rec_timeout = int(self.dict_config.get("rec_timeout", "3500"))

            # csv
            for point_name in self.dict_point.keys():
                self.dict_siemenss7_point[point_name] = SiemensS7Point(
                    bool(str(self.dict_point[point_name]['point_writable'])),
                    str(self.dict_point[point_name]['point_name']), str(self.dict_point[point_name]['point_device_address']),
                    int(str(self.dict_point[point_name]['point_rack'])), int(str(self.dict_point[point_name]['point_slot'])),
                    str(self.dict_point[point_name]['point_address']), 1)

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
            siemenss7_device_dict = {}
            for point_name in dict_point.keys():
                if point_name in self.dict_siemenss7_point.keys():
                    siemenss7_point = self.dict_siemenss7_point[point_name]
                    device_address = siemenss7_point.get_point_device_address
                    if device_address not in siemenss7_device_dict.keys():
                        siemenss7_device_dict[device_address] = {}
                        siemenss7_device_dict[device_address][point_name] = siemenss7_point

            if len(siemenss7_device_dict) > 0:
                result_dict = self._read_siemenss7_values(siemenss7_device_dict)
        except Exception as e:
            raise e
        return result_dict

    def _scrap_points(self) -> dict:
        result_dict = {}
        try:
            siemenss7_device_dict = {}  #
            for point_name in self.dict_siemenss7_point.keys():
                siemenss7_point = self.dict_siemenss7_point[point_name]
                device_address = siemenss7_point.get_point_device_address
                if device_address not in siemenss7_device_dict.keys():
                    siemenss7_device_dict[device_address] = {}
                siemenss7_device_dict[device_address][point_name] = siemenss7_point

            if len(siemenss7_device_dict) > 0:
                result_dict = self._read_siemenss7_values(siemenss7_device_dict)
        except Exception as e:
            raise e
        return result_dict

    def set_points(self, dict_point: dict) -> dict:
        set_result_dict = {}
        try:
            siemenss7_device_dict = {}
            for point_name in dict_point.keys():
                if point_name in self.dict_siemenss7_point.keys():
                    siemenss7_point = self.dict_siemenss7_point[point_name]
                    device_address = siemenss7_point.get_point_device_address
                    if device_address not in siemenss7_device_dict.keys():
                        siemenss7_device_dict[device_address] = {}
                    point_value = dict_point[point_name]
                    if siemenss7_point.get_point_scale != 1 and siemenss7_point.get_point_scale != 0:
                        point_value = '%.2f' % (point_value * siemenss7_point.get_point_scale)
                    siemenss7_point.set_point_set_value(point_value)
                    siemenss7_device_dict[device_address][point_name] = siemenss7_point

            if len(siemenss7_device_dict) > 0:
                set_result_dict = self._write_siemenss7_values(siemenss7_device_dict)
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
            pass
        except Exception as e:
            raise e
        return search_point

    def _read_siemenss7_values(self, siemenss7_device_dict: dict) -> dict:
        result_dict = {}
        try:
            siemenss7_client_thread = []
            for device_address in siemenss7_device_dict.keys():
                siemenss7_client = SiemensS7Engine('read', device_address, siemenss7_device_dict[device_address],
                                                       self.siemenss7_multi_read, self.siemenss7_cmd_interval,
                                                       self.siemenss7_send_timeout, self.siemenss7_rec_timeout)
                siemenss7_client.setDaemon(True)
                siemenss7_client.start()
                siemenss7_client_thread.append(siemenss7_client)

            for siemenss7_client in siemenss7_client_thread:
                siemenss7_client.join()
                result_dict.update(siemenss7_client.get_values())

        except Exception as e:
            raise e
        return result_dict

    def _write_siemenss7_values(self, siemenss7_device_dict: dict) -> dict:
        result_dict = {}
        try:
            siemenss7_client_thread = []
            for device_address in siemenss7_device_dict.keys():
                siemenss7_client = SiemensS7Engine('write', device_address, siemenss7_device_dict[device_address],
                                                       self.siemenss7_multi_read, self.siemenss7_cmd_interval,
                                                       self.siemenss7_send_timeout, self.siemenss7_rec_timeout)
                siemenss7_client.setDaemon(True)
                siemenss7_client.start()
                siemenss7_client_thread.append(siemenss7_client)

            for siemenss7_client in siemenss7_client_thread:
                siemenss7_client.join()
                result_dict.update(siemenss7_client.get_set_result())

        except Exception as e:
            raise e
        return result_dict