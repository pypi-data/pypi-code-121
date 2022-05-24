'''MIVA Module'''
import binascii
import re
import json
import struct
import time
import datetime
import sys
import traceback
import platform
# from threading import Thread
from threading import Lock
from os import path, system
import serial
from pyZynoUnifiedDrivers.module_utils import crc32c, check_sum, isfloat, int_to_time_str
# from module_utils import byte_fill
# from module_event_log import EventLogMonitor

# Define Key Pressing
_NONE_KEY = '0'
_UP_KEY = '1'
_DOWN_KEY = '2'
_INFO_KEY = '3'
_OK_KEY = '4'
_POWER_KEY = '5'
_RUN_KEY = '6'
_BOLUS_KEY = '7'
_STOP_KEY = '8'

_SHORT_PRESS = '0'
_LONG_PRESS = '1'
_MID_PRESS = '2'

#
_BAUD_RATE = 9600
_BYTE_SIZE = 8
_STOPBITS = 1
_PARITY = serial.PARITY_NONE
_FLOW_CONTROL = 0
_TIMEOUT = 0.1
_WRITE_TIMEOUT = 0.1
_ENCRYPTION_KEY = b'\x01\x23\x45\x67\x89\xAB\xCD\xEF' + \
                  b'\x01\x23\x45\x67\x89\xAB\xCD\xEF' + \
                  b'\x01\x23\x45\x67\x89\xAB\xCD\xEF' + \
                  b'\x01\x23\x45\x67\x89\xAB\xCD\xEF'

# Define Flash Structure the same as MIVA pump
FLASH_PAGE_SIZE = 4096
EVENT_LOG_NUMBER_OF_PAGES = 169
EVENT_LOG_SIZE = 16
# 4096 * 169 / 16 = 43264 (A900)
EVENT_LOG_NUMBER_OF_EVENTS = int((FLASH_PAGE_SIZE * EVENT_LOG_NUMBER_OF_PAGES) / EVENT_LOG_SIZE)
# Infusion Data Structure Occupies How Many Event Logs
EVENT_LOGS_PER_INFUSION_DATA_LOG = 16
# Define Regular Expressions
re_scpi_get_cmd = r'^((:[0-9a-zA-Z_]+)+(\?))$'
re_scpi_set_cmd = r'^((:[a-zA-Z]+)+)(\s+)?(\d+)?(\.)?(\d+)?$'
re_get_key_list = r'(:)(key)(:)(list)(\?)((\s+)?(>)(\s+)?([a-z0-9_]+\.txt))?$'
re_get_screenshot = r'(screen(shot)?)((\s+)?(>)(\s+)?(.+\.(png|txt|jpg|json)))?$'
re_compare_screenshot = r'(screen(shot)?)(\s+)?(==)(\s+)?(.+\.(txt|json|jpg|png))?$'
re_clear_key_list = r'(:)(key)(:)(list)(:)(clear)$'
re_compare_parameters = r'^((:[a-zA-Z_]+)+(\?))(\s*)(==|>|>=|<=|<|!=)(\s*)(\S+)(\s+)?(delta(\s*)?==(\s*)?(\d+(\.\d*)?|\.\d+)(%)?)?(\s+)?$'
re_compare_list = r'((:[a-zA-Z]+)+(\?))(\s*)(==|>|>=|<=|<|!=)(\s*)(\[.*\])(\s*)'
re_query_event_timestamp = r'(:)(time(stamp)?)(:)([A-Za-z_]+)(\?)'
re_search_for_event = r'(:)(event(log)?)(:)([A-Za-z_]+)(\?)'
re_query_event_list = r'(:)(event(log)?)(:)(\d+)(\?)'
re_compare_dict_equal = r'^((:[a-zA-Z_]+)+(\?))(\s*)(==)(\s*)(\{.*\})(\s*)$'
re_compare_str = r'^((:[a-zA-Z_]+)+(\?))(\s*)(==|>|>=|<=|<|!=)(\s*)\"(.*)\"(\s+)?$' 
re_compare_str_equal = r'^((:[a-zA-Z_]+)+(\?))(\s*)(==)(\s*)\"(.*)\"(\s+)?$'
re_compare_scpi_return_number = r'^((:[a-zA-Z_]+)+(\?))(\s*)(==|>|>=|<=|<|!=)(\s*)((:[a-zA-Z_]+)+(\?))(\s+)?(delta(\s*)?==(\s*)?(\d+(\.\d*)?|\.\d+)(%)?)?(\s+)?$'
re_query_lockout = r'^(:)(prot(ocol)?|infu(sion)?)(:)(ld|db|sd|ed)(:)(lock(out)?)((:)(min|max|def(ault)?))?(\?)(\s+)?$'


class Key:
    '''Key Definition'''
    
    # Define Key Pressing
    NONE_KEY = '0'
    UP_KEY = '1'
    DOWN_KEY = '2'
    INFO_KEY = '3'
    OK_KEY = '4'
    POWER_KEY = '5'
    RUN_KEY = '6'
    BOLUS_KEY = '7'
    SHORT_PRESS = '0'
    LONG_PRESS = '1'


#
_BAUD_RATE = 9600
_BYTE_SIZE = 8
_STOPBITS = 1
_PARITY = serial.PARITY_NONE
_FLOW_CONTROL = 0
_TIMEOUT = 0.1
_WRITE_TIMEOUT = 0.1
_ENCRYPTION_KEY = b'\x01\x23\x45\x67\x89\xAB\xCD\xEF' + \
                  b'\x01\x23\x45\x67\x89\xAB\xCD\xEF' + \
                  b'\x01\x23\x45\x67\x89\xAB\xCD\xEF' + \
                  b'\x01\x23\x45\x67\x89\xAB\xCD\xEF'


def scan_serial_ports():
    '''Scan Serial Port'''
    ports = []
    if platform.system() == 'Linux':
        ports = ['/dev/ttyUSB%s' % (i) for i in range(0, 256)]
    else:
        ports = ['com%s' % (i) for i in range(1, 256)]
    result = []
    for port in ports:
        try:
            ser = serial.Serial(port)
            ser.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


def build_message(command):
    '''Build Message to Be Sent to Pump Based on Command
        @param command R/W+Index+Parameters
        @return message that can be recognized by pump
    '''
    frame_start = 0x02
    frame_end = 0x03
    crc = check_sum(command).upper()
    #
    message = []
    #
    message.append(frame_start)
    #
    for each_char in command:
        message.append(ord(each_char))
    #
    for each_char in crc:
        message.append(ord(each_char))
    #
    message.append(frame_end)
    #
    return message


def get_infusion_data_frame(event_log_hex):
    '''get infusion data frame
        -- DATA_LOG_BEGIN 1
        16 x 16 bytes protocol data in between
        -- DATA_LOG_END 2    
    '''
    infusion_data_frame_id = int(event_log_hex[10:12], 16)
    switcher = {
        1: 'INFUSION_DATA_BEGIN',
        2: 'INFUSION_DATA_END'
    }
    return switcher.get(infusion_data_frame_id, "Unknown Status ({})".format(infusion_data_frame_id))


def get_battery_status(event_log_hex):
    '''get battery status'''
    battery_status_id = int(event_log_hex[10:14], 16)
    switcher = {
        # 0: 'BATTERY_NO_UPDATE',
        1: 'BATTERY_MEDIUM',
        2: 'BATTERY_LOW',
        4: 'BATTERY_DEPLETED',
        8: 'BATTERY_RESET',
        16: 'BATTERY_AC',
        32: 'BATTERY_HIGH',
        64: 'BATTERY_NEW',
        128: 'BATTERY_OVER_UPPER_LIMIT',
        256: 'BATTERY_EMPTY',
        512: 'BATTERY_UNDER_LOWER_LIMIT'
    }
    # get() method of dictionary data type returns  
    # value of passed argument if it is present  
    # in dictionary otherwise second argument will 
    # be assigned as default value of passed argument
    battery_status_list = []
    if battery_status_id == 0:
        battery_status_list = ['BATTERY_NO_UPDATE']
    else:
        for i in range(len(switcher)):
            battery_status = switcher.get(battery_status_id & (2 ** i), "Unknown Status")
            if battery_status != "Unknown Status":
                battery_status_list.append(battery_status + ' (b\'' + '{0:b}'.format(battery_status_id & (2 ** i)).zfill(8) + '\')')
        if battery_status_list == []:
            battery_status_list = ['Unknown Status (b\'' + '{0:b}'.format(event_log_hex[10:14]).zfill(8) + '\')']
    return battery_status_list


def get_send_library_crc(library_bytes):
    library_block_begin_index = 64
    library_block_end_index = 1152
    block_size = 64
    # The library Block range is : [64:1152]
    # The library Block size should be [1152 - 64 = 1088]
    # Calculate the Digital Signature (Checksum)
    library_hex = library_bytes.hex().upper()
    crc = 0x0
    total_blocks = library_block_end_index - library_block_begin_index
    for i in range(total_blocks):
        # Check to see if the whole block is all [FF]
        # If the whole block is all FF then don't calculate the checksum for the block
        # And do not send the block to the pump in order to save time
        all_empty_bytes = True
        for each_byte in library_bytes[i * block_size:(i + 1) * block_size]:
            if each_byte != 0xFF:
                all_empty_bytes = False
                break
        if (not all_empty_bytes):
            crc = crc32c(crc, library_hex[i * block_size * 2: (i + 1) * block_size * 2])
    return crc


def get_infusion_pause_vinf(event_log_hex):
    ''' get VINF when infusion paused (ml)'''
    pause_vinf_hex = event_log_hex[14:22]
    pause_vinf_float = struct.unpack('!f', bytes.fromhex(pause_vinf_hex))[0]
    return pause_vinf_float

    
def get_infusion_limit_type(event_log_hex):
    ''' get infusion limit reached type'''
    limit_reached_type = int(event_log_hex[10:14], 16);
    switcher = {
        1: 'MAX_PER_HR',
        2: 'MAX_PER_INTERVAL',
        4: 'CLEARED'
    }
    return switcher.get(limit_reached_type, "Unknown Type ({})".format(limit_reached_type))


def get_authentication_code(event_log_hex):
    '''get authentication code'''
    authentication_code = int(event_log_hex[10:14], 16);
    return authentication_code


def get_bolus_type(event_log_hex):
    '''get bolus type'''
    bolus_type_id = int(event_log_hex[10:12], 16);
    switcher = {
        1: 'AUTO_BOLUS',
        # 'DEMAND_BOLUS'
        2: 'EXTRA_BOLUS',
        8: 'CLINICIAN_BOLUS'
    }
    return switcher.get(bolus_type_id, "Unknown Type ({})".format(bolus_type_id))


def get_bolus_attempted_number(event_log_hex):
    '''get bolus attempted number'''
    number_of_bolus_attempted = int(event_log_hex[12:14], 16);
    return number_of_bolus_attempted


def get_occlusion_type(event_log_hex):
    '''get occlusion type'''
    occlusion_type_id = int(event_log_hex[10:14], 16);
    switcher = {
        1: 'UPSTREAM_OCCLUSION',
        2: 'DOWNSTREAM_OCCLUSION',
        4: 'OCCLUSION_CLEARED'
    }
    return switcher.get(occlusion_type_id, "Unknown Type ({})".format(occlusion_type_id))


def get_delay_end_type(event_log_hex):
    '''get delay end type'''
    delay_end_type_id = int(event_log_hex[10:14], 16);
    switcher = {
        1: 'NORMAL_END',
        2: 'SKIPPED'        
    }
    return switcher.get(delay_end_type_id, "Unknown Type ({})".format(delay_end_type_id))


def get_pump_limit_type(event_log_hex):
    '''get limit type'''
    limit_type = int(event_log_hex[10:14], 16);
    switcher = {
        1: 'PRODUCT_LIFE_REACHED_SEEK_REPLACEMENT_PUMP',
        2: 'SERVICE_LIFE_REACHED_DUE_FOR_SERVICE'        
    }
    return switcher.get(limit_type, "Unknown Type ({})".format(limit_type))


def get_eventlog_battery_voltage(event_log_hex):
    '''get battery voltage (V)'''
    battery_voltage_hex = event_log_hex[14:22]
    battery_voltage_float = struct.unpack('!f', bytes.fromhex(battery_voltage_hex))[0]
    return float('{0:.2f}'.format(battery_voltage_float))


def get_eventlog_battery_vinf(event_log_hex):
    '''get battery VINF (mL)'''
    battery_vinf_hex = event_log_hex[22:30]
    battery_vinf_float = struct.unpack('!f', bytes.fromhex(battery_vinf_hex))[0]
    return float('{0:.1f}'.format(battery_vinf_float))


def get_battery_charge(event_log_hex):
    '''get battery charge (V)'''
    battery_charge_hex = event_log_hex[14:22]
    battery_charge_float = struct.unpack('!f', bytes.fromhex(battery_charge_hex))[0]
    return float('{0:.2f}'.format(battery_charge_float))


def get_firmware_error_type(event_log_hex):
    '''get firmware error type'''
    firmware_error_type_id = int(event_log_hex[10:14], 16);
    switcher = {
        1: 'FLASH_CRC_ERROR',
        2: 'CORRUPTED_LIB'        
    }
    return switcher.get(firmware_error_type_id, "Unknown Type ({})".format(firmware_error_type_id))


def get_firmware_error_file(event_log_hex):
    '''get firmware error file'''
    firmware_error_file_id = int(event_log_hex[14:16], 16);
    
    switcher = {
        1: 'infusion_info.c',
        2: 'infusion_task_manage.c',
        3: 'navigation.c',
        4: 'main.c',
        5: 'post.c',
        6: 'protocol_data.c',
        7: 'uart_manager.c',
        8: 'uart_command.c',
        9: 'pump_info.c'
    }
    return switcher.get(firmware_error_file_id, "Unknown File ({})".format(firmware_error_file_id))


def get_firmware_error_line(event_log_hex):
    '''get firmware error line number

       It is the line number of the code line in the file 
       that cause the firmware error.
    '''
    firmware_error_line_hex = event_log_hex[16:20]
    firmware_error_line_int = int(firmware_error_line_hex, 16)
    return firmware_error_line_int


def get_system_error_type(event_log_hex):
    '''get system error type'''
    system_error_type_id = int(event_log_hex[10:14], 16);
    
    switcher = {
                    1: 'PRESSURE_SENSOR_ERROR',
                    2: 'SLOW_MOTOR_ERROR',
                    4: 'SHORTED_MOTOR_ERROR',
                    8: 'MOTOR_OPEN_ERROR',
                    16: 'MOTOR_SAFETY_FAIL_ERROR',
                    32: 'MOTOR_RUNNING_WRONG_STATE_ERROR',
                    64: 'MOTOR_DRIVER_FAILURE',
                    128: 'TIMER_INTERRUPT_FAILURE',
                    256: 'POST_FAILURE',
                    512: 'MOTOR_FAST_ERROR',
                    1024: 'UP_SENSOR_FAILURE',
                    2048: 'DOWN_SENSOR_FAILURE',
                    4096: 'MOTOR_SENSOR_FAILURE',
                    8192: 'AUDIO_FAILURE',
                    16384: 'SUPER_CAPACITOR_FAILURE',
                    32768: 'EXTERNAL_WATCHDOG_FAILURE'
                }
    # get() method of dictionary data type returns  
    # value of passed argument if it is present  
    # in dictionary otherwise second argument will 
    # be assigned as default value of passed argument
    # return switcher.get(system_error_type_id, "Unknown Error ({})".format(system_error_type_id))
    system_error_type_list = []
    if system_error_type_id == 0:
        system_error_type_list = ['Unknown Error']
    else:
        for i in range(len(switcher)):
            system_error_type = switcher.get(system_error_type_id & (2 ** i), "Unknown Error")
            if system_error_type != "Unknown Error":
                system_error_type_list.append(system_error_type + ' (b\'' + '{0:b}'.format(system_error_type_id & (2 ** i)).zfill(8) + '\')')
        if system_error_type_list == []:
            system_error_type_list = ['Unknown Error (b\'' + '{0:b}'.format(event_log_hex[10:14]).zfill(8) + '\')']
    return system_error_type_list


def get_battery_failure_type(event_log_hex):
    '''get battery failure type'''
    battery_failure_type_id = int(event_log_hex[10:14], 16);
    
    switcher = {
        1: 'BATTERY_OVERHEATED',
        2: 'BATTERY_EMPTY'
    }
    return switcher.get(battery_failure_type_id, "Unknown Type ({})".format(battery_failure_type_id))


def get_debug_info(event_log_hex):
    '''get debug info'''
    debug_info_hex = event_log_hex[10:14]
    debug_info_int = int(debug_info_hex, 16)
    return debug_info_int

    
def get_timer_count(event_log_hex):
    '''get timer count'''
    timer_count_hex = event_log_hex[14:22]
    timer_count_int = int(timer_count_hex, 16)
    return timer_count_int


def get_finish_dose_type(event_log_hex):
    '''get battery failure type'''
    dose_type_id = int(event_log_hex[10:14], 16);
    
    switcher = {
        1: 'EXTRA_DOSE_FINISH',
        2: 'STARTING_DOSE_FINISH'
    }
    return switcher.get(dose_type_id, "Unknown Type ({})".format(dose_type_id))


def get_cancel_dose_type(event_log_hex):
    '''get battery failure type'''
    dose_type_id = int(event_log_hex[10:13], 16);
    
    switcher = {
        1: 'STARTING_DOSE',
        2: 'EXTRA_DOSE',
        4: 'DOSE_TYPE_UNKNOWN'
    }
    return switcher.get(dose_type_id, "Unknown Type ({})".format(dose_type_id))


def get_system_error2_type(event_log_hex):
    '''get system error2 type'''
    system_error2_type_id = int(event_log_hex[10:14], 16);
    
    switcher = {
                    1: 'BATTERY_OVER_UPPER_LIMIT',
                    2: 'BATTERY_UNDER_LOWER_LIMIT',
                    4: 'PROTECTION_CPU_FAIL',
                    8: 'BACKUP_AUDIO_FAIL'                   
                }
    system_error2_type_list = []
    if system_error2_type_id == 0:
        system_error2_type_list = ['Unknown Error']
    else:
        for i in range(len(switcher)):
            system_error2_type = switcher.get(system_error2_type_id & (2 ** i), "Unknown Error")
            if system_error2_type != "Unknown Error":
                system_error2_type_list.append(system_error2_type + ' (b\'' + '{0:b}'.format(system_error2_type_id & (2 ** i)).zfill(8) + '\')')
        if system_error2_type_list == []:
            system_error2_type_list = ['Unknown Error (b\'' + '{0:b}'.format(event_log_hex[10:14]).zfill(8) + '\')']
    return system_error2_type_list


def get_pump_hard_limit_reached_type(event_log_hex):
    '''get pump hard limit reached type'''
    limit_type = int(event_log_hex[10:14], 16);
    switcher = {
        3: 'PRODUCT_LIFE_REACHED_REPLACE_PUMP'                
    }
    return switcher.get(limit_type, "Unknown Type ({})".format(limit_type))


def get_event_log_sub_type(event_log_hex):
    '''Get Event Log Sub-Type'''
    event_log_sub_type = 'UNKOWN_TYPE'
    event_log_type = get_event_log_type(event_log_hex)
    if event_log_type == 'INFUSION_DATA':
        # INFUSION_DATA 0
        infusion_data_frame = get_infusion_data_frame(event_log_hex)
        event_log_sub_type = infusion_data_frame
    elif event_log_type == 'RUN_INFUSION':
        # RUN_INFUSION 1
        pass    
    elif event_log_type == 'INFUSION_PAUSED':
        # INFUSION_PAUSED 2
        pass    
    elif event_log_type == 'CASSETTE_EMPTY':
        # CASSETTE_EMPTY 3
        pass
    elif event_log_type == 'INFUSION_LIMIT_REACHED':
        # INFUSION_LIMIT_REACHED 4
        infusion_limit_type = get_infusion_limit_type(event_log_hex)
        event_log_sub_type = infusion_limit_type
    elif event_log_type == 'AUTHENTICATION':
        # AUTHENTICATION 5
        pass
    elif event_log_type == 'DOSE_GRANTED':
        # DOSE_GRANTED 6
        bolus_type = get_bolus_type(event_log_hex)
        event_log_sub_type = bolus_type
    elif event_log_type == 'DOSE_DENIED':
        # DOSE_DENIED 7
        pass
    elif event_log_type == 'DOSE_CANCEL':
        # DOSE_CANCEL 8
        cancel_dose_type = get_cancel_dose_type(event_log_hex)
        event_log_sub_type = cancel_dose_type
    elif event_log_type == 'OCCLUSION':
        # OCCLUSION 9
        occlusion_type = get_occlusion_type(event_log_hex)
        event_log_sub_type = occlusion_type
    elif event_log_type == 'DELAY_END':
        # DELAY_END 10
        delay_end_type = get_delay_end_type(event_log_hex)
        event_log_sub_type = delay_end_type
    elif event_log_type == 'PUMP_LIMIT_REACHED':
        # PUMP_LIMIT_REACHED 11
        limit_type = get_pump_limit_type(event_log_hex)
        event_log_sub_type = limit_type
    elif event_log_type == 'CLEAR_SHIFT_TOTAL':
        # CLEAR_SHIFT_TOTAL 12
        pass
    elif event_log_type == 'BATTERY':
        # BATTERY 13
        battery_status = get_battery_status(event_log_hex)
        event_log_sub_type = battery_status
    elif event_log_type == 'CASSETTE_DETACHED':
        # CASSETTE_DETACHED 14
        pass
    elif event_log_type == 'TIME_STAMP':
        # TIME_STAMP 15
        pass
    elif event_log_type == 'POWER_ON':
        # POWER_ON 16
        pass
    elif event_log_type == 'POWER_OFF':
        # POWER_OFF 17
        pass    
    elif event_log_type == 'FIRMWARE_ERROR':
        # FIRMWARE_ERROR 18
        firmware_error_type = get_firmware_error_type(event_log_hex)
        event_log_sub_type = firmware_error_type
    elif event_log_type == 'SYSTEM_ERROR':
        # SYSTEM_ERROR 19
        system_error_type = get_system_error_type(event_log_hex)
        event_log_sub_type = system_error_type
    elif event_log_type == 'BATTERY_FAILURE':
        # BATTERY_FAILURE 20
        battery_failure_type = get_battery_failure_type(event_log_hex)
        event_log_sub_type = battery_failure_type
    elif event_log_type == 'DEBUG':
        # DEBUG 21
        pass
    elif event_log_type == 'UNATTENDED':
        # UNATTENDED 22
        pass
    elif event_log_type == 'HCP_SETTING_CHANGE':
        # HCP_SETTING_CHANGE 23
        pass
    elif event_log_type == 'BOLUS_FINISH':
        # DEMAND_BOLUS_FINISH 24
        finish_dose_type = get_finish_dose_type(event_log_hex)
        event_log_sub_type = finish_dose_type
    elif event_log_type == 'POWER_ON_BATTERY_LOG':
        # POWER_ON_BATTERY_LOG 25
        pass
    elif event_log_type == 'STARTING_DOSE_SKIP':
        # STARTING_DOSE_SKIP 26
        pass
    elif event_log_type == 'SYSTEM_ERROR2':
        # SYSTEM_ERROR2 27
        system_error2_type = get_system_error2_type(event_log_hex)
        event_log_sub_type = system_error2_type
    if event_log_type == 'PUMP_HARD_LIMIT_REACHED':
        # PUMP_HARD_LIMIT_REACHED 28
        limit_type = get_pump_hard_limit_reached_type(event_log_hex)
        event_log_sub_type = limit_type
    return event_log_sub_type


def get_event_log_type(event_log_hex):
    '''get eventlog status'''
    
    # event_log_hex[0:2] - event log id
    event_log_type_id = int(event_log_hex[0:2], 16)
    
    switcher = { 
        0: 'INFUSION_DATA',
        1: 'RUN_INFUSION',
        2: 'INFUSION_PAUSED',
        # 'INFUSION_COMPLETED'
        3: 'CASSETTE_EMPTY',
        4: 'INFUSION_LIMIT_REACHED',
        5: 'AUTHENTICATION',
        # 'BOLUS_GRANTED'
        6: 'DOSE_GRANTED',
        # 'DOSE_GRANTED'
        7: 'DOSE_DENIED',
        8: 'DOSE_CANCEL',
        9: 'OCCLUSION',
       10: 'DELAY_END',
       11: 'PUMP_LIMIT_REACHED',
       12: 'CLEAR_SHIFT_TOTAL',
       13: 'BATTERY',
        #  'OPEN_CASSETTE'
       14: 'CASSETTE_DETACHED',
       15: 'TIME_STAMP',
       16: 'POWER_ON',
       17: 'POWER_OFF',
       18: 'FIRMWARE_ERROR',
       19: 'SYSTEM_ERROR',
       20: 'BATTERY_FAILURE',
       21: 'DEBUG',
       22: 'UNATTENDED',
       23: 'HCP_SETTING_CHANGE',
       24: 'BOLUS_FINISH',
       25: 'POWER_ON_BATTERY_LOG',
       26: 'STARTING_DOSE_SKIP',
       27: 'SYSTEM_ERROR2',
       28: 'PUMP_HARD_LIMIT_REACHED'
    } 
  
    # get() method of dictionary data type returns  
    # value of passed argument if it is present  
    # in dictionary otherwise second argument will 
    # be assigned as default value of passed argument 
    return switcher.get(event_log_type_id, "Unknown Type ({})".format(event_log_type_id)) 

  
def get_time_stamp(event_log_hex, relative_time=True):
    '''get time stamp
       input:
           event_log_hex - 16-bytes
       return:
           time stamp ("YYYY-MM-DD HH:MM:SS")
       Hex Bitmap (high - low):
            year: 6-byte
           month: 4-byte
             day: 5-byte
            hour: 5-byte
          minute: 6-byte
          second: 6-byte
    '''
    # event_log_hex[2:10] - time_stamp
    time_stamp_hex = event_log_hex[2:10]
    
    time_stamp = {'year': '1',
                  'month': '1',
                  'day': '1',
                  'hour': '1',
                  'minute': '1',
                  'second': '1'
                  }
    if relative_time:
        # The pump time is in relative format
        time_stamp_hex_little = event_log_hex[2:10].upper()
        time_stamp_int_little = int(time_stamp_hex_little, 16)
        time_stamp_int_big = struct.unpack("<I", struct.pack(">I", time_stamp_int_little))[0]
        time_stamp_hex_big = hex(time_stamp_int_big)[2:].upper().zfill(8)
        # print("time_stamp_hex_little    = 0x{0}".format(time_stamp_hex_little))
        # print('time_stamp_hex_big = 0x{0}'.format(time_stamp_hex_big))
        # [time_stamp_hex_big] is in format 'F0 00 00 00', So the first 'F' need to be removed.
        time_stamp_int = 0
        if time_stamp_hex_big[0] == '0':
            time_stamp_int = int(time_stamp_hex_big, 16)
        time_stamp_int = int('0' + time_stamp_hex_big[1:], 16)
        return time_stamp_int
    else:
        time_stamp_int = int(time_stamp_hex, 16)
        year = int((time_stamp_int & 0xFC000000) >> 26) + 2000
        time_stamp['year'] = str(year)
                    
        month = int((time_stamp_int & 0x3C00000) >> 22)
        month = str(month)
        while len(month) < 2:
            month = '0' + month
        time_stamp['month'] = month
        
        days = int((time_stamp_int & 0x3E0000) >> 17)
        days = str(days)
        while len(days) < 2:
            days = '0' + days
        time_stamp['day'] = days
        
        hours = int((time_stamp_int & 0x1F000) >> 12)
        hours = str(hours)
        while len(hours) < 2:
            hours = '0' + hours
        time_stamp['hour'] = hours
    
        minutes = int((time_stamp_int & 0xFC0) >> 6)
        minutes = str(minutes)
        while len(minutes) < 2:
            minutes = '0' + minutes
        time_stamp['minute'] = minutes
        
        seconds = time_stamp_int & 0x3F
        seconds = str(seconds)
        while len(seconds) < 2:
            seconds = '0' + seconds
        time_stamp['second'] = seconds
    return time_stamp


def parse_multiple_event_log(event_log_hex_list):
    # Parse Multiple Event Logs
    event_logs = []
    num_to_print = len(event_log_hex_list)
    print('Parsing [{}] event log...'.format(num_to_print))
    event_log_index = 0
    while len(event_logs) < num_to_print:
        if event_log_index >= num_to_print:
            break
        if event_log_hex_list[event_log_index] == "".join(['F'] * 32):
            # Ignore All 'F' lines
            event_log_index += 1
            continue
        # Rotation buffer. Pointer need to be reset when hit 0
        event_log_hex = event_log_hex_list[event_log_index]
        each_event_log = parse_event_log(event_log_hex, pump_time_offset=0)
        # print(each_event_log)
        event_logs.append(each_event_log)
        if len(event_logs) < num_to_print and \
                each_event_log['event_type'] == 'INFUSION_DATA' and \
                each_event_log['infusion_data_frame'] == 'INFUSION_DATA_BEGIN':
            print('event_type = INFUSION_DATA', end='\r')
            print('infusion_data_frame = INFUSION_DATA_BEGIN', end='\r')
            # Try out the correct infusion data log size
            tentative_event_log_hex = event_log_hex_list[event_log_index + 2 + 1]
            tentative_event_log = parse_event_log(tentative_event_log_hex, pump_time_offset=0)
            # print(tentative_event_log)
            if tentative_event_log['infusion_data_frame'] == 'INFUSION_DATA_END':
                infusion_data_log_size = 2
            else:
                infusion_data_log_size = 16
            #
            infusion_data_hex = ''
            for i in range(event_log_index + 1, event_log_index + infusion_data_log_size + 1):
                infusion_data_hex += event_log_hex_list[i]
            # print('infusion data hex = {}'.format(infusion_data_hex))
            infusion_data = parse_infusion_data_log(infusion_data_hex)
            event_logs.append(infusion_data)
            event_log_index += infusion_data_log_size
        elif each_event_log['event_type'] == 'INFUSION_DATA' and \
                each_event_log['infusion_data_frame'] == 'INFUSION_DATA_END':
            print('event_type = INFUSION_DATA', end='\r')
            print('infusion_data_frame = INFUSION_DATA_END', end='\r')
        event_log_index += 1
    return event_logs 


def parse_event_log(event_log_hex, pump_time_offset=-1):
    '''Parse Event Log
        Input:
            event_log_hex -- 32 bytes hex (16 bytes data)
        Output:
            event_log_json -- event log json string
        
    '''
    event_log = {}
    event_log_type = get_event_log_type(event_log_hex)
    event_log['event_type'] = event_log_type
    if pump_time_offset == -1:
        time_stamp = get_time_stamp(event_log_hex, relative_time=False)
        # The pump time is in normal format
        time_stamp_string = time_stamp['year'] + '-' + \
                            time_stamp['month'] + '-' + \
                            time_stamp['day'] + ' ' + \
                            time_stamp['hour'] + ':' + \
                            time_stamp['minute'] + ':' + \
                            time_stamp['second']
        # print("{0:7s} = {1}".format('time', time_stamp_string))
        event_log['time'] = time_stamp_string
    else:
        # The pump time is in relative format
        time_stamp_int = get_time_stamp(event_log_hex)
        time_stamp_hex_big = hex(time_stamp_int).upper()[2:]
        if pump_time_offset >= time_stamp_int:
            # [pump_time_offset] is supposed to be always greater than [time_stamp_int]
            relative_time_diff = pump_time_offset - time_stamp_int
            relative_time_diff_delta = datetime.timedelta(seconds=relative_time_diff)
            current_time = datetime.datetime.now()
            time_of_event_occur = current_time - relative_time_diff_delta
            event_log['time'] = time_of_event_occur.strftime("%Y-%m-%d %H:%M:%S") \
                                +' (0x' + time_stamp_hex_big + ' - ' + str(time_stamp_int) + ' sec)'
            if -time.timezone >= 0:
                event_log['time'] = time_of_event_occur.strftime("%Y-%m-%dT%H:%M:%S") \
                                +'+' + int_to_time_str(abs(time.timezone), 'hh:mm')\
                                +' (0x' + time_stamp_hex_big + ' - ' + str(time_stamp_int) + ' sec)'
            elif -time.timezone == 0:
                event_log['time'] = time_of_event_occur.strftime("%Y-%m-%dT%H:%M:%SZ") \
                                +' (0x' + time_stamp_hex_big + ' - ' + str(time_stamp_int) + ' sec)'
            elif -time.timezone < 0:
                event_log['time'] = time_of_event_occur.strftime("%Y-%m-%dT%H:%M:%S") \
                                +'-' + int_to_time_str(abs(time.timezone), 'hh:mm')\
                                +' (0x' + time_stamp_hex_big + ' - ' + str(time_stamp_int) + ' sec)'
        else:
            event_log['time'] = '0x' + time_stamp_hex_big + ' (' + str(time_stamp_int) + ' sec)'
    if event_log_type == 'INFUSION_DATA':
        # INFUSION_DATA 0
        infusion_data_frame = get_infusion_data_frame(event_log_hex)
        event_log['infusion_data_frame'] = infusion_data_frame
    if event_log_type == 'RUN_INFUSION':
        # RUN_INFUSION 1
        pass
    if event_log_type == 'INFUSION_PAUSED':
        # INFUSION_PAUSED 2
        pause_vinf = get_infusion_pause_vinf(event_log_hex)
        event_log['vinf (mL)'] = pause_vinf
    if event_log_type == 'CASSETTE_EMPTY':
        # CASSETTE_EMPTY 3
        pass
    if event_log_type == 'INFUSION_LIMIT_REACHED':
        # INFUSION_LIMIT_REACHED 4
        infusion_limit_type = get_infusion_limit_type(event_log_hex)
        event_log['limit type'] = infusion_limit_type
    if event_log_type == 'AUTHENTICATION':
        # AUTHENTICATION 5
        auth_code = get_authentication_code(event_log_hex)
        event_log['auth code'] = auth_code
    if event_log_type == 'DOSE_GRANTED':
        # DOSE_GRANTED 6
        bolus_type = get_bolus_type(event_log_hex)
        event_log['bolus type'] = bolus_type
    if event_log_type == 'DOSE_DENIED':
        # DOSE_DENIED 7
        number_of_bolus_attempted = get_bolus_attempted_number(event_log_hex)
        event_log['attempted no.'] = number_of_bolus_attempted
    if event_log_type == 'DOSE_CANCEL':
        # DOSE_CANCEL 8
        event_log['dose type'] = get_cancel_dose_type(event_log_hex)
        pass
    if event_log_type == 'OCCLUSION':
        # OCCLUSION 9
        occlusion_type = get_occlusion_type(event_log_hex)
        event_log['occlusion type'] = occlusion_type
    if event_log_type == 'DELAY_END':
        # DELAY_END 10
        delay_end_type = get_delay_end_type(event_log_hex)
        event_log['delay end type'] = delay_end_type
    if event_log_type == 'PUMP_LIMIT_REACHED':
        # PUMP_LIMIT_REACHED 11
        limit_type = get_pump_limit_type(event_log_hex)
        event_log['limit type'] = limit_type
    if event_log_type == 'CLEAR_SHIFT_TOTAL':
        # CLEAR_SHIFT_TOTAL 12
        pass
    if event_log_type == 'BATTERY':
        # BATTERY 13
        battery_status = get_battery_status(event_log_hex)
        # print('{0:7s} = {1}'.format('battery status', battery_status))
        event_log['battery status'] = battery_status
        #
        battery_voltage = get_eventlog_battery_voltage(event_log_hex)
        # print('{0:7s} = {1}'.format('battery voltage (V)', battery_voltage))
        event_log['battery voltage (V)'] = battery_voltage
        #
        battery_vinf = get_eventlog_battery_vinf(event_log_hex)
        # print('{0:7s} = {1}'.format('battery VINF (mL)', battery_vinf))
        event_log['battery vinf (mL)'] = battery_vinf
    if event_log_type == 'CASSETTE_DETACHED':
        # CASSETTE_DETACHED 14
        pass
    if event_log_type == 'TIME_STAMP':
        # TIME_STAMP 15
        pass
    if event_log_type == 'POWER_ON':
        # POWER_ON 16
        battery_charge = get_battery_charge(event_log_hex)
        event_log['battery charge (V)'] = battery_charge
        #
        battery_vinf = get_eventlog_battery_vinf(event_log_hex)
        # print('{0:7s} = {1}'.format('battery VINF (mL)', battery_vinf))
        event_log['battery vinf (mL)'] = battery_vinf
    if event_log_type == 'POWER_OFF':
        # POWER_OFF 17
        battery_charge = get_battery_charge(event_log_hex)
        event_log['battery charge (V)'] = battery_charge
        #
        battery_vinf = get_eventlog_battery_vinf(event_log_hex)
        # print('{0:7s} = {1}'.format('battery VINF (mL)', battery_vinf))
        event_log['battery vinf (mL)'] = battery_vinf
    if event_log_type == 'FIRMWARE_ERROR':
        # FIRMWARE_ERROR 18
        firmware_error_type = get_firmware_error_type(event_log_hex)
        event_log['firmware error type'] = firmware_error_type
        firmware_error_file = get_firmware_error_file(event_log_hex)
        event_log['file name'] = firmware_error_file
        firmware_error_line = get_firmware_error_line(event_log_hex)
        event_log['line #'] = firmware_error_line
    if event_log_type == 'SYSTEM_ERROR':
        # SYSTEM_ERROR 19
        system_error_type = get_system_error_type(event_log_hex)
        event_log['system error type'] = system_error_type
    if event_log_type == 'BATTERY_FAILURE':
        # BATTERY_FAILURE 20
        battery_failure_type = get_battery_failure_type(event_log_hex)
        event_log['battery failure type'] = battery_failure_type
        #
        battery_voltage = get_eventlog_battery_voltage(event_log_hex)
        # print('{0:7s} = {1}'.format('battery voltage (V)', battery_voltage))
        event_log['battery voltage (V)'] = battery_voltage
        #
        battery_vinf = get_eventlog_battery_vinf(event_log_hex)
        # print('{0:7s} = {1}'.format('battery VINF (mL)', battery_vinf))
        event_log['battery vinf (mL)'] = battery_vinf
    if event_log_type == 'DEBUG':
        # DEBUG 21
        debug_info = get_debug_info(event_log_hex)
        event_log['debug info'] = debug_info
        debug_message_hex = event_log_hex
        event_log['message hex'] = debug_message_hex
        timer_count = get_timer_count(event_log_hex)
        event_log['timer count'] = timer_count
    if event_log_type == 'UNATTENDED':
        # UNATTENDED 22
        pass
    if event_log_type == 'HCP_SETTING_CHANGE':
        # HCP_SETTING_CHANGE 23
        event_log['protocol index'] = get_protocol_index(event_log_hex)
        event_log['node type'] = get_node_type(event_log_hex) 
        event_log['is_guards_equal_to_value'] = is_guards_equal_to_value(event_log_hex)
        event_log['parameter_index'] = get_parameter_index(event_log_hex)
        event_log['old_value'] = get_value_before_change(event_log_hex)
        event_log['new_value'] = get_value_after_change(event_log_hex)
    if event_log_type == 'BOLUS_FINISH':
        # DEMAND_BOLUS_FINISH 24
        event_log['dose_type'] = get_finish_dose_type(event_log_hex)
        pass
    if event_log_type == 'POWER_ON_BATTERY_LOG':
        # POWER_ON_BATTERY_LOG 25
        event_log['battery voltage (V)'] = get_eventlog_battery_voltage(event_log_hex)
        #
        battery_vinf = get_eventlog_battery_vinf(event_log_hex)
        # print('{0:7s} = {1}'.format('battery VINF (mL)', battery_vinf))
        event_log['battery vinf (mL)'] = battery_vinf
        pass
    if event_log_type == 'STARTING_DOSE_SKIP':
        # STARTING_DOSE_SKIP 26
        pass
    if event_log_type == 'SYSTEM_ERROR2':
        # SYSTEM_ERROR2 27
        system_error2_type = get_system_error2_type(event_log_hex)
        event_log['system error2 type'] = system_error2_type
    if event_log_type == 'PUMP_HARD_LIMIT_REACHED':
        # PUMP_HARD_LIMIT_REACHED 28
        limit_type = get_pump_hard_limit_reached_type(event_log_hex)
        event_log['limit type'] = limit_type
    return event_log


def compare_event_log_equal(event_log, event_log_ref):
    if 'event_type' in event_log and 'event_type' in event_log_ref:
        if event_log['event_type'] == event_log['event_type']:
            return True
        else:
            return False
    else:
        if event_log == event_log_ref:
            return True
        else:
            return False


def get_protocol_index(event_log_hex):
    '''Get Protocol Index'''
    protocol_index_hex = event_log_hex[10:11]
    protocol_index = int(protocol_index_hex, 16)
    if protocol_index == 0:
        return 'Daily'
    elif protocol_index == 1:
        return 'Nightly'
    elif protocol_index == 2:
        return 'Activity'


def get_node_type(event_log_hex):
    '''Get Node Type'''
    node_type = int(event_log_hex[11:12], 16) & 0x7
    if node_type == 0:
        return 'Value'
    elif node_type == 1:
        return 'Upper Limit'
    elif node_type == 2:
        return 'Lower Limit'


def is_guards_equal_to_value(event_log_hex):
    '''Is Guards Equal to Value'''
    is_guards_equal = int(event_log_hex[11:12], 16) & 0x8
    if is_guards_equal == 8:
        return 'Yes'
    elif is_guards_equal == 0:
        return 'No'


def get_parameter_index(event_log_hex):
    '''Get Parameter Index'''
    parameter_index = int(event_log_hex[12:14], 16)
    if parameter_index == 0:
        return 'LDS'
    elif parameter_index == 1:
        return 'RATE'
    elif parameter_index == 2:
        return 'DB_VOL'
    elif parameter_index == 3:
        return 'DB_LCK'
    elif parameter_index == 4:
        return 'VTBI'
    elif parameter_index == 6:
        return 'NEAR_END'
    elif parameter_index == 8:
        return 'STDOS_LCK'
    elif parameter_index == 9:
        return 'VISIBILITY'


def get_value_before_change(event_log_hex):
    '''Get Value before Change'''
    parameter_index = int(event_log_hex[12:14], 16)
    if parameter_index == 3 or parameter_index == 8:
        return int(event_log_hex[14:22], 16)
    elif parameter_index == 9:
        if int(event_log_hex[14:22], 16) == 0:
            return "VISIBLE"
        else:
            return "INVISIBLE"
    else:
        return struct.unpack('!f', bytes.fromhex(event_log_hex[14:22]))[0]


def get_value_after_change(event_log_hex):
    '''Get Value after Change'''
    parameter_index = int(event_log_hex[12:14], 16)
    if parameter_index == 3 or parameter_index == 8:
        return int(event_log_hex[22:30], 16)
    elif parameter_index == 9:
        if int(event_log_hex[22:30], 16) == 0:
            return "VISIBLE"
        else:
            return "INVISIBLE"
    else:
        return struct.unpack('!f', bytes.fromhex(event_log_hex[22:30]))[0]

    
def get_protocol_name(protocol_hex):
    '''Get Protocol Name'''
    protocol_name_hex = protocol_hex[198:218]
    protocol_bytes = bytes.fromhex(protocol_name_hex)
    # trim / remove trailing null spaces from a string
    protocol_name = protocol_bytes.decode("ASCII").rstrip(' \t\r\n\0')
    return protocol_name


def get_protocol_drug_name(protocol_hex):
    '''Get Protocol Name'''
    protocol_drug_name_hex = protocol_hex[218:238]
    protocol_drug_name_bytes = bytes.fromhex(protocol_drug_name_hex)
    # trim / remove trailing null spaces from a string
    protocol_drug_name = protocol_drug_name_bytes.decode("ASCII").rstrip(' \t\r\n\0')
    if len(protocol_drug_name) == 0:
        protocol_drug_name = None
    return protocol_drug_name


def get_protocol_infusion_mode(protocol_hex):
    '''Get Infusion Mode'''
    infusion_mode_id = int(protocol_hex[186:188], 16)
    switcher = {
        0: 'continuous',
        1: 'bolus',
        2: 'intermittent'        
    }
    return switcher.get(infusion_mode_id, "Unknown Mode")

    
def get_protocol_rate_unit(protocol_hex):
    '''Get Rate Unit'''
    rate_unit = int(protocol_hex[194:196], 16)
    switcher = {
        0: 'mL/hr',
        1: 'mg/min',
        2: 'mg/kg/min',
        3: 'mcg/min',
        4: 'mcg/kg/min'
    }
    return switcher.get(rate_unit, "Unknown Unit")


def get_protocol_drug_unit(protocol_hex):
    '''Get Drug Concentration Unit'''
    drug_unit = int(protocol_hex[196:198], 16)
    switcher = {
        0: 'mg',
        1: 'mcg'
    }
    return switcher.get(drug_unit, "Unknown Unit")


def get_protocol_switches(protocol_hex):
    '''Get Switches'''
    switches_int = int(protocol_hex[160:168], 16)
    # print('switches_int = {}'.format(switches_int))
    switches = {}
    infusion_mode = get_protocol_infusion_mode(protocol_hex)
    if infusion_mode == 'continuous':
        # Continuous Mode Bit Map:
        # Rate 0
        switches['rate'] = ((switches_int >> 0) & 1) == 1
        # Vtbi 1
        switches['vtbi'] = ((switches_int >> 1) & 1) == 1
        # Loading Dose 2
        switches['loading_dose'] = ((switches_int >> 2) & 1) == 1
        # Time 3
        switches['time'] = ((switches_int >> 3) & 1) == 1
        # Delay Start 4
        switches['delay_start'] = ((switches_int >> 4) & 1) == 1
        # KVO Rate 5
        switches['kvo_rate'] = ((switches_int >> 5) & 1) == 1
        # Delay KVO Rate 6
        switches['delay_kvo_rate'] = ((switches_int >> 6) & 1) == 1
        # Concentration 7
        switches['concentration'] = ((switches_int >> 7) & 1) == 1
        # Weight 10
        switches['weight'] = ((switches_int >> 10) & 1) == 1
        # Drug Amount 22
        switches['drug_amount'] = ((switches_int >> 22) & 1) == 1
        # Dilute Volume
        switches['dilute_volume'] = False
        # Flow Rate Calibration Factor
        # switches['flow_rate_calibration_factor'] = False

    elif infusion_mode == 'bolus':
        # Bolus Mode Bit Map:
        # Basal Rate 0
        switches['basal_rate'] = ((switches_int >> 0) & 1) == 1
        # VTBI 1
        switches['vtbi'] = ((switches_int >> 1) & 1) == 1
        # Loading Dose 2
        switches['loading_dose'] = ((switches_int >> 2) & 1) == 1
        # Time 3
        switches['time'] = ((switches_int >> 3) & 1) == 1
        # Delay Start 4
        switches['delay_start'] = ((switches_int >> 4) & 1) == 1
        # Auto Bolus 5
        switches['auto_bolus'] = ((switches_int >> 5) & 1) == 1
        # Bolus Interval 6
        switches['bolus_interval'] = ((switches_int >> 6) & 1) == 1
        # Demand Bolus 7
        switches['demand_bolus'] = ((switches_int >> 7) & 1) == 1
        # Lockout Time 8
        switches['lockout_time'] = ((switches_int >> 8) & 1) == 1
        # KVO Rate 10
        switches['kvo_rate'] = ((switches_int >> 9) & 1) == 1
        # Delay KVO Rate 10
        switches['delay_kvo_rate'] = ((switches_int >> 10) & 1) == 1
        # Max Per Hour 11
        switches['max_per_hour'] = ((switches_int >> 11) & 1) == 1
        # Max Per Interval 12
        switches['max_per_interval'] = ((switches_int >> 12) & 1) == 1
        # Clinician Dose 13
        switches['clinician_dose'] = ((switches_int >> 13) & 1) == 1
        # Concentration 14
        switches['concentration'] = ((switches_int >> 14) & 1) == 1
        # Drug Amount 15
        switches['drug_amount'] = ((switches_int >> 15) & 1) == 1
        # Dilute Volume 16
        switches['dilute_volume'] = ((switches_int >> 16) & 1) == 1
        # Weight 17
        switches['weight'] = ((switches_int >> 17) & 1) == 1
        # Flow Rate Calibration Factor
        # switches['flow_rate_calibration_factor'] = False

    elif infusion_mode == 'intermittent':
        # Intermittent Mode Bit Map:
        # Dose Rate 0
        switches['dose_rate'] = ((switches_int >> 0) & 1) == 1
        # Dose VTBI 1
        switches['dose_vtbi'] = ((switches_int >> 1) & 1) == 1
        # Loading Dose 2
        switches['loading_dose'] = ((switches_int >> 2) & 1) == 1
        # Total Time 3
        switches['total_time'] = ((switches_int >> 3) & 1) == 1
        # Interval Time 4
        switches['interval_time'] = ((switches_int >> 4) & 1) == 1
        # Delay Start 5
        switches['delay_start'] = ((switches_int >> 5) & 1) == 1
        # Intermittent KVO Rate 6
        switches['intermittent_kvo_rate'] = ((switches_int >> 6) & 1) == 1
        # KVO Rate 7
        switches['kvo_rate'] = ((switches_int >> 7) & 1) == 1
        # Delay KVO Rate 8
        switches['delay_kvo_rate'] = ((switches_int >> 8) & 1) == 1        
        # Max Amount Per Hour 9
        switches['max_per_hour'] = ((switches_int >> 9) & 1) == 1        
        # Max Amount Per Interval 10
        switches['max_per_interval'] = ((switches_int >> 10) & 1) == 1
        # Concentration 11
        switches['concentration'] = ((switches_int >> 11) & 1) == 1
        # Drug Amount 12
        switches['drug_amount'] = ((switches_int >> 12) & 1) == 1
        # Dilute Volume 13
        switches['dilute_volume'] = ((switches_int >> 13) & 1) == 1
        # Weight 14
        switches['weight'] = ((switches_int >> 14) & 1) == 1
        # Flow Rate Calibration Factor
        # switches['flow_rate_calibration_factor'] = False

    return switches


def get_protocol_drug_components(protocol_hex):
    '''Get Drug Components'''
    drug_components_hex = protocol_hex[238:448]
    # print('drug_components_hex = {}'.format(drug_components_hex))
    drug_components_bytes = bytes.fromhex(drug_components_hex)
    # print('drug components = {}'.format(drug_components_bytes.decode("ASCII").rstrip(' \t\r\n\0')))
    drug_components = []
    DRUG_COMPONENT_LENGTH = 35
    DRUG_COMPONENT_NAME_LENGTH = 20
    # DRUG_COMPONENT_CONCENTRATION_LENGTH = 15
    for drug_component_index in range(3):
        name_start_index = drug_component_index * DRUG_COMPONENT_LENGTH
        name_end_index = drug_component_index * DRUG_COMPONENT_LENGTH + DRUG_COMPONENT_NAME_LENGTH
        name_bytes = drug_components_bytes[name_start_index:name_end_index]
        # print('name_bytes = {}'.format(name_bytes))
        # trim / remove trailing null spaces from a string
        name = name_bytes.decode("ASCII").rstrip(' \t\r\n\0')
        # print('name = {}'.format(name))
        #
        concentration_start_index = drug_component_index * DRUG_COMPONENT_LENGTH + \
                                    DRUG_COMPONENT_NAME_LENGTH
        concentration_end_index = (drug_component_index + 1) * DRUG_COMPONENT_LENGTH
        concentration_bytes = drug_components_bytes[concentration_start_index:concentration_end_index]
        # print('concentration_bytes = {}'.format(concentration_bytes))
        # trim / remove trailing null spaces from a string
        concentration = concentration_bytes.decode("ASCII").rstrip(' \t\r\n\0')
        # print('concentration = {}'.format(concentration))
        # [each_drug] is a local variable
        each_drug = {}
        each_drug['name'] = name
        each_drug['concentration'] = concentration
        if each_drug['name'] != '':
            drug_components.append(each_drug)
    # print('drug_components = {}'.format(drug_components))
    if len(drug_components) == 0:
        drug_components = None
    return drug_components

    
def get_protocol_union(protocol_hex):
    '''Get Protocol Union'''
    protocol_union_hex = protocol_hex[0:160]
    protocol_union_bytes = bytes.fromhex(protocol_union_hex)
    swithes = get_protocol_switches(protocol_hex)
    protocol_union = {}
    infusion_mode = get_protocol_infusion_mode(protocol_hex)
    if infusion_mode == 'continuous':
        # 0:4 Rate 4-byte Float
        protocol_union['rate'] = None
        if swithes['rate']:
            protocol_union['rate'] = struct.unpack('!f', protocol_union_bytes[0:4])[0]
            protocol_union['rate_hex'] = protocol_union_hex[0:8]
        # 4:8 VTBI 4-byte Float
        protocol_union['vtbi'] = None
        if swithes['vtbi']:
            protocol_union['vtbi'] = struct.unpack('!f', protocol_union_bytes[4:8])[0]
        # 8:12 Loading Dose 4-byte Float
        protocol_union['loading_dose'] = None
        if swithes['loading_dose']:
            protocol_union['loading_dose'] = struct.unpack('!f', protocol_union_bytes[8:12])[0]
        # 12:16 Time 4-byte int (minute)
        protocol_union['time'] = None
        if swithes['time']:
            protocol_union['time'] = int(int.from_bytes(protocol_union_bytes[12:16], 'big') / 60)
        # 16:20 Delay Start 4-byte
        protocol_union['delay_start'] = None
        if swithes['delay_start']:
            protocol_union['delay_start'] = int(int.from_bytes(protocol_union_bytes[16:20], 'big') / 60)
        # 20:24 KVO Rate 4-byte
        protocol_union['kvo_rate'] = None
        if swithes['kvo_rate']:
            protocol_union['kvo_rate'] = struct.unpack('!f', protocol_union_bytes[20:24])[0]
        # 24:28 Delay KVO Rate 4-byte
        protocol_union['delay_kvo_rate'] = None
        if swithes['delay_kvo_rate']:
            protocol_union['delay_kvo_rate'] = struct.unpack('!f', protocol_union_bytes[24:28])[0]
        # 28:32 Concentration 4-byte
        protocol_union['concentration'] = None
        if swithes['concentration']:
            protocol_union['concentration'] = struct.unpack('!f', protocol_union_bytes[28:32])[0]
        # 32:36 Drug Amount 4-byte
        protocol_union['drug_amount'] = None
        if swithes['drug_amount']:
            protocol_union['drug_amount'] = struct.unpack('!f', protocol_union_bytes[32:36])[0]
        # 36:40 Solvent Volume 4-byte
        protocol_union['dilute_volume'] = None
        if swithes['dilute_volume']:
            protocol_union['dilute_volume'] = struct.unpack('!f', protocol_union_bytes[36:40])[0]
        # 40:44 Weight 4-byte
        protocol_union['weight'] = None
        if swithes['weight']:
            protocol_union['weight'] = struct.unpack('!f', protocol_union_bytes[40:44])[0]

    if infusion_mode == 'bolus':
        # 0:4 Basal Rate 4-byte Float
        protocol_union['basal_rate'] = None
        if swithes['basal_rate']:
            protocol_union['basal_rate'] = struct.unpack('!f', protocol_union_bytes[0:4])[0]
        # 4:8 VTBI 4-byte Float
        protocol_union['vtbi'] = None
        if swithes['vtbi']:
            protocol_union['vtbi'] = struct.unpack('!f', protocol_union_bytes[4:8])[0]
        # 8:12 Loading Dose 4-byte Float
        protocol_union['loading_dose'] = None
        if swithes['loading_dose']:
            protocol_union['loading_dose'] = struct.unpack('!f', protocol_union_bytes[8:12])[0]
        # 12:16 Time 4-byte Integer (minute)
        protocol_union['time'] = None
        if swithes['time']:
            protocol_union['time'] = int(int.from_bytes(protocol_union_bytes[12:16], 'big') / 60)
        # 16:20 Delay Start 4-byte Integer
        protocol_union['delay_start'] = None
        if swithes['delay_start']:
            protocol_union['delay_start'] = int(int.from_bytes(protocol_union_bytes[16:20], 'big') / 60)
        # 20:24 Auto Bolus 4-byte Float
        protocol_union['auto_bolus'] = None
        if swithes['auto_bolus']:
            protocol_union['auto_bolus'] = struct.unpack('!f', protocol_union_bytes[20:24])[0]
        # 24:28 Auto Bolus Interval 4-byte Integer (minute)
        protocol_union['bolus_interval'] = None
        if swithes['bolus_interval']:
            protocol_union['bolus_interval'] = int(int.from_bytes(protocol_union_bytes[24:28], 'big') / 60)
        # 28:32 Demand Bolus 4-byte Float
        protocol_union['demand_bolus'] = None
        if swithes['demand_bolus']:
            protocol_union['demand_bolus'] = struct.unpack('!f', protocol_union_bytes[28:32])[0]
        # 32:36 Demand Bolus Lockout Time 4-byte Integer (minute)
        protocol_union['lockout_time'] = None
        if swithes['lockout_time']:
            protocol_union['lockout_time'] = int(int.from_bytes(protocol_union_bytes[32:36], 'big') / 60)
        # 36:40 KVO Rate 4-byte Float
        protocol_union['kvo_rate'] = None
        if swithes['kvo_rate']:
            protocol_union['kvo_rate'] = struct.unpack('!f', protocol_union_bytes[36:40])[0]
        # 40:44 Delay KVO Rate 4-byte Float        
        protocol_union['delay_kvo_rate'] = None
        if swithes['delay_kvo_rate']:
            protocol_union['delay_kvo_rate'] = struct.unpack('!f', protocol_union_bytes[40:44])[0]
        # 44:48 Max Per Hour 4-byte Float
        protocol_union['max_per_hour'] = None
        if swithes['max_per_hour']:
            protocol_union['max_per_hour'] = struct.unpack('!f', protocol_union_bytes[44:48])[0]
        # 48:52 Max Per Interval 4-byte Float
        protocol_union['max_per_interval'] = None
        if swithes['max_per_interval']:
            protocol_union['max_per_interval'] = struct.unpack('!f', protocol_union_bytes[48:52])[0]
        # 52:56 Clinician Dose 4-byte Float
        protocol_union['clinician_dose'] = None
        if swithes['clinician_dose']:
            protocol_union['clinician_dose'] = struct.unpack('!f', protocol_union_bytes[52:56])[0]
        # 56:60 Concentration 4-byte Float
        protocol_union['concentration'] = None
        if swithes['concentration']:
            protocol_union['concentration'] = struct.unpack('!f', protocol_union_bytes[56:60])[0]
        # 60:64 Drug Amount 4-byte Float
        protocol_union['drug_amount'] = None
        if swithes['drug_amount']:
            protocol_union['drug_amount'] = struct.unpack('!f', protocol_union_bytes[60:64])[0]
        # 64:68 Solvent Volume 4-byte Float
        protocol_union['dilute_volume'] = None
        if swithes['dilute_volume']:
            protocol_union['dilute_volume'] = struct.unpack('!f', protocol_union_bytes[64:68])[0]
        # 68:72 Weight 4-byte Float
        protocol_union['weight'] = None
        if swithes['weight']:
            protocol_union['weight'] = struct.unpack('!f', protocol_union_bytes[68:72])[0]

    if infusion_mode == 'intermittent':
        # 0:4 Dose Rate 4-Byte Float
        protocol_union['dose_rate'] = None
        if swithes['dose_rate']:
            protocol_union['dose_rate'] = struct.unpack('!f', protocol_union_bytes[0:4])[0]
        # 4:8 Dose VTBI 4-Byte Float
        protocol_union['dose_vtbi'] = None
        if swithes['dose_vtbi']:
            protocol_union['dose_vtbi'] = struct.unpack('!f', protocol_union_bytes[4:8])[0]
        # 8:12 Loading Dose 4-Byte Float
        protocol_union['loading_dose'] = None
        if swithes['loading_dose']:
            protocol_union['loading_dose'] = struct.unpack('!f', protocol_union_bytes[8:12])[0]
        # 12:16 Total Time 4-Byte Integer (Minute)
        protocol_union['total_time'] = None
        if swithes['total_time']:
            protocol_union['total_time'] = int(int.from_bytes(protocol_union_bytes[12:16], 'big') / 60)
        # 16:20 Interval Time 4-Byte Integer (Minute)
        protocol_union['interval_time'] = None
        if swithes['interval_time']:
            protocol_union['interval_time'] = int(int.from_bytes(protocol_union_bytes[16:20], 'big') / 60)
        # 20:24 Delay Start 4-Byte Integer (Minute)
        protocol_union['delay_start'] = None
        if swithes['delay_start']:
            protocol_union['delay_start'] = int(int.from_bytes(protocol_union_bytes[20:24], 'big') / 60)
        # 24:28 Intermittent KVO Rate 4-Byte Float
        protocol_union['intermittent_kvo_rate'] = None
        if swithes['intermittent_kvo_rate']:
            protocol_union['intermittent_kvo_rate'] = struct.unpack('!f', protocol_union_bytes[24:28])[0]
        # 28:32 KVO Rate 4-Byte Float
        protocol_union['kvo_rate'] = None
        if swithes['kvo_rate']:
            protocol_union['kvo_rate'] = struct.unpack('!f', protocol_union_bytes[28:32])[0]
        # 32:36 Delay KVO Rate 4-Byte Float
        protocol_union['delay_kvo_rate'] = None
        if swithes['delay_kvo_rate']:
            protocol_union['delay_kvo_rate'] = struct.unpack('!f', protocol_union_bytes[32:36])[0]
        # 36:40 Max Per Hour 4-Byte Float
        protocol_union['max_per_hour'] = None
        if swithes['max_per_hour']:
            protocol_union['max_per_hour'] = struct.unpack('!f', protocol_union_bytes[36:40])[0]
        # 40:44 Max Per Interval 4-Byte Float
        protocol_union['max_per_interval'] = None
        if swithes['max_per_interval']:
            protocol_union['max_per_interval'] = struct.unpack('!f', protocol_union_bytes[40:44])[0]
        # 44:48 Concentration 4-Byte Float
        protocol_union['concentration'] = None
        if swithes['concentration']:
            protocol_union['concentration'] = struct.unpack('!f', protocol_union_bytes[44:48])[0]
        # 48:52 Drug Amount  4-Byte Float
        protocol_union['drug_amount'] = None
        if swithes['drug_amount']:
            protocol_union['drug_amount'] = struct.unpack('!f', protocol_union_bytes[48:52])[0]
        # 52:56 Solvent Volume 4-Byte Float
        protocol_union['dilute_volume'] = None
        if swithes['dilute_volume']:
            protocol_union['dilute_volume'] = struct.unpack('!f', protocol_union_bytes[52:56])[0]
        # 56:60 Weight 4-Byte Float
        protocol_union['weight'] = None
        if swithes['weight']:
            protocol_union['weight'] = struct.unpack('!f', protocol_union_bytes[56:60])[0]
    return protocol_union


def parse_infusion_data_log(protocol_hex):
    '''parse infusion data log'''
    infusion_data = {}
    if len(protocol_hex) == 16 * 32:
        # ['protocol'] 0:160
        infusion_data['protocol'] = get_protocol_union(protocol_hex)
        # ['switches'] 160:168
        infusion_data['switches'] = get_protocol_switches(protocol_hex)
        # ['protocol_crc'] 168:176
        infusion_data['crc'] = protocol_hex[168:176]
        # ['auth_role'] 176:180
        infusion_data['auth_role'] = int(protocol_hex[176:180], 16)
        # ['rate_factor'] 180:184
        infusion_data['rate_factor'] = int(protocol_hex[180:184], 16)
        # ['concentration_modifiable'] 184:186
        infusion_data['concentration_modifiable'] = int(protocol_hex[184:186], 16) == int(1)
        # ['infusion_mode'] 186:188
        infusion_data['infusion_mode'] = get_protocol_infusion_mode(protocol_hex)
        # ['id'] 188:190
        infusion_data['id'] = int(protocol_hex[188:190], 16)
        # ['label_pool_id] 190:192
        infusion_data['label_pool_id'] = int(protocol_hex[190:192], 16)
        # ['label_id'] 192:194
        infusion_data['label_id'] = int(protocol_hex[192:194], 16)
        # ['rate_unit'] 194:196
        infusion_data['rate_unit'] = get_protocol_rate_unit(protocol_hex)
        # ['concentration_unit'] 196:198
        infusion_data['concentration_unit'] = get_protocol_drug_unit(protocol_hex)
        # ['name'] 198:218
        infusion_data['name'] = get_protocol_name(protocol_hex)
        # ['drug_name'] 218:238
        infusion_data['drug_name'] = get_protocol_drug_name(protocol_hex)
        # ['drug_components'] 238:448
        # infusion_data['drug_components'] = get_protocol_drug_components(protocol_hex)
        infusion_data['drug_components'] = None
        # ['protocol_index'] 448:450
        infusion_data['protocol_index'] = int(protocol_hex[448:450], 16)
        # ['view_index'] 450:452
        infusion_data['view_index'] = int(protocol_hex[450:452], 16)
        # ['label_index'] 452:454
        infusion_data['label_index'] = int(protocol_hex[452:454], 16)
    elif len(protocol_hex) == 2 * 32:
        switcher = {
            2: 'Daily 1',
            3: 'Nightly',
            4: 'Daily 2'
        }
        protocol_bytes = bytes.fromhex(protocol_hex)
        name_id = int(int.from_bytes(protocol_bytes[0:4], 'big'))
        infusion_data['name'] = switcher.get(name_id, 'Unknown_Name')
        infusion_data['cont_dose_rate'] = struct.unpack('!f', protocol_bytes[4:8])[0]
        # infusion_data['rate_hex'] = protocol_hex[0:8]
        infusion_data['vtbi'] = struct.unpack('!f', protocol_bytes[8:12])[0]
        infusion_data['starting_dose'] = struct.unpack('!f', protocol_bytes[12:16])[0]
        infusion_data['extra_dose'] = struct.unpack('!f', protocol_bytes[16:20])[0]
        infusion_data['extra_dose_lockout'] = int(int.from_bytes(protocol_bytes[20:24], 'big'))
        # infusion_data['db_lockout_hex'] = protocol_hex[32:40]
    else:
        infusion_data = {'content': 'empty'}
    return infusion_data


def get_send_rx_error_messge(error_code):
    '''get error message'''
    switcher = { 
        0: 'No_Error',
        1: 'SEND_RX_ERROR_UNEXPECTED_INITIALIZATION_INPUT',
        2: 'SEND_RX_ERROR_SERIAL_NUMBER',
        3: 'SEND_RX_ERROR_LIBRARY_BUILDER_LIBRARY_AUTHENTICATION',
        4: 'SEND_RX_ERROR_LIBRARY_BUILDER_PROTOCOL_CRC',
        5: 'SEND_RX_ERROR_STATE',
        6: 'SEND_RX_ERROR_DATA_INTEGRITY',
        7: 'SEND_RX_ERROR_ENCRYPTION_AUTHORIZATION',
        8: 'Unknown_Error',
    }
    # get() method of dictionary data type returns  
    # value of passed argument if it is present  
    # in dictionary otherwise second argument will 
    # be assigned as default value of passed argument 
    return switcher.get(error_code, "Unknown_Error")


def input_digits(serial_comm, digits_str):
    '''Input Number (on the pump)'''
    # print('Input Digits [{}]...'.format(digits_str))
    # time.sleep(_TIMEOUT * 10)
    # Input Digits
    for index in range(len(digits_str)):
        digit = int(digits_str[index])
        if digit > 5:
            while digit < 10:
                serial_comm.press_key(_DOWN_KEY, _SHORT_PRESS)
                print('key: Down (short)')
                time.sleep(_TIMEOUT * 2)
                digit += 1
        else: 
            while digit > 0:
                serial_comm.press_key(_UP_KEY, _SHORT_PRESS)
                print('key: Up (short)')
                time.sleep(_TIMEOUT * 2)
                digit -= 1
        serial_comm.press_key(_OK_KEY, _SHORT_PRESS)
        print('key: Ok (short)')
        time.sleep(_TIMEOUT * 2)


def reset_battery(serial_comm):
    '''Reset Battery (on the pump)'''
    print('==')
    print('Reset Battery...')
    time.sleep(_TIMEOUT * 2)
    #
    return_text = serial_comm.press_key(_INFO_KEY, _LONG_PRESS)
    if len(return_text) == 4 and return_text[0:2] == 'KE':
        print('key: Info (long)')
    time.sleep(_TIMEOUT * 2)
    #
    return_text = serial_comm.press_key(_DOWN_KEY, _SHORT_PRESS)
    if len(return_text) == 4 and return_text[0:2] == 'KE':
        print('key: Down (short)')
    time.sleep(_TIMEOUT * 2)
    #
    return_text = serial_comm.press_key(_OK_KEY, _SHORT_PRESS)
    if len(return_text) == 4 and return_text[0:2] == 'KE':
        print('key: Ok (short)')
    time.sleep(_TIMEOUT * 2)
    #
    return_text = serial_comm.press_key(_DOWN_KEY, _SHORT_PRESS)
    if len(return_text) == 4 and return_text[0:2] == 'KE':
        print('key: Down (short)')
    time.sleep(_TIMEOUT * 2)
    #
    return_text = serial_comm.press_key(_OK_KEY, _SHORT_PRESS)
    if len(return_text) == 4 and return_text[0:2] == 'KE':
        print('key: Ok (short)')
    time.sleep(_TIMEOUT * 2)
    #
    return_text = serial_comm.press_key(_INFO_KEY, _LONG_PRESS)
    if len(return_text) == 4 and return_text[0:2] == 'KE':
        print('key: Info (long)')
    time.sleep(_TIMEOUT * 2)
    
    
def select_protocol(serial_comm, library, protocol):
    '''Select Protocol (on the pump)'''
    protocol_id = protocol['id']
    node_children = library.library['content']['node']['children']
    protocol_navi_path = library.get_protocol_navi_path(protocol_id, node_children)
    # convert Python Dictionary to JSON:
    # protocol_navi_path_json = json.dumps(protocol_navi_path, indent=4)
    # print(protocol_navi_path_json)
    # Go back to the [Top] menu
    print('==')
    print('Go back to [Top] menu...')
    time.sleep(_TIMEOUT * 2)
    #
    navi_path_len = len(protocol_navi_path)
    while navi_path_len >= 0:
        return_text = serial_comm.press_key(_INFO_KEY, _SHORT_PRESS)
        if len(return_text) == 4 and return_text[0:2] == 'KE':
            print('key: Back (short)')
        time.sleep(_TIMEOUT * 2)
        navi_path_len -= 1
    # Reset Battery
    reset_battery(serial_comm)
    # Select [New Rx]
    print('==')
    print('Select [New Rx]...')
    time.sleep(_TIMEOUT * 2)
    #
    return_text = serial_comm.press_key(_DOWN_KEY, _SHORT_PRESS)
    if len(return_text) == 4 and return_text[0:2] == 'KE':
        print('key: Down (short)')
    time.sleep(_TIMEOUT * 2)
    # Enter [New Rx]
    return_text = serial_comm.press_key(_OK_KEY, _SHORT_PRESS)
    if len(return_text) == 4 and return_text[0:2] == 'KE':
        print('key: Ok/Enter (short)')
    time.sleep(_TIMEOUT * 2)
    #
    # Go back to the [Top] menu the 2nd Time
    print('==')
    print('Go back to [Top] menu...')
    time.sleep(_TIMEOUT * 2)
    #
    navi_path_len = len(protocol_navi_path)
    while navi_path_len >= 0:
        return_text = serial_comm.press_key(_INFO_KEY, _SHORT_PRESS)
        if len(return_text) == 4 and return_text[0:2] == 'KE':
            print('key: Back (short)')
        time.sleep(_TIMEOUT * 2)
        navi_path_len -= 1
    # Select [New Rx]
    print('==')
    print('Select [New Rx]...')
    time.sleep(_TIMEOUT * 2)
    #
    return_text = serial_comm.press_key(_DOWN_KEY, _SHORT_PRESS)
    if len(return_text) == 4 and return_text[0:2] == 'KE':
        print('key: Down (short)')
    time.sleep(_TIMEOUT * 2)
    # Enter [New Rx]
    return_text = serial_comm.press_key(_OK_KEY, _SHORT_PRESS)
    if len(return_text) == 4 and return_text[0:2] == 'KE':
        print('key: Ok/Enter (short)')
    time.sleep(_TIMEOUT * 2)
    # Go to the selected protocol
    print('==')
    print('Select [{}]...'.format(protocol['content']['name'].strip(' \t\r\n\0')))
    time.sleep(_TIMEOUT * 2)
    #
    pin_entered = False
    for each_navi_node in protocol_navi_path:
        index = each_navi_node['menu_position']
        while index > 0:
            # Press [Down] Key
            return_text = serial_comm.press_key(_DOWN_KEY, _SHORT_PRESS)
            if len(return_text) == 4 and return_text[0:2] == 'KE':
                print('key: Down (short)')
            time.sleep(_TIMEOUT * 2)
            index -= 1
        # Press [Ok] Key
        return_text = serial_comm.press_key(_OK_KEY, _SHORT_PRESS)
        if len(return_text) == 4 and return_text[0:2] == 'KE':
            print('key: Ok/Enter (short)')
        time.sleep(_TIMEOUT * 2)
        # Enter Pin
        if each_navi_node['auth'][0]['pin'] != '' and not pin_entered:
            pin_number = each_navi_node['auth'][0]['pin']
            # Input PIN number
            print('==')
            print('Input PIN number [{}]...'.format(pin_number))
            time.sleep(_TIMEOUT * 2)
            #
            input_digits(serial_comm, pin_number)
            pin_entered = True
     

def set_parameter_value(serial_comm, new_value, parameter):
    '''Set Parameter Value on the Pump
       parameter include the following information:
        length       - total length of the parameter
        fract_length - length of fractional part of the parameter
        value        - the value of the parameter
        unit         - the unit of the parameter
        name         - the name of the parameter
    '''
    old_value = parameter['value']
    max_value = parameter['max']
    min_value = parameter['min']
    fract_length = parameter['fract_length']
    length = parameter['length']
    # Translate new and old values if the unit is [minute]
    if parameter['unit'] == 'minute':
        new_value_str = str(int(new_value / 60))
        new_value_str = new_value_str + str(int(new_value % 60)).zfill(2)
        new_value = int(new_value_str)
        
        old_value_str = str(int(old_value / 60))
        old_value_str = old_value_str + str(int(old_value % 60)).zfill(2)
        old_value = int(old_value_str)
        
        max_value_str = str(int(max_value / 60))
        max_value_str = max_value_str + str(int(max_value % 60)).zfill(2)
        max_value = int(max_value_str)
        
        min_value_str = str(int(min_value / 60))
        min_value_str = min_value_str + str(int(min_value % 60)).zfill(2)
        min_value = int(min_value_str)
    #
    old_value = str(int(old_value * pow(10, fract_length))).zfill(length)
    max_value = str(int(max_value * pow(10, fract_length))).zfill(length)
    min_value = str(int(min_value * pow(10, fract_length))).zfill(length)
    new_value = str(int(new_value * pow(10, fract_length))).zfill(length)
    print('old_value = {}'.format(old_value))
    print('new_value = {}'.format(new_value))
    #
    if parameter['name'] == 'diluteVolume':
        index = 3
        while index > 0:
            # Press [Ok] Key / Skip over the [Drug Amount]
            serial_comm.press_key(_OK_KEY, _SHORT_PRESS)
            print('key: Ok (short)')
            time.sleep(_TIMEOUT * 2)
            index -= 1
    # Set value from [OLD] value to [MIN] value
    print('==')
    print('Set value from [{}] to [{}]'.format(old_value, min_value))
    time.sleep(_TIMEOUT * 2)
    # diff_value = ''
    for index in range(length):
        diff = int(min_value[index]) - int(old_value[index])
        if diff < 0:
            while diff < 0:
                # Press [Down] Key
                serial_comm.press_key(_DOWN_KEY, _SHORT_PRESS)
                print('key: Down (short)')
                time.sleep(_TIMEOUT * 2)
                diff += 1
        if diff > 0:
            while diff > 0:
                # Press [Up] Key
                serial_comm.press_key(_UP_KEY, _SHORT_PRESS)
                print('key: Up (short)')
                time.sleep(_TIMEOUT * 2)
                diff -= 1
        # Press [Ok] Key
        serial_comm.press_key(_OK_KEY, _SHORT_PRESS)
        print('key: Ok (short)')
        time.sleep(_TIMEOUT * 2)
    #
    if parameter['name'] == 'drugAmount':
        index = 3
        while index > 0:
            # Press [Ok] Key / Skip over the [Dilute Volume]
            serial_comm.press_key(_OK_KEY, _SHORT_PRESS)
            print('key: Ok (short)')
            time.sleep(_TIMEOUT * 2)
            index -= 1
    # Press [Ok] Key / Enter the Parameter Agian
    serial_comm.press_key(_OK_KEY, _SHORT_PRESS)
    print('key: Ok (short)')
    time.sleep(_TIMEOUT * 2)
    #
    if parameter['name'] == 'diluteVolume':
        index = 3
        while index > 0:
            # Press [Ok] Key / Skip over the [Drug Amount]
            serial_comm.press_key(_OK_KEY, _SHORT_PRESS)
            print('key: Ok (short)')
            time.sleep(_TIMEOUT * 2)
            index -= 1
    # Set value from [MIN] value to [MAX] value
    print('==')
    print('Set value from [{}] to [{}]'.format(min_value, max_value))
    time.sleep(_TIMEOUT * 2)
    for index in range(length):
        diff = int(max_value[index]) - int(min_value[index])
        if int(min_value[index]) > 0 and diff >= 0 and index > 0:
            diff = int(min_value[index])
            while diff > 0:
                # Press [Down] Key
                serial_comm.press_key(_DOWN_KEY, _SHORT_PRESS)
                print('key: Down (short)')
                time.sleep(_TIMEOUT * 2)
                diff -= 1
        # Press [Down] Key
        serial_comm.press_key(_DOWN_KEY, _SHORT_PRESS)
        print('key: Down (short)')
        time.sleep(_TIMEOUT * 2)
        # Press [Ok] Key
        serial_comm.press_key(_OK_KEY, _SHORT_PRESS)
        print('key: Ok (short)')
        time.sleep(_TIMEOUT * 2)
    #
    if parameter['name'] == 'drugAmount':
        index = 3
        while index > 0:
            # Press [Ok] Key / Skip over the [Dilute Volume]
            serial_comm.press_key(_OK_KEY, _SHORT_PRESS)
            print('key: Ok (short)')
            time.sleep(_TIMEOUT * 2)
            index -= 1
    # Press [Ok] Key Enter the Parameter Agian
    serial_comm.press_key(_OK_KEY, _SHORT_PRESS)
    print('key: Ok (short)')
    time.sleep(_TIMEOUT * 2)
    #
    if parameter['name'] == 'diluteVolume':
        index = 3
        while index > 0:
            # Press [Ok] Key / Skip over the [Drug Amount]
            serial_comm.press_key(_OK_KEY, _SHORT_PRESS)
            print('key: Ok (short)')
            time.sleep(_TIMEOUT * 2)
            index -= 1
    # Set value from [MAX] value to [NEW] value
    print('==')
    print('Set value from [{}] to [{}]'.format(max_value, new_value))
    time.sleep(_TIMEOUT * 2)
    # diff_value = ''
    raise_base = True
    for index in range(length):
        diff = int(new_value[index]) - int(max_value[index])
        if diff < 0:
            while diff < 0:
                # Press [Down] Key
                serial_comm.press_key(_DOWN_KEY, _SHORT_PRESS)
                print('key: Down (short)')
                time.sleep(_TIMEOUT * 2)
                diff += 1
        if diff > 0:
            if raise_base and int(min_value[index]) > int(max_value[index]):
                diff = diff - (int(min_value[index]) - int(max_value[index])) + 1
            while diff > 0:
                # Press [Up] Key
                serial_comm.press_key(_UP_KEY, _SHORT_PRESS)
                print('key: Up (short)')
                time.sleep(_TIMEOUT * 2)
                diff -= 1
        # Press [Ok] Key
        serial_comm.press_key(_OK_KEY, _SHORT_PRESS)
        print('key: Ok (short)')
        time.sleep(_TIMEOUT * 2)
        # 
        if int(new_value[index]) > int(min_value[index]):
            raise_base = False
    #
    if parameter['name'] == 'drugAmount':
        index = 3
        while index > 0:
            # Press [Ok] Key / Skip over the [Dilute Volume]
            serial_comm.press_key(_OK_KEY, _SHORT_PRESS)
            print('key: Ok (short)')
            time.sleep(_TIMEOUT * 2)
            index -= 1


def parse_key_list(key_list_str):
    '''
    parse the key list
    input:
        key_list_str - A string of key press each key press is 2-digit.
                       The first digit is the key type
                       The second digit is the key duration
    '''
    short_press_switcher = {
        _UP_KEY: 'up',
        _DOWN_KEY: 'down',
        _INFO_KEY: 'back',
        _OK_KEY: 'ok',
        _POWER_KEY: '#',
        _RUN_KEY: 'mute',
        _BOLUS_KEY: 'bolus'
    }
    long_press_switcher = {
        _UP_KEY: '#',
        _DOWN_KEY: '#',
        _INFO_KEY: 'info',
        _OK_KEY: '#',
        _POWER_KEY: '#',
        _RUN_KEY: 'run',
        _BOLUS_KEY: '#',
        _STOP_KEY: 'stop'
    }

    key_list = []
    current_key = ''
    for i in range(int(len(key_list_str) / 2)):
        key_type = key_list_str[2 * i]
        # print('key_type = {}'.format(key_type))
        key_duration = key_list_str[2 * i + 1]
        # print('key_duration = {}'.format(key_duration))
        if key_duration == _SHORT_PRESS:
            current_key = short_press_switcher.get(key_type, "Unknown Key ({})".format(key_list_str[2 * i:2 * i + 2]))
        elif key_duration == _LONG_PRESS:
            current_key = long_press_switcher.get(key_type, "Unknown Key ({})".format(key_list_str[2 * i:2 * i + 2]))
        if current_key != '':
            # print('current_key = {}'.format(current_key))
            key_list.append(current_key)
    return key_list


class SerialComm:
    '''Serial Communication class'''
    _CONSTANT = 0

    def __init__(self, s_port):
        # self.event_log_monitor = EventLogMonitor()
        # self.protocol = None
        # self.protocol_name = ''
        # self.rx_path = ''
        # Create a mutex
        self.lock = Lock()
        # Serial config data structure
        self.serial_config = {"port": s_port, \
                              "baud_rate": _BAUD_RATE, \
                              "byte_size": _BYTE_SIZE, \
                              "stop_bits": _STOPBITS, \
                              "parity": _PARITY, \
                              "flow_control": _FLOW_CONTROL, \
                              "timeout": _TIMEOUT, \
                              "write_timeout": _WRITE_TIMEOUT
                              }
        # self.serial = None
        # create a serial object
        # print('Initializing Serial Port [{}] Connection...'.format(s_port))
        # print('==')
        self.serial = serial.Serial(s_port, self.serial_config['baud_rate'], \
                                    timeout=_TIMEOUT, \
                                    write_timeout=_WRITE_TIMEOUT)
        self.serial.bytesize = self.serial_config['byte_size']
        self.serial.stopbits = self.serial_config['stop_bits']
        self.serial.parity = self.serial_config['parity']
        self.serial.xonxoff = self.serial_config['flow_control']
        self.serial.rtscts = self.serial_config['flow_control']
        self.serial.timeout = self.serial_config['timeout']
        self.serial.write_timeout = self.serial_config['write_timeout']
        # print('Serial Port [{}] Connected'.format(s_port))
        # print('==')
        #
        # pump type is in ['caps', 'h', 'k']
        self.pump_type = None
        # pump time offset
        self.pump_time_offset = -1
        # disable S9 function
        self.disable_s9_command()

    def load_serial_config(self):
        """Load Serial Configuration from a Json File"""
        # read json file
        file = open(self.serial_config_path, "r")
        serial_config_json = file.read()
        file.close()
        # convert JSON to Python Dict
        self.serial_config = json.loads(serial_config_json)

    def save_serial_config(self):
        """Save Serial Configuration to a Json File
        Serial Configuration contains:
            - baud_rate
            - byte_size
            - stop_bits
            - parity
            - flow_control
            - timeout
            - write_timeout
        """
        # convert Python Dict to JSON:
        serial_config_json = json.dumps(self.serial_config, indent=4)
        # Save to json file
        file = open(self.serial_config_path, "w")
        file.write(serial_config_json)
        file.close()

    def read_single_event_log(self, index):
        '''read event log with index
            index - event log index number (data type: integer)
        '''
        # Event log index construction
        # Each page 4096 bytes, each event 16 bytes, 256 events, totally 169 pages long.
        # use [index mod (256 * 169)] to determine the real index value.
        index = int(index)
        event_log_index = hex(index % EVENT_LOG_NUMBER_OF_EVENTS)[2:].upper()
        if len(event_log_index) > 8:
            event_log_index = event_log_index[len(event_log_index) - 8:]
        elif len(event_log_index) < 8:
            while len(event_log_index) < 8:
                event_log_index = '0' + event_log_index
        return_text = self.query('RE' + event_log_index)
        print('return = {}'.format(return_text), end='\r')
        # print(len(return_text))
        if len(return_text) != 42 or return_text[0:2] != 'RE':
            return_text = ''
        return return_text
    
    def query(self, sent_text):
        '''query'''
        sent_text = sent_text.upper()
        return_text = ''
        try:
            ############################################################################
            #                          CRITICAL SECTION START                          #
            #                                                                          #
            
            # Acquire Mutex
            self.lock.acquire()
            # print("lock.acquire")
            
            sent_message = build_message(sent_text)
            self.serial.write(sent_message)
            self.serial.flush()
            time.sleep(_TIMEOUT)
            if sent_text[0:2] == 'W1':
                time.sleep(_TIMEOUT * 2)
            # trim / remove trailing NULL(0x00) spaces from a string
            return_text = self.serial.readline()
            # print('len(return_text) = {}'.format(len(return_text)))
            return_text = return_text.decode().rstrip(' \t\r\n\0')
            return_text = re.sub(r'[\x00-\x1F]+', '', return_text)
            return_text = return_text[0:len(return_text) - 2].upper()
            # time.sleep(_TIMEOUT)
            
            # Release Mutex
            self.lock.release()
            # print("lock.release")
            #                                                                          #
            #                          CRITICAL SECTION END                            #
            ############################################################################
            return return_text
        except:
            traceback.print_exc()
            self.lock.release()
            # print("lock.release")
            raise
        
    def write(self, sent_text):
        '''write'''
        sent_text = sent_text.upper()
        try:
            ############################################################################
            #                          CRITICAL SECTION START                          #
            #                                                                          #
            
            # Acquire Mutex
            self.lock.acquire()
            # print("lock.acquire")
            
            sent_message = build_message(sent_text)
            self.serial.write(sent_message)
            self.serial.flush()
            time.sleep(_TIMEOUT)
            if sent_text[0:2] == 'W1':
                # [W1] command is a [write_calibration] function
                time.sleep(_TIMEOUT * 2)
            # Release Mutex
            self.lock.release()
            # print("lock.release")
            #                                                                          #
            #                          CRITICAL SECTION END                            #
            ############################################################################
        except:
            traceback.print_exc()
            self.lock.release()
            # print("lock.release")
            raise
    
    def read(self):
        '''read'''
        return_text = ''
        try:
            ############################################################################
            #                          CRITICAL SECTION START                          #
            #                                                                          #
            
            # Acquire Mutex
            self.lock.acquire()
            # print("lock.acquire")
                       
            # trim / remove trailing NULL(0x00) spaces from a string
            return_text = self.serial.readline()
            # print('len(return_text) = {}'.format(len(return_text)))
            return_text = return_text.decode().rstrip(' \t\r\n\0')
            return_text = re.sub(r'[\x00-\x1F]+', '', return_text)
            return_text = return_text[0:len(return_text) - 2].upper()
            # time.sleep(_TIMEOUT)
            
            # Release Mutex
            self.lock.release()
            # print("lock.release")
            #                                                                          #
            #                          CRITICAL SECTION END                            #
            ############################################################################
            return return_text
        except:
            traceback.print_exc()
            self.lock.release()
            # print("lock.release")
            raise
            
    def close(self):
        '''close serial port'''
        self.serial.close()
        
    def read_infusion_data_log(self, index, event_logs_size=EVENT_LOGS_PER_INFUSION_DATA_LOG):
        '''read infusion data log
            the infusion data log is build with [event_logs_size] event log
            each event log
        '''
        index_offset = 0
        infusion_data_log_data_hex = ''
        while index_offset < event_logs_size:
            return_text = self.read_single_event_log(index + index_offset)
            if len(return_text) == 42 and return_text[0:2] == 'RE':
                hex_event_log = return_text[10:42]
                infusion_data_log_data_hex += hex_event_log
            index_offset += 1
        if len(infusion_data_log_data_hex) != event_logs_size * 32:
            infusion_data_log_data_hex = ''
        return infusion_data_log_data_hex

    def search_event(self, event_type=''):
        '''search through the event logs for a specific event type
            return - event log hex'''
        return_event_log_hex = ''
        event_log_index = self.read_event_log_indices()        
        event_log_index_head = int(event_log_index['head'], 16)
        event_log_index_tail = int(event_log_index['tail'], 16)
        if event_log_index_tail > event_log_index_head: 
            event_log_index_head += EVENT_LOG_NUMBER_OF_EVENTS       
        #
        num_to_search = event_log_index_head - event_log_index_tail + 1
        event_logs = []
        
        if num_to_search == 0:
            print('Abort: NO event log is to be printed')
        else:
            # Update [self.pump_time_offset]
            self.read_pump_time()
            while len(event_logs) < num_to_search:
                if event_log_index_tail > event_log_index_head:
                    break
                # Rotation buffer. Pointer need to be reset when hit 0
                if event_log_index_head < 0:
                    event_log_index_head += EVENT_LOG_NUMBER_OF_EVENTS
                single_event_log = self.read_single_event_log(event_log_index_head)
                if len(single_event_log) == 42 and single_event_log[0:2] == 'RE':
                    event_log_hex = single_event_log[10:42]
                    # Get Event Log Type
                    event_log_type = get_event_log_type(event_log_hex)
                    event_log_sub_type = get_event_log_sub_type(event_log_hex)
                    if len(event_logs) < num_to_search:
                        if event_log_type != 'INFUSION_DATA':
                            event_logs.insert(0, event_log_hex)
                            if event_type in [event_log_type, event_log_sub_type]:
                                return_event_log_hex = event_log_hex
                                
                                break
                        elif event_log_type == 'INFUSION_DATA':
                            # INFUSION_DATA 0
                            if event_log_sub_type == 'INFUSION_DATA_BEGIN':
                                event_logs.insert(0, event_log_hex)
                                if event_type == event_log_sub_type:
                                    return_event_log_hex = event_log_hex
                                    break
                            elif event_log_sub_type == 'INFUSION_DATA_END':
                                event_logs.insert(0, event_log_hex)
                                if event_type == event_log_sub_type:
                                    return_event_log_hex = event_log_hex
                                    break
                                # Try out the correct infusion data log size
                                tentative_return_text = self.read_single_event_log(event_log_index_head - 2 - 1)
                                if len(tentative_return_text) == 42 and tentative_return_text[0:2] == 'RE':
                                    tentative_event_log_hex = tentative_return_text[10:42]
                                    tentative_event_log = parse_event_log(tentative_event_log_hex, self.pump_time_offset)
                                    if tentative_event_log['infusion_data_frame'] == 'INFUSION_DATA_BEGIN':
                                        infusion_data_log_size = 2
                                    else:
                                        infusion_data_log_size = 16
                                #
                                event_log_index_head -= infusion_data_log_size
                                infusion_data_hex = self.read_infusion_data_log(event_log_index_head, infusion_data_log_size)
                                event_logs.insert(0, infusion_data_hex)
                                if event_type == 'INFUSION_DATA':
                                    return_event_log_hex = infusion_data_hex
                                    break
                else:
                    print("Reading [Event Log] Failed")
                #
                event_log_index_head -= 1
            print()
        return return_event_log_hex
        
    def read_multiple_event_log(self, num_to_print=-1):
        '''Reda Multiple Event Log'''
        event_log_index = self.read_event_log_indices()        
        event_log_index_head = int(event_log_index['head'], 16)
        event_log_index_tail = int(event_log_index['tail'], 16)
        if event_log_index_tail > event_log_index_head: 
            event_log_index_head += EVENT_LOG_NUMBER_OF_EVENTS       
        #
        if num_to_print < 0:
            print('Querying [ALL] event log...')
            num_to_print = event_log_index_head - event_log_index_tail + 1
        else:
            print('Querying [{}] event log...'.format(num_to_print))
        event_logs = []
        if num_to_print == 0:
            print('Abort: NO event log is to be printed')
        else:
            # Update [self.pump_time_offset]
            self.read_pump_time()
            while len(event_logs) < num_to_print:
                if event_log_index_tail > event_log_index_head:
                    break
                # Rotation buffer. Pointer need to be reset when hit 0
                if event_log_index_head < 0:
                    event_log_index_head += EVENT_LOG_NUMBER_OF_EVENTS
                return_text = self.read_single_event_log(event_log_index_head)
                if len(return_text) == 42 and return_text[0:2] == 'RE':
                    event_log_hex = return_text[10:42]
                    each_event_log = parse_event_log(event_log_hex, self.pump_time_offset)
                    event_logs.insert(0, each_event_log)
                    if len(event_logs) < num_to_print and \
                            each_event_log['event_type'] == 'INFUSION_DATA' and \
                            each_event_log['infusion_data_frame'] == 'INFUSION_DATA_END':
                        print('event_type = INFUSION_DATA', end='\r')
                        print('infusion_data_frame = INFUSION_DATA_END', end='\r')
                        # Try out the correct infusion data log size
                        tentative_return_text = self.read_single_event_log(event_log_index_head - 2 - 1)
                        if len(tentative_return_text) == 42 and tentative_return_text[0:2] == 'RE':
                            tentative_event_log_hex = tentative_return_text[10:42]
                            tentative_event_log = parse_event_log(tentative_event_log_hex, self.pump_time_offset)
                            if tentative_event_log['infusion_data_frame'] == 'INFUSION_DATA_BEGIN':
                                infusion_data_log_size = 2
                            else:
                                infusion_data_log_size = 16
                        #
                        event_log_index_head -= infusion_data_log_size
                        infusion_data_hex = self.read_infusion_data_log(event_log_index_head, infusion_data_log_size)
                        # print('infusion data hex = {}'.format(infusion_data_hex))
                        infusion_data = parse_infusion_data_log(infusion_data_hex)
                        event_logs.insert(0, infusion_data)
                    elif each_event_log['event_type'] == 'INFUSION_DATA' and \
                            each_event_log['infusion_data_frame'] == 'INFUSION_DATA_BEGIN':
                        print('event_type = INFUSION_DATA', end='\r')
                        print('infusion_data_frame = INFUSION_DATA_BEGIN', end='\r')
                else:
                    print("Reading [Event Log] Failed")
                event_log_index_head -= 1
        return event_logs

    def read_range_event_log(self, start_index, end_index):
        number_to_print = int((EVENT_LOG_NUMBER_OF_EVENTS + end_index - start_index) \
                                % EVENT_LOG_NUMBER_OF_EVENTS)
        event_logs = []
        offset = 1
        print()
        print('start_index = {}'.format(start_index))
        print('end_index = {}'.format(end_index))
        print('number_to_print = {}'.format(number_to_print))
        # Update the [pump_time_offset] 
        self.read_pump_time()
        while offset <= number_to_print:
            index = (start_index + offset) % EVENT_LOG_NUMBER_OF_EVENTS
            return_text = self.read_single_event_log(index)
            if len(return_text) == 42 and return_text[0:2] == 'RE':
                event_log_hex = return_text[10:42]
                each_event_log = parse_event_log(event_log_hex, self.pump_time_offset)
                event_logs.append(each_event_log)
                if len(event_logs) < number_to_print and \
                        each_event_log['event_type'] == 'INFUSION_DATA' and \
                        each_event_log['infusion_data_frame'] == 'INFUSION_DATA_BEGIN':
                    # Try out the correct infusion data log size
                    tentative_return_text = self.read_single_event_log(index + 2 + 1)
                    if len(tentative_return_text) == 42 and tentative_return_text[0:2] == 'RE':
                        tentative_event_log_hex = tentative_return_text[10:42]
                        tentative_event_log = parse_event_log(tentative_event_log_hex, self.pump_time_offset)
                        if tentative_event_log['infusion_data_frame'] == 'INFUSION_DATA_END':
                            infusion_data_log_size = 2
                        else:
                            infusion_data_log_size = 16
                    #
                    print('event_type = {}'.format(each_event_log['event_type']))
                    print('infusion_data_frame = {}'.format(each_event_log['infusion_data_frame']))
                    #
                    infusion_data_hex = self.read_infusion_data_log(start_index + offset + 1, infusion_data_log_size)
                    # print('infusion data hex = {}'.format(infusion_data_hex))
                    infusion_data = parse_infusion_data_log(infusion_data_hex)
                    event_logs.append(infusion_data)
                    offset += infusion_data_log_size
                elif each_event_log['event_type'] == 'INFUSION_DATA' and \
                        each_event_log['infusion_data_frame'] == 'INFUSION_DATA_END':
                    print('event_type = {}'.format(each_event_log['event_type']))
                    print('infusion_data_frame = {}'.format(each_event_log['infusion_data_frame']))
            else:
                print("Reading [Event Log] Failed")
            offset += 1
        return event_logs 

    def read_event_log_indices(self):
        '''Read event log index'''
        # the event log start with Tail and end with Head
        # whenever a new log is generated, the Head index increases by 1
        event_log_index = {'tail': '',
                           'head': ''}
        return_text = self.query('RI')
        # print('return_text = {}'.format(return_text))
        # print('len(return_text) = {}'.format(len(return_text)))
        # return_text includes the command 'RI'
        if len(return_text) == 18 and return_text[0:2] == 'RI':
            event_log_index['tail'] = return_text[2:10]
            event_log_index['head'] = return_text[10:18]
        return event_log_index
        
    def get_pump_sn(self):
        '''Get pump serial number'''
        serial_number = ''
        
        return_text = self.query('RN')
#         print(return_text)
#         print(len(return_text))
        return_text = re.match(r'.*((RN)([A-Z0-9]{8}))', return_text)
        if return_text is not None:
            return_text = return_text[1]
        else:
            return_text = ''
        if len(return_text) == 10 and return_text[0:2] == 'RN':
            serial_number = return_text[2:10]
        return serial_number

    def set_pump_sn(self, serial_number):
        '''Set pump serial number'''
        return_text = self.query('WN' + serial_number)
        # print(len(return_text))
        status = len(return_text) == 2 and return_text[0:2] == 'WN'
        return status
    
    def disable_s9_command (self):
        '''Disable S9 command output'''
        return_text = self.query('W0' + '0')
#         print(return_text)
#         print('len(return_text) = {}'.format(len(return_text)))
        status = len(return_text) == 2 and return_text[0:2] == 'W0'
        return status
    
    def enable_s9_command (self):
        '''Enable S9 command output'''
        return_text = self.query('W0' + '1')
#         print(return_text)
#         print('len(return_text) = {}'.format(len(return_text)))
        status = len(return_text) == 2 and return_text[0:2] == 'W0'
        return status
    
    def get_motor_calibration_factor(self):
        '''Get motor calibration factor'''
        motor_calibration_factor = None
        return_text = self.query('R1')
        print(return_text)
        # print(len(return_text))
        if len(return_text) == 6 and return_text[0:2] == 'R1':
            motor_calibration_factor = int(return_text[2:], 16)
        return motor_calibration_factor

    def get_occlusion_thresholds(self):
        '''Get upstream and downstream thresholds of the occlusion sensor'''
        occlusion_thresholds = {}
        return_text = self.query('R2')
        print(return_text)
        # print(len(return_text))
        return_text = re.match(r'.*((R2)([A-F0-9]{8}))', return_text)
        if return_text is not None:
            return_text = return_text[1]
        else:
            return_text = ''
        if len(return_text) == 10 and return_text[0:2] == 'R2':
            occlusion_thresholds['up'] = int(return_text[2:6], 16)
            occlusion_thresholds['down'] = int(return_text[6:10], 16)
        return occlusion_thresholds

    def set_occlusion_thresholds(self, occlusion_thresholds=None):
        '''Set upstream and downstream thresholds of the occlusion sensor'''
        if occlusion_thresholds is None:
            occlusion_thresholds = {}
            print('Set [Occlusion Thresholds]')
            input('Please remove cassette from the pump first, then hit [ENTER]...')
            message = input('The cassette is removed? (y/n):')
            if message.lower().strip(' \t\r\n\0') not in ['abort', 'n', 'no', '']:
                return_text = self.query('RD')
#                 print(return_text)
                w2_command = return_text.replace("RD", "W2")
#                 print('w2_command = {}'.format(w2_command))
#                 time.sleep(_TIMEOUT * 10)
#                 w2_command = 'W2' + '00FF' + '00FF'
                return_text = self.query(w2_command)
#                 print(return_text)
#                 print('len(return_text) = '.format(len(return_text)))
#                 if len(return_text) == 10 and return_text[0:2] == 'W2':
#                     occlusion_thresholds['up'] = int(return_text[2:6], 16)
#                     occlusion_thresholds['down'] = int(return_text[6:10], 16)
                occlusion_thresholds['up'] = int(w2_command[2:6], 16)
                occlusion_thresholds['down'] = int(w2_command[6:10], 16)
            else:
                print('Aborted: set [occlusion thresholds]')
        else:
            # convert integer to hex string
            up_str = hex(occlusion_thresholds['up'])[2:].zfill(4).upper()
            down_str = hex(occlusion_thresholds['down'])[2:].zfill(4).upper()
            w2_command = 'W2' + up_str + down_str
            print('w2_command = {}'.format(w2_command))
            return_text = self.query(w2_command)
            print(return_text)
            print('len(return_text) = '.format(len(return_text)))
            if len(return_text) == 10 and return_text[0:2] == 'W2':
                occlusion_thresholds['up'] = int(return_text[2:6], 16)
                occlusion_thresholds['down'] = int(return_text[6:10], 16)
        return occlusion_thresholds

    def get_total_volume_infused(self):
        '''Get total volume infused'''
        total_volume_infused = None
        return_text = self.query('R3')
        # print(len(return_text))
        if len(return_text) == 6 and return_text[0:2] == 'R3':
            total_volume_infused = int(return_text[2:], 16)
        return total_volume_infused
        
    def get_battery_voltage(self):
        '''Get Battery Voltage'''
        battery_voltage = None
        return_text = self.query('R7')
        # print(len(return_text))
        if len(return_text) == 6 and return_text[0:2] == 'R7':
            # For MIVA            
            battery_voltage = int(return_text[2:], 16) / 100
        return battery_voltage

    def get_product_life_volume(self):
        '''Get Product Life Volume'''
        product_life_volume = {}
        return_text = self.query('R8')
        # print('return_text = {}'.format(return_text))
        # print(len(return_text))
        if len(return_text) == 12 and return_text[0:2] == 'R8':
            # the last 2-bytes(return_text[12:14]) are checksum bytes
            calibration_factor = int(return_text[2:6], 16)
            #
            total_rotation = int(return_text[6:12], 16)
            # 
            calibration_multiplier = 0.000005
            rmpk = calibration_factor * calibration_multiplier
            total_volume = total_rotation * rmpk 
            #
            product_life_volume['calibration'] = calibration_factor
            product_life_volume['rotation'] = total_rotation
            product_life_volume['volume'] = total_volume
        return product_life_volume
    
    def get_total_pump_on_time(self):
        '''Get total pump ON time (seconds, type = integer)'''
        return_text = self.query('R9')
        # print('return_text = {}'.format(return_text))
        # print(len(return_text))
        if len(return_text) == 10 and return_text[0:2] == 'R9':
            total_pump_on_time = int(return_text[2:10], 16)
        return total_pump_on_time

    def get_battery_calibration_and_voltage(self):
        '''Get Battery Calibration and Voltage'''
        calibration_and_voltage = {}
        return_text = self.query('RA')
        # print('return_text = {}'.format(return_text))
        # print(len(return_text))
        if len(return_text) == 10 and return_text[0:2] == 'RA':
            calibration = int(return_text[2:6], 16) / 1000
            #
            voltage = int(return_text[6:10], 16) / 100
            #
            calibration_and_voltage['calibration'] = calibration
            calibration_and_voltage['voltage'] = voltage
        return calibration_and_voltage
    
    def set_battery_calib(self, calib_factor):
        '''Set Battery Calibration Factor
           calib_factor - Calibration Factor. A float number around 1 (ex. 1.026 or 0.985)
        '''
        calib_factor = int(calib_factor * 1000)
        calib_factor_hex = hex(calib_factor)[2:].zfill(4).upper()
        return_text = self.query('WA' + calib_factor_hex)
        # print('sent_text = {}'.format('WA' + calib_factor_hex))
        print('return_text = {}'.format(return_text))
        print(len(return_text))
        status = len(return_text) == 6 and return_text[0:2] == 'WA'
        return status
    
    def get_base_year(self):
        '''Get Base Year'''
        base_year = None
        return_text = self.query('RB')
        # print('return_text = {}'.format(return_text))
        # print(len(return_text))
        if len(return_text) == 6 and return_text[0:2] == 'RB':
            # the last 2-bytes(return_text[2:6]) are checksum bytes
            base_year = int(return_text[2:6], 16)
        return base_year

    def get_library_name_version(self):
        '''Get Library Version'''
        library_name_version = {}
        return_text = self.query('RL')
        # print('return_text = {}'.format(return_text))
        # print(len(return_text))
        if len(return_text) == 22 and return_text[0:2] == 'RL':
            name_version = return_text[2:22].rstrip(' \t\r\n\0')
            library_name_version['name'] = name_version.split()[0].rstrip(' \t\r\n\0')
            library_name_version['version'] = name_version.split()[1].rstrip(' \t\r\n\0')
        return library_name_version

    def get_software_version(self):
        '''Get Software Version'''
        software_version = ''
        return_text = self.query('RS')
        print(return_text)
        # print(len(return_text))
        return_text = re.match(r'.*((RS)([A-Z0-9.\-]{8}))', return_text)
        if return_text is not None:
            return_text = return_text[1]
        else:
            return_text = ''
        if len(return_text) == 10 and return_text[0:2] == 'RS':
            software_version = return_text[2:10].rstrip(' \t\r\n\0')
        return software_version

    def send_command(self, cmd):
        '''Send [cmd] command to the pump'''
        return_text = ''
        cmd = cmd.upper().rstrip(' \t\r\n\0')
        if cmd in ['INFO']:
            # Send [INFO Key] command
            return_text = self.press_key(Key.INFO_KEY, Key.LONG_PRESS)
            if len(return_text) == 4 and return_text[0:2] == 'KE':
                print('key: Info (long)')
        elif cmd in ['BACK']:
            # Send [INFO] key command (Short)
            return_text = self.press_key(Key.INFO_KEY, Key.SHORT_PRESS)
            if len(return_text) == 4 and return_text[0:2] == 'KE':
                print('key: Back (short)')
        elif cmd in ['RUN']:
            # Send [RUN] key command
            return_status = self.trigger_run_infusion()
            if return_status:
                print('key: Run (long)')
        elif cmd in ['STOP']:
            # Send [STOP] key command
            return_status = self.trigger_stop_infusion()
            if return_status:
                print('key: Stop (long)')
        elif cmd in ['OK', 'ENTER']:
            # Send [OK] key command
            return_text = self.press_key(Key.OK_KEY, Key.SHORT_PRESS)
            if len(return_text) == 4 and return_text[0:2] == 'KE':
                print('key: Ok/Enter (short)')
        elif cmd in ['UP']:
            # Send [UP] key command
            return_text = self.press_key(Key.UP_KEY, Key.SHORT_PRESS)
            if len(return_text) == 4 and return_text[0:2] == 'KE':
                print('key: Up (short)')
        elif cmd in ['DOWN']:
            # Send [DOWN] key command
            return_text = self.press_key(Key.DOWN_KEY, Key.SHORT_PRESS)
            if len(return_text) == 4 and return_text[0:2] == 'KE':
                print('key: Down (short)')
        elif cmd in ['POWER OFF', 'POWEROFF', 'SHUT DOWN', 'SHUTDOWN', 'SHUT OFF', 'SHUTOFF', 'POWER']:
            # Send [POWER] key command
            return_text = self.trigger_power_off()
            if return_text:
                print('key: On/Off (long)')
        elif cmd in ['BOLUS']:
            # Send [BOLUS] key command
            return_text = self.press_key(Key.BOLUS_KEY, Key.SHORT_PRESS)
            if len(return_text) == 4 and return_text[0:2] == 'KE':
                print('key: Bolus (short)')
        elif cmd in ['MUTE']:
            # Send [RUN/STOP] key command
            return_text = self.press_key(Key.RUN_KEY, Key.SHORT_PRESS)
            if len(return_text) == 4 and return_text[0:2] == 'KE':
                print('key: Run/Stop (short)')
        elif re.match(r'(:)(infu(sion)?)(:)(mode)(\?)', cmd.lower()):
            # Query Infusion Mode 
            # Command -- ':INFUsion:MODE?'
            return_text = self.get_infusion_mode()
            # print(':infu:mode? == {}'.format(return_text))
        elif re.match(r'(:)(infu(sion)?)(:)(time)(\?)', cmd.lower()):
            # Query Infusion Time in Seconds? 
            # Command -- ':INFUsion:TIME?'
            return_text = self.get_infusion_time()
            # print(':infu:time? == {0} sec'.format(return_text))
            # print('type(return_text) == {0}'.format(type(return_text)))
        elif re.match(r'(:)(infu(sion)?)(:)(rate)(:)(unit)(\?)', cmd.lower()):
            # Query Infusion Rate Unit? 
            # Command -- ':INFUsion:RATE:UNIT?'
            return_text = self.get_infusion_rate_unit()
            # print(':infu:rate:unit? == {0}'.format(return_text))
        elif re.match(r'(:)(infu(sion)?)(:)(vinf)(\?)', cmd.lower()):
            # Query Infusion Volume Infused (VINF)? 
            # Command -- ':INFUsion:VINF?'
            return_text = self.get_infusion_vinf()
            # print(':infu:vinf? == {0} mL'.format(return_text))
        elif re.match(r'(:)(infu(sion)?)(:)(vtbi)(\?)', cmd.lower()):
            # Query Infusion Volume To Be Infused (VTBI)? 
            # Command -- ':INFUsion:VTBI?'
            return_text = self.get_infusion_vtbi()
            # print(':infu:vtbi? == {0} mL'.format(return_text))
        elif re.match(r'(:)(infu(sion)?)(:)(bol(us)?)(:)(run(ning)?)(\?)', cmd.lower()):
            # Query Is BOLUS Running?
            # Command -- ':INFUsion:BOLus:RUNning?'
            return_text = self.is_bolus_running()
            # print(':infu:bolus:run? == {0}'.format(return_text))
        elif re.match(r'(:)(infu(sion)?)(:)(bol(us)?)(:)(rate)(\?)', cmd.lower()):
            # Query BOLUS Rate?
            # Command -- ':INFUsion:BOLus:RATE?'
            return_text = self.get_bolus_rate()
            # print(':infu:bolus:rate? == {0}'.format(return_text))
        elif re.match(r'(:)(infu(sion)?)(:)(bol(us)?)(:)(vinf)(\?)', cmd.lower()):
            # Query BOLUS Volume Infused (VINF)? 
            # Command -- ':INFUsion:BOLus:VINF?'
            return_text = self.get_bolus_vinf()
            # print(':infu:bolus:vinf? == {0} mL'.format(return_text))
        elif re.match(r'(:)(infu(sion)?)(:)(bol(us)?)(:)(vtbi)(\?)', cmd.lower()):
            # Query BOLUS Volume To Be Infused (VTBI)? 
            # Command -- ':INFUsion:BOLus:VTBI?'
            return_text = self.get_bolus_vtbi()
            # print(':infu:bolus:vtbi? == {0} mL'.format(return_text))
        elif re.match(r'(:)(prot(ocol)?)(:)(rate)(:)(unit)(\?)', cmd.lower()):
            # Query Protocol Rate Unit? 
            # Command -- ':PROTocol:RATE:UNIT?'
            return_text = self.get_protocol_rate_unit()
            # print(':prot:rate:unit? == {0}'.format(return_text))
        elif re.match(r'(:)(prot(ocol)?)(:)(vtbi)(\?)', cmd.lower()):
            # Query Protocol Volume To Be Infused (VTBI)? 
            # Command -- ':PROTocol:VTBI?'
            return_text = self.get_protocol_vtbi()
            # print(':prot:vtbi? == {0:.2f}'.format(return_text))
        elif re.match(r'(:)(prot(ocol)?)(:)(time)(\?)', cmd.lower()):
            # Query Protocol Time in Seconds? 
            # Command -- ':PROTocol:TIME?'
            return_text = self.get_protocol_time()
            print(':prot:time? == {0} sec'.format(return_text))
        elif re.match(r'(:)(prot(ocol)?)(:)(time)(:)(unit)(\?)', cmd.lower()):
            # Query Protocol Time Unit? 
            # Command -- ':PROTocol:TIME:UNIT?'
            return_text = self.get_protocol_time_unit()
            # print(':prot:time:unit? == {0}'.format(return_text))
        elif re.match(r'(:)(prot(ocol)?)(:)(bol(us)?)(:)(rate)(\?)', cmd.lower()):
            # Query Protocol BOLUS Rate?
            # Command -- ':PROTocol:BOLus:RATE?'
            return_text = self.get_protocol_bolus_rate()
            # print(':prot:bolus:rate? == {0}'.format(return_text))
        elif re.match(r'(:)(prot(ocol)?)(:)(auto)(:)(bol(us)?)(:)(vtbi)(\?)', cmd.lower()):
            # Query Protocol Auto BOLUS Volume To Be Infused (VTBI)? 
            # Command -- ':PROTocol:AUTO:BOLus:VTBI?'
            return_text = self.get_protocol_auto_bolus_vtbi()
            if type(return_text) == float:
                print(':prot:auto:bolus:vtbi? == {0:.2f}'.format(return_text))
            else:
                print(':prot:auto:bolus:vtbi? == {0}'.format(return_text))
        elif re.match(r'(:)(prot(ocol)?)(:)(dem(and)?)(:)(bol(us)?)(:)(vtbi)(\?)', cmd.lower()):
            # Query Protocol Demand BOLUS Volume To Be Infused (VTBI)? 
            # Command -- ':PROTocol:DEMand:BOLus:VTBI?'
            return_text = self.get_protocol_demand_bolus_vtbi()
            if type(return_text) == float:
                print(':prot:demand:bolus:vtbi? == {0:.2f}'.format(return_text))
            else:
                print(':prot:demand:bolus:vtbi? == {0}'.format(return_text))
        elif re.match(r'(:)(power)', cmd.lower()):
            # Send [POWER] key command
            return_status = self.trigger_power_off()
            if return_status:
                print('key: On/Off (long)')
        elif re.match(re_query_event_timestamp, cmd.lower()):
            # Query time stamp of certain event in the event log
            # Command -- ':TIMEstamp:{event_type}?'
            re_match_result = re.match(re_query_event_timestamp, cmd.lower())
            event_type = re_match_result[5]
            event_type = event_type.upper()
            print('search for [{}]'.format(event_type))
            event_log_hex = self.search_event(event_type)
            time_stamp_int = None
            if len(event_log_hex) == 32:
                time_stamp_int = get_time_stamp(event_log_hex)
            # print()
            # print(time_stamp_int)            
            return_text = time_stamp_int
        elif re.match(re_search_for_event, cmd.lower()):
            # Search for certain event in the event log
            # Command -- ':EVENTlog:{event_type}?'
            re_match_result = re.match(re_search_for_event, cmd.lower())
            event_type = re_match_result[5]
            event_type = event_type.upper()
            print('Search for [{}]'.format(event_type))
            event_log_hex = self.search_event(event_type)
            event_log = {}
            if len(event_log_hex) == 32:
                event_log = parse_event_log(event_log_hex, self.pump_time_offset)
            elif len(event_log_hex) == 16 * 32:
                event_log = parse_infusion_data_log(event_log_hex)
            elif len(event_log_hex) == 2 * 32:
                event_log = parse_infusion_data_log(event_log_hex)
            # print()
            # print('{0} == {1}'.format(cmd, event_log_json))
            return_text = event_log
        elif re.match(re_query_event_list, cmd.lower()):
            # Query Event Log List
            # Command -- ':EVENTlog:{number_to_query}?'
            re_match_result = re.match(re_query_event_list, cmd.lower())
            num_to_query = int(re_match_result[5])
            return_text = self.get_eventlog_list(num_to_query)
            print(':event:{0}? == {1}'.format(num_to_query, return_text))
        elif re.match(re_get_key_list, cmd.lower()):
            # Get key press list from the pump 
            # Command -- ':KEY:LIST?'
            re_match_result = re.match(re_get_key_list, cmd.lower())
            sent_text = ':KEY:LIST?'
            return_text = self.query(sent_text)
            raw_key_lsit = []
            for i in range(int(len(return_text) / 2)):
                raw_key_lsit.append(return_text[2 * i:2 * i + 2])
            print('len = {}'.format(len(raw_key_lsit)))
            print('{}'.format(raw_key_lsit))
            key_list = parse_key_list(return_text)
            return_text = key_list
            print('{0} == {1}'.format(cmd.upper(), return_text))
        elif re.match(re_scpi_get_cmd, cmd.lower()):
            # SCPI get commands, such as:
            # :protocol:rate?
            # :key:list?
            return_text = self.query(cmd.upper())
            # print('type(return_text) == {}'.format(type(return_text)))
            # print('len(return_text) == {}'.format(len(return_text)))
            if return_text.isdigit() and not re.match(r':screen(shot)?:line:[0-8]\?', cmd.lower()):
                # Check for Integer
                return_text = int(return_text)            
            elif isfloat(return_text) and not re.match(r':screen(shot)?:line:[0-8]\?', cmd.lower()):
                # Check for Float
                return_text = float(return_text)
            elif return_text == 'TRUE':
                # Check for True
                return_text = True
            elif return_text == 'FALSE':
                # Check for False
                return_text = False
        elif re.match(re_scpi_set_cmd, cmd.lower()):
            # SCPI set commands, such as:
            # :protocol:rate 20.0
            # :key:list:clear
            return_text = self.query(cmd.upper())
            print(cmd.upper())
        return return_text

    def press_key(self, key_type, key_duration):
        '''Simulate [key_type] key [duration] press'''        
        key_command = "KE" + key_type + key_duration
        print('{0:6s} : {1}'.format('sent', key_command))
        return_text = self.query(key_command)
        # print('{0:6s} : {1}'.format('return', return_text))
        # if len(return_text) == 4 and return_text[0:2] == 'KE':
            # print('[KE] command succeed')
        # else:
            # print('[KE] command failed!')
        return return_text

    def send_rx_initialize(self, rx):
        '''Send Rx Initialization [LI] command'''
        result = True
        error_code = ''

        # get pump serial number (8-digit ASCII string) Ex.: SN800008
        pump_sn = rx.get_pump_sn().zfill(8)
        print('{0:11s} = {1}'.format('pump sn', pump_sn))
        # convert ASCII string to Hex string (16-digit Hex string) Ex.: 534E383030303038
        pump_sn_hex = binascii.hexlify(pump_sn.encode()).decode()
        print('{0:11s} = {1}'.format('pump sn hex', pump_sn_hex))
        # library CRC (8-digit Hex string) Ex.: 6B6B8B66
        library_crc = rx.get_library_crc().zfill(8)
        print('{0:11s} = {1}'.format('lib crc', library_crc))
        # library number (integer) Ex.: 318
        library_number = rx.get_library_number()
        print('{0:11s} = {1}'.format('lib num', library_number))
        # convert integer to hex string (8 digit hex string) Ex.: 0000013E
        library_number_hex = hex(library_number)[2:].zfill(8)
        print('{0:11s} = {1}'.format('lib num hex', library_number_hex))
        # build [LI] command Ex.: LI534E3830303030386B6B8B660000013E
        li_command = 'LI' + pump_sn_hex + library_crc + library_number_hex
        print("{0:6s} : {1}".format('sent', li_command))
        return_text = self.query(li_command)
        print('{0:6s} : {1}'.format('return', return_text))
        # print(len(return_text))
        if len(return_text) == 3 and return_text[0:2] == 'LI':
            error_code = return_text[2:3]
        if error_code != '0':
            print('[LI] command error: {}'.format(error_code))
            result = False
        else:
            print('[LI] command succeed')
        return result
    
    def input_digits(self, digits_str):
        '''Input Number (on the pump)'''
        # print('Input Digits [{}]...'.format(digits_str))
        # time.sleep(_TIMEOUT * 2)
        # Input Digits
        for index in range(len(digits_str)):
            digit = int(digits_str[index])
            if digit > 5:
                while digit < 10:
                    self.press_key(_DOWN_KEY, _SHORT_PRESS)
                    print('key: Down (short)')
                    time.sleep(_TIMEOUT * 2)
                    digit += 1
            else: 
                while digit > 0:
                    self.press_key(_UP_KEY, _SHORT_PRESS)
                    print('key: Up (short)')
                    time.sleep(_TIMEOUT * 2)
                    digit -= 1
            self.press_key(_OK_KEY, _SHORT_PRESS)
            print('key: Ok (short)')
            time.sleep(_TIMEOUT * 2)

    def read_pump_time(self):
        '''Read Pump Time'''
        pump_time = ''
        return_text = self.query('RC')
        # print(return_text)
        # print(len(return_text))
        if len(return_text) == 14 and return_text[0:2] == 'RC':
            # Normal time stamp, need to be interpreted
            pump_time = return_text[2:14]
        elif len(return_text) == 10 and return_text[0:2] == 'RC':
            # Relative time since firmware download (4-byte integer represented in 8-byte Hex)
            pump_time = return_text[2:10]
            # [pump_time] is in format 'F0 00 00 00', So the first 'F' need to be removed.
            self.pump_time_offset = int('0' + pump_time[1:], 16)
        return pump_time
        
    def get_occlusion_sensor(self):
        '''Read Pump Occlusion Sensor Values'''
        occlusion_sensor = {}
        return_text = self.query('RD')
        # print(return_text)
        # print(len(return_text))
        if len(return_text) == 10 and return_text[0:2] == 'RD':
            up_stream = int(return_text[2:6], 16)
            down_stream = int(return_text[6:10], 16)
            occlusion_sensor['up'] = up_stream
            occlusion_sensor['down'] = down_stream
        return occlusion_sensor
    
    def get_all_sensor(self):
        '''Read Pump Motor Sensor Values'''
        sensor = {}
        return_text = self.read()
        print(return_text)
        # print(len(return_text))
        return_text = re.match(r'.*((S9)([A-F0-9]{9}))', return_text)
        if return_text is not None:
            return_text = return_text[1]
        else:
            return_text = ''
        if len(return_text) == 11 and return_text[0:2] == 'S9':
            hall_effect_sensor = int(bin(int(return_text[2], 16) & 0x8)[2]) 
            motor_running = int(bin(int(return_text[2], 16) & 0x4)[2])
            up_stream = int(return_text[2:5], 16) & 0x3FF
            down_stream = int(return_text[6:8], 16)
            battery_voltage = int(return_text[8:11], 16) / 100
            sensor['up'] = up_stream
            sensor['down'] = down_stream
            sensor['system'] = hall_effect_sensor
            sensor['motor_running'] = motor_running
            sensor['battery_voltage'] = battery_voltage
        return sensor
    
    def write_pump_time(self, time_stamp=None):
        '''Write Pump Time
        input: 
            time_stamp - [YYYY-MM-DD hh:mm:ss]
        output:
            status - [True | False]
            
        '''
        status = False
        if time_stamp == None:
            current_datetime = datetime.datetime.now()
            day = hex(current_datetime.day)[2:].zfill(2)
            month = hex(current_datetime.month)[2:].zfill(2)
            year = hex(current_datetime.year - 2000)[2:].zfill(2)
            hour = hex(current_datetime.hour)[2:].zfill(2)
            minute = hex(current_datetime.minute)[2:].zfill(2)
            second = hex(current_datetime.second)[2:].zfill(2)
            wc_command = 'WC' + day + month + year + hour + minute + second
            return_text = self.query(wc_command)
            # print(return_text)
            # print(len(return_text))
            status = (len(return_text) == 2 and return_text[0:2] == 'WC')
        else:
            day = hex(int(time_stamp[8:10]))[2:].zfill(2)
            month = hex(int(time_stamp[5:7]))[2:].zfill(2)
            year = hex(int(time_stamp[:4]) - 2000)[2:].zfill(2)
            hour = hex(int(time_stamp[11:13]))[2:].zfill(2)
            minute = hex(int(time_stamp[14:16]))[2:].zfill(2)
            second = hex(int(time_stamp[17:19]))[2:].zfill(2)
            wc_command = 'WC' + day + month + year + hour + minute + second
            return_text = self.query(wc_command)
            # print(return_text)
            # print(len(return_text))
            status = (len(return_text) == 2 and return_text[0:2] == 'WC')
        return status

    def reset_pump(self):
        '''Reset Pump Service Total VINF and Total Infusion Time
            need to restart the pump and verify from the info menu
        '''
        return_text = self.query('WR')
        # print(return_text)
        # print(len(return_text))
        status = (len(return_text) == 2 and return_text[0:2] == 'WR')
        return status

    def read_platform(self):
        '''read pump platform ('H' or 'K')'''
        platform = 'C'
        return_text = self.query('RM')
        if len(return_text) == 4 and return_text[0:2] == 'RM':
            if return_text[2:] == '00':
                platform = 'H'
            elif return_text[2:] == '01':
                platform = 'K'
        return platform

    def write_platform(self, platform):
        '''write pump platform'''
        status = True
        platform = platform.upper().strip(' \t\r\n\0')
        if platform in ['H', 'K']:
            if platform == 'H':
                sent_text = 'WM00'
            else:
                sent_text = 'WM01'
            return_text = self.query(sent_text)
            if len(return_text) == 4 and return_text[0:2] == 'WM':
                print('Pump platform is set to: {0} ({1})'.format(platform, return_text[2:4]))
        else:
            status = False
            print('Abort: unkown platform: {}'.format(platform))
        return status

    #===================

    def get_infusion_mode(self):
        infusion_mode = ''
        return_text = self.query('Q0')
        if return_text[0:2] == 'Q0':
            infusion_mode = return_text[2:]
        return infusion_mode
    
    # def is_infusion_running(self):
    #     is_infusion_running = False
    #     return_text = self.query('Q1')
    #     if return_text[0:2] == 'Q1':
    #         if return_text[2:] == '1':
    #             is_infusion_running = True
    #     return is_infusion_running

    # def get_infusion_rate(self):
    #     infusion_rate = -1
    #     return_text = self.query('Q2')
    #     if return_text[0:2] == 'Q2':
    #         infusion_rate = int(return_text[2:], 16) / 100
    #     return infusion_rate

    def get_infusion_time(self):
        infusion_time = -1
        return_text = self.query('Q3')
        if return_text[0:2] == 'Q3':
            # print(return_text)
            infusion_time = int(return_text[2:], 16)
        return infusion_time
    
    def get_infusion_rate_unit(self):
        infusion_rate_unit = ''
        return_text = self.query('Q4')
        if return_text[0:2] == 'Q4':
            # print(return_text)
            infusion_rate_unit = return_text[2:]
        return infusion_rate_unit
    
    def get_infusion_vinf(self):
        infusion_vinf = -1
        return_text = self.query('Q5')
        if return_text[0:2] == 'Q5':
            infusion_vinf = int(return_text[2:], 16) / 100
        return infusion_vinf

    def get_infusion_vtbi(self):
        infusion_vtbi = -1
        return_text = self.query('Q6')
        if return_text[0:2] == 'Q6':
            infusion_vtbi = int(return_text[2:], 16) / 100
        return infusion_vtbi

    def is_bolus_running(self):
        is_bolus_running = False
        return_text = self.query('Q7')
        if return_text[0:2] == 'Q7':
            if return_text[2:] == '1':
                is_bolus_running = True
        return is_bolus_running
    
    def get_bolus_rate(self):
        bolus_rate = -1
        return_text = self.query('Q8')
        if return_text[0:2] == 'Q8':
            bolus_rate = int(return_text[2:], 16) / 100
        return bolus_rate
    
    def get_bolus_vinf(self):
        bolus_vinf = -1
        return_text = self.query('Q9')
        if return_text[0:2] == 'Q9':
            bolus_vinf = int(return_text[2:], 16) / 100
        return bolus_vinf
    
    def get_bolus_vtbi(self):
        bolus_vtbi = -1
        return_text = self.query('QA')
        if return_text[0:2] == 'QA':
            bolus_vtbi = int(return_text[2:], 16) / 100
        return bolus_vtbi
    
    # def get_protocol_rate(self):
    #     protocol_rate = -1
    #     return_text = self.query('QB')
    #     if return_text[0:2] == 'QB':
    #         protocol_rate = int(return_text[2:], 16) / 100
    #     return protocol_rate
    
    def get_protocol_rate_unit(self):
        protocol_rate_unit = ''
        return_text = self.query('QC')
        if return_text[0:2] == 'QC':
            # print(return_text)
            protocol_rate_unit = return_text[2:]
        return protocol_rate_unit
    
    def get_protocol_vtbi(self):
        protocol_vtbi = ''
        return_text = self.query('QD')
        if return_text[0:2] == 'QD':
            # print(return_text)
            protocol_vtbi = int(return_text[2:], 16) / 100
        return protocol_vtbi
    
    def get_protocol_time(self):
        protocol_time = ''
        return_text = self.query('QE')
        if return_text[0:2] == 'QE':
            # print(return_text)
            protocol_time = int(return_text[2:], 16)
        return protocol_time
    
    def get_protocol_time_unit(self):
        protocol_time_unit = ''
        return_text = self.query('QF')
        if return_text[0:2] == 'QF':
            # print(return_text)
            protocol_time_unit = return_text[2:]
        return protocol_time_unit
    
    def get_protocol_bolus_rate(self):
        protocol_bolus_rate = -1
        return_text = self.query('QG')
        if return_text[0:2] == 'QG':
            # print(return_text)
            protocol_bolus_rate = int(return_text[2:], 16) / 100
        return protocol_bolus_rate
    
    def get_protocol_auto_bolus_vtbi(self):
        protocol_auto_bolus_vtbi = ''
        return_text = self.query('QH')
        if return_text[0:2] == 'QH' and return_text[2:] != 'ERROR':
            # print(return_text)
            protocol_auto_bolus_vtbi = int(return_text[2:], 16) / 100
        else:
            print(return_text)
        return protocol_auto_bolus_vtbi
    
    def get_protocol_demand_bolus_vtbi(self):
        protocol_demand_bolus_vtbi = ''
        return_text = self.query('QI')
        if return_text[0:2] == 'QI' and return_text[2:] != 'ERROR':
            # print(return_text)
            protocol_demand_bolus_vtbi = int(return_text[2:], 16) / 100
        else:
            print(return_text)
        return protocol_demand_bolus_vtbi

    def get_eventlog_list(self, num_to_query):
        eventlog_list = []
        eventlogs = self.read_multiple_event_log(num_to_query)
        for each_eventlog in eventlogs:
            if 'event_type' in each_eventlog:
                eventlog_list.append(each_eventlog['event_type'])
                if each_eventlog['event_type'] == 'INFUSION_DATA':
                    eventlog_list.append(each_eventlog['infusion_data_frame'])
                elif each_eventlog['event_type'] == 'OCCLUSION':
                    eventlog_list.append(each_eventlog['occlusion type'])
        return eventlog_list
    
    def get_screenshot_hex_list(self):
        screenshot_ready = False
        while not screenshot_ready:
            screenshot_ready = self.send_command(':screenshot:ready?')
            print('screenshot_ready = {}'.format(screenshot_ready))
        screenshot_hex_list = []
        for i in range(8):
            sent_text = ':screenshot:line:' + str(i) + '?'
            return_text = self.send_command(sent_text)
            print(return_text)
            screenshot_hex_list.append(return_text)
        return screenshot_hex_list

    #===================
    def trigger_power_off(self):
        '''trigger power off'''
        status = False
        sent_text = 'WT00'
        return_text = self.query(sent_text)
        if len(return_text) == 2 and return_text[0:2] == 'WT':
            # print('Trigger Power Off')
            status = True
        return status
    
    def trigger_run_infusion(self):
        '''trigger run infusion'''
        status = False
        sent_text = 'WT01'
        return_text = self.query(sent_text)
        if len(return_text) == 2 and return_text[0:2] == 'WT':
            # print('Trigger Run Infusion succeed')
            status = True
        return status
    
    def trigger_stop_infusion(self):
        '''trigger stop infusion'''
        status = False
        sent_text = 'WT02'
        return_text = self.query(sent_text)
        if len(return_text) == 2 and return_text[0:2] == 'WT':
            # print('Trigger Stop Infusion succeed')
            status = True
        return status
    
    def start(self):
        '''start console'''
        try:
            #
            cmd = ''
            while cmd not in ['exit', 'quit']:
                cmd = input('>')
                # #
                # # Pause [Event Log Monitor]
                # if self.event_log_monitor.is_on():
                    # if not self.event_log_monitor.is_paused():
                        # self.event_log_monitor.pause()
                #
                # # Disable [Infusion Monitor] Output
                # self.infusion_monitor.diable_output()
                        
                #
                if cmd.upper().rstrip(' \t\r\n\0') in ['HELP', '?']:
                    print(' RE - Read Event Log')
                    print(' RI - Read Event Log Tail and Head Indexes (sequence: tail -> head)')
                    print(' RN - Read Pump Serial Number')
                    print(' WN - Write Pump Serial Number')
                    print(' R1 - Read Motor Calibration Factor')
                    print(' R2 - Read Thresholds of Upstream and Downstream Occlusion Sensor')
                    print(' W2 - Write Thresholds of Upstream and Downstream Occlusion Sensor')
                    print(' R3 - Read Pump Product Total Volume Infused (Integer) ')
                    print(' R7 - Read Battery Voltage')
                    print(' R8 - Read Pump Product Total Volume Infused (Float)')
                    print(' R9 - Read Pump Product Total ON Time')
                    print(' RA - Read Battery Calibration and Voltage')
                    print(' RB - Read Base Year')
                    print(' RC - Read Clock')
                    print(' RD - Read Upstream and Downstream Occlusion Sensor')
                    print(' RL - Read Library Name and Version')
                    print(' RS - Read Firmware Version')
                    print(' WC - Write Clock')
                    print(' WK - Write AES Encryption Key')
                    print(' RM - Read Platform (H and K pump only)')
                    print(' WM - Write Platform (H and K pump only)')
                    print(' WR - Reset Pump Service Total Volume Infused and Total ON Time')
                    print(' GR - Generate Rx')
                    print(' SR - Send Rx')
                    print(' SL - Send Library')
                    print(' EL - Encrypt Library JSON To Byte Array')
                    print(' ER - Encrypt Rx JSON To Byte Array')
                    print(' SC - Send Generic Command')
                    print('----')
                    print(' Key Commands:')
                    print(' info - Long Press [INFO] Key')
                    print(' back - Short Press [INFO] Key')
                    print(' run - Short Press [RUN/STOP] Key')
                    print(' stop - Long Press [RUN/STOP] Key')
                    print(' ok - Short Press [OK] Key')
                    print(' enter - Short Press [OK] Key')
                    print(' up - Short Press [UP] Key')
                    print(' down - Short Press [DOWN] Key')
                    print(' power off - Long press [ON/OFF] Key')
                    print(' bolus - Short press [BOLUS] Key')
                    print('----')
                    print(' start elm - Start Event Log Monitor')
                    print(' stop elm - Stop Event Log Monitor')
                    print(' status elm - Check Event Log Monitor Status')
                    print(' pin - Input PIN number')
                    print('----')
                    
                elif cmd.upper().rstrip(' \t\r\n\0') in ['VERSION', 'ABOUT']:
                    copyright_symbol = u"\u00A9"
                    print('\t Nimbus MIVA Pump Configuration Tool')
                    print('\t Copyright {} 2020-2021'.format(copyright_symbol))
                    print('\t Zyno Medical LLC')
                    print('\t Ver 1.0.1')
                    print('\t Author: yancen.li@zynomed.com')
                # elif re.match('(re)(\s+)?(>)?(\s+)?([a-z0-9_]+\.txt)?', \
                #         cmd.lower().rstrip(' \t\r\n\0')):
                #     # Read whole event log
                #     re_result = re.match('(re)(\s+)?(>)?(\s+)?([a-z0-9_]+\.txt)?', \
                #                     cmd.lower().rstrip(' \t\r\n\0'))
                #     entire_event_log = self.read_entire_event_log()
                #     entire_event_log_json = json.dumps(entire_event_log, indent=4)
                #     print('     Event logs read: [{}]'.format(len(entire_event_log)))
                #     event_log_path = None
                #     # print('re_result[5] = {}'.format(re_result[5]))
                #     # print('re_result[7] = {}'.format(re_result[7]))
                #     if re_result[3] != None and re_result[5] != None:
                #         event_log_path = re_result[5]
                #         # Save to json file
                #         file = open(event_log_path, "w")
                #         file.write(entire_event_log_json)
                #         file.close()
                #         print('     Event logs saved: [{}]'.format(event_log_path))
                # Read the last N event log
                elif re.match('(re)(\s+)?(\d+)(\s+)?(>)?(\s+)?([a-z0-9_]+\.txt)?', \
                        cmd.lower().rstrip(' \t\r\n\0')):
                    re_result = re.match('(re)(\s+)?(\d+)?(\s+)?(>)?(\s+)?([a-z0-9_]+\.txt)?', \
                                    cmd.lower().rstrip(' \t\r\n\0'))
                    # the number of event log to print
                    num_to_print = 0
                    if re_result[3] == None:
                        num_to_print = -1
                    else:
                        num_to_print = int(re_result[3])
                    # the path the event log will be saved to
                    event_log_path = None
                    # print('re_result[5] = {}'.format(re_result[5]))
                    # print('re_result[7] = {}'.format(re_result[7]))
                    if re_result[5] != None and re_result[7] != None:
                        event_log_path = re_result[7]
                    #
                    event_logs = self.read_multiple_event_log(num_to_print)
                    event_logs_json = json.dumps(event_logs, indent=4)
                    print(event_logs_json)
                    print('     Event logs read: [{}]'.format(len(event_logs)))
                    # Save to json file
                    if event_log_path is not None:
                        file = open(event_log_path, "w")
                        file.write(event_logs_json)
                        file.close()
                        print('     Event logs saved: [{}]'.format(event_log_path))
                # Read Event Log Indices
                elif cmd.upper().rstrip(' \t\r\n\0') == 'RI':
                    event_log_index = self.read_event_log_indices()
                    event_log_index_tail = event_log_index['tail']
                    event_log_index_head = event_log_index['head']
                    if event_log_index_tail != '' and event_log_index_head != '':
                        print('Event log tail = {}'.format(event_log_index_tail))
                        print('Event log head = {}'.format(event_log_index_head))
                    else:
                        print('Error: get event log index failed')
                # Read Pump Serial Number
                elif cmd.upper().rstrip(' \t\r\n\0') == 'RN':
                    serial_number = self.get_pump_sn()
                    if serial_number != '':
                        print('S/N: {}'.format(serial_number))
                    else:
                        print('Error: get serial number failed')
                # Write Pump Serial Number
                elif cmd.upper().rstrip(' \t\r\n\0') == 'WN':
                    print('Enter NEW S/N: ', end='')
                    serial_number = input('').upper()
                    if len(serial_number) == 8 and re.findall(r"SN[0-9]{6,6}", serial_number) != []:
                        status = self.set_pump_sn(serial_number)
                        if status:
                            # print('New S/N: {}'.format(serial_number))
                            print("Write pump serial number  -  Done!")
                        else:
                            print('Error: set serial number failed')
                    else:
                        print('Error: invalid serial number \'{}\' '.format(serial_number), end='')
                        print('Enter \'SN\' followed by 6-digit pump serial number ', end='')
                        print('(ex: \'SN800009\')')
                # Read Motor Calibration Factor
                elif cmd.upper().rstrip(' \t\r\n\0') == 'R1':
                    motor_calibration_factor = self.get_motor_calibration_factor()
                    if motor_calibration_factor != None:
                        print('Motor calibration factor: {}'.format(motor_calibration_factor))
                    else:
                        print('Error: get [motor calibration factor] failed')
                # Read Occlusion Sensor Value
                elif cmd.upper().rstrip(' \t\r\n\0') == 'R2':
                    occlusion_thresholds = self.get_occlusion_thresholds()
                    if occlusion_thresholds != {}:
                        print('Up threshold: {}'.format(occlusion_thresholds['up']))
                        print('Dn threshold: {}'.format(occlusion_thresholds['down']))
                    else:
                        print('Error: get [occlusion thresholds] failed')
                # Write Occlusion Sensor Value
                elif cmd.upper().rstrip(' \t\r\n\0') == 'W2':
                    occlusion_thresholds = self.set_occlusion_thresholds()
                    if occlusion_thresholds != {}:
                        print('Up threshold is set to: {}'.format(occlusion_thresholds['up']))
                        print('Dn threshold is set to: {}'.format(occlusion_thresholds['down']))
                    else:
                        print('Error: set [occlusion thresholds] failed')
                # Read [Total Volume Infused]
                elif cmd.upper().rstrip(' \t\r\n\0') == 'R3':
                    total_volume_infused = self.get_total_volume_infused()
                    if total_volume_infused != None:
                        print('Total volume infused: {} mL'.format(total_volume_infused))
                    else:
                        print('Error: get [Total Volume Infused] failed')

                # Read Battery Voltage
                elif cmd.upper().rstrip(' \t\r\n\0') == 'R7':
                    battery_voltage = self.get_battery_voltage()
                    if battery_voltage != None:
                        print('Battery voltage: {:.2f} V'.format(battery_voltage))
                    else:
                        print('Error: get [Battery Voltage] failed')
                        
                # Read Motor Calibration Factor and Total Rotation
                elif cmd.upper().rstrip(' \t\r\n\0') == 'R8':
                    
                    product_life_volume = self.get_product_life_volume()
                    if product_life_volume != {}:
                        print('Motor calibration factor: {}'.format(product_life_volume['calibration']))
                        print('Motor total rotation: {}'.format(product_life_volume['rotation']))
                        print('Product life volume: {:.2f} mL'.format(product_life_volume['volume']))
                    else:
                        print('Error: get [Calibration Factor and Total Rotation] failed')
                # Read Total Pump ON Time
                elif cmd.upper().rstrip(' \t\r\n\0') == 'R9':
                    total_pump_on_time = self.get_total_pump_on_time()
                    if total_pump_on_time != '':
                        day = str(int(total_pump_on_time / 3600 / 24)).zfill(2)
                        hour = str(int(total_pump_on_time / 3600 % 24)).zfill(2)
                        minute = str(int(total_pump_on_time % 3600 / 60)).zfill(2)
                        second = str(int(total_pump_on_time % 3600 % 60)).zfill(2)
                        print('{0} day {1} hr {2} min {3} sec'.format(day, hour, minute, second))
                        print("Read pump total ON time - Done!")
                    else:
                        print('Error: get [Battery Voltage] failed')
                elif cmd.upper().rstrip(' \t\r\n\0') == 'RA':
                    # Read Battery Calibration
                    battery_calibration_and_voltage = self.get_battery_calibration_and_voltage()
                    if battery_calibration_and_voltage != {}:
                        print('Battery calibration factor = {}'\
                                .format(battery_calibration_and_voltage['calibration']))
                        print('Battery voltage = {:.2f} V'\
                                .format(battery_calibration_and_voltage['voltage']))
                    else:
                        print('Error: get [Battery Voltage] failed')
                elif cmd.upper().rstrip(' \t\r\n\0') == 'WA':
                    # Write Battery Calibration Factor
                    calib_factor = input('Enter Battery Calibration Factor: ')
                    if re.match(r'^\d+(.)?(\d+)?$', calib_factor) is None:
                        print('Error: invalid battery calibration factor \'{}\' '.format(calib_factor))
                    else:
                        calib_factor = float(calib_factor)
                        if calib_factor >= 0.9 and calib_factor <= 1.1:
                            status = self.set_battery_calib(calib_factor)
                            if status:
                                print("Set battery calibration factor  -  Done!")
                            else:
                                print('Error: set battery calibration factor failed')
                        else:
                            print('Error: \'{}\' out of range [0.900, 1.100]'.format(calib_factor))
                # Read Base Year
                elif cmd.upper().rstrip(' \t\r\n\0') == 'RB':
                    base_year = self.get_base_year()
                    if base_year != '':
                        print('Base year = {}'.format(base_year))
                    else:
                        print('Error: get [Base Year] failed')
                # Read Up Down Stream Occlusion Sensor
                elif cmd.upper().rstrip(' \t\r\n\0') == 'RD':
                    occlusion_sensor = self.get_occlusion_sensor()
                    if occlusion_sensor != '':
                        print('Read occlusion sensor...')
                        print('Up stream = {}'.format(occlusion_sensor['up']))
                        print('Dn stream = {}'.format(occlusion_sensor['down']))
                    else:
                        print('Error: get [Occlusion Sensor] failed')
                # Read Library Name and Version
                elif cmd.upper().rstrip(' \t\r\n\0') == 'RL':
                    library_name_version = self.get_library_name_version()
                    if library_name_version != '':
                        print('Library name: [{}]'.format(library_name_version['name']))
                        print('Library version: [{}]'.format(library_name_version['version']))
                    else:
                        print('Error: get [Library Version] failed')
                # Read Firmware Version
                elif cmd.upper().rstrip(' \t\r\n\0') == 'RS':
                    software_version = self.get_software_version()
                    if software_version != '':
                        print('Firmware version: [{}]'.format(software_version))
                    else:
                        print('Error: get [Software Version] failed')
                elif cmd.upper().rstrip(' \t\r\n\0') == 'INFO':
                    # Send [INFO] key command
                    return_text = self.press_key(_INFO_KEY, _LONG_PRESS)
                    if len(return_text) == 4 and return_text[0:2] == 'KE':
                        print('key: Info (long)')
                elif cmd.upper().rstrip(' \t\r\n\0') == 'BACK':
                    # Send [BACK] key command
                    return_text = self.press_key(_INFO_KEY, _SHORT_PRESS)
                    if len(return_text) == 4 and return_text[0:2] == 'KE':
                        print('key: back (short)')
                elif cmd.upper().rstrip(' \t\r\n\0') in ['RUN', 'START']:
                    # Send [RUN] key command [SHORT]
                    return_text = self.press_key(_RUN_KEY, _MID_PRESS)
                    if len(return_text) == 4 and return_text[0:2] == 'KE':
                        print('key: Run/Stop (short)')
                elif cmd.upper().rstrip(' \t\r\n\0') == 'STOP':
                    # Send [STOP] key command [LONG]
                    return_text = self.press_key(_RUN_KEY, _MID_PRESS)
                    if len(return_text) == 4 and return_text[0:2] == 'KE':
                        print('key: Run/Stop (long)')
                elif cmd.upper().rstrip(' \t\r\n\0') in ['OK', 'ENTER']:
                    # Send [OK] key command
                    return_text = self.press_key(_OK_KEY, _SHORT_PRESS)
                    if len(return_text) == 4 and return_text[0:2] == 'KE':
                        print('key: Ok/Enter (short)')
                elif cmd.upper().rstrip(' \t\r\n\0') == 'UP':
                    # Send [UP] key command
                    return_text = self.press_key(_UP_KEY, _SHORT_PRESS)
                    if len(return_text) == 4 and return_text[0:2] == 'KE':
                        print('key: Up (short)')
                elif cmd.upper().rstrip(' \t\r\n\0') == 'DOWN':
                    # Send [DOWN] key command
                    return_text = self.press_key(_DOWN_KEY, _SHORT_PRESS)
                    if len(return_text) == 4 and return_text[0:2] == 'KE':
                        print('key: Down (short)')
                elif cmd.upper().rstrip(' \t\r\n\0') in \
                        ['POWER OFF', 'POWEROFF', 'SHUT DOWN', 'SHUTDOWN', \
                            'SHUT OFF', 'SHUTOFF', 'POWER']:
                    # Send [POWER] key command
                    return_text = self.press_key(_POWER_KEY, _LONG_PRESS)
                    if len(return_text) == 4 and return_text[0:2] == 'KE':
                        print('key: On/Off (long)')
                elif cmd.upper().rstrip(' \t\r\n\0') == 'BOLUS':
                    # Send [BOLUS] key command
                    return_text = self.press_key(_BOLUS_KEY, _SHORT_PRESS)
                    if len(return_text) == 4 and return_text[0:2] == 'KE':
                        print('key: Bolus (short)')
                elif cmd.lower().rstrip(' \t\r\n\0') in ['rc', 'read clock']:
                    # Read Pump Time
                    pump_time = self.read_pump_time()
                    if pump_time != '':
                        # print(pump_time)
                        day = str(int(pump_time[0:2], 16)).zfill(2)
                        month = str(int(pump_time[2:4], 16)).zfill(2)
                        year = str(int(pump_time[4:6], 16) + 2000).zfill(2)
                        hour = str(int(pump_time[6:8], 16)).zfill(2)
                        minute = str(int(pump_time[8:10], 16)).zfill(2)
                        second = str(int(pump_time[10:12], 16)).zfill(2)
                        print('{0}-{1}-{2} {3}:{4}:{5}'.format(year, month, day, hour, minute, second))
                        print("Read pump time - Done!")
                    else:
                        print('Error: read pump time failed')
                elif cmd.lower().rstrip(' \t\r\n\0') in ['wc', 'write clock']:
                    # Write Pump Time 
                    status = self.write_pump_time()
                    if status:
                        current_date_time = datetime.datetime.now()
                        current_date = datetime.date(current_date_time.year, current_date_time.month, current_date_time.day)
                        current_time = datetime.time(current_date_time.hour, current_date_time.minute, current_date_time.second)
                        print('{0} {1}'.format(current_date, current_time))
                        print("Write pump time - Done!")
                    else:
                        print('Error: write pump time failed')
                elif cmd.lower().rstrip(' \t\r\n\0') in ['wr', 'reset pump']:
                    # Reset Pump Service Total VINF and Total ON Time 
                    print("Reset pump ...")
                    status = self.reset_pump()
                    if status:
                        print("Reset service total volume infused - Done!")
                        print("Reset service total ON time - Done!")
                    else:
                        print('Error: reset pump failed')
                elif cmd.lower().rstrip(' \t\r\n\0') in ['sc', 'send command']:
                    # Send Generic Command
                    print('Enter command to send: ', end='')
                    sent_text = input('').upper()
                    return_text = self.query(sent_text)
                    print(return_text)
                # Read Platform (H and K pump only)
                elif cmd.lower().rstrip(' \t\r\n\0') in ['rm', 'read platform']:
                    platform = self.read_platform()
                    if platform != '':
                        print('pump platform: [{}]'.format(platform))
                    else:
                        print('Error: read pump platform failed')
                # Write Platform (H and K pump only)
                elif cmd.lower().rstrip(' \t\r\n\0') in ['wm', 'write platform']:
                    print('Enter Pump Platform (H or K): ', end='')
                    platform = input('').upper()
                    status = self.write_platform(platform)
                    if status:
                        print("Write pump platform - Done!")
                    else:
                        print('Error: write pump platform failed')
                else:
                    system(cmd)
                #
                # # Enable [Infusion Monitor] Output
                # self.infusion_monitor.enable_output()
                #
                # # Resume [Event Log Monitor]
                # if self.event_log_monitor.is_on():
                    # if self.event_log_monitor.is_paused():
                        # self.event_log_monitor.resume()
                #
                
            #
            # print('==')
            # print('stop event log monitor...')
            # print('==')
            # self.stop_event_log_monitor()
            #
            print('Stopping Serial Port Connection...')
            self.serial.close()
            print('Serial port stopped at [{}]'.format(time.strftime('%H:%M:%S', time.localtime())))
            print('==')
        except KeyboardInterrupt:
            print()
            print("{0}: {1}\n".format(sys.exc_info()[0], sys.exc_info()[1]))
            #
            # print('==')
            # print('stop event log monitor...')
            # print('==')
            # self.stop_event_log_monitor()
        except serial.serialutil.SerialException:
            print("{0}: {1}\n".format(sys.exc_info()[0], sys.exc_info()[1]))
            #
            # print('==')
            # print('stop event log monitor...')
            # print('==')
            # self.stop_event_log_monitor()
        except (OSError, NameError, PermissionError):
            print("{0}: {1}\n".format(sys.exc_info()[0], sys.exc_info()[1]))
            #
            # print('==')
            # print('stop event log monitor...')
            # print('==')
            # self.stop_event_log_monitor()
        # except (KeyError):
            # print("{0}: {1}\n".format(sys.exc_info()[0], sys.exc_info()[1]))


def main(argv):
    '''main function'''
    try:
        current_file = path.basename(__file__)
        if len(argv) == 1:
            print('Empty argument list. ', end='')
            print('To start, type <{}> followed by the com port. '.format(current_file), end='')
            print('Ex: \'{} COM1\''.format(current_file))
            serial_port_list = scan_serial_ports()
            print('\tAvailable Serial Ports:')
            print('\t\t\t\t', end='')
            for each_serial_port in serial_port_list:
                print('{} '.format(each_serial_port), end='')
        else:
            serial_port = argv[1].upper()
            if re.match('com\d+', serial_port.lower().rstrip(' \t\r\n\0')):
                serial_comm = SerialComm(serial_port)
                serial_comm.start()
            else:
                print('Error: invalid port \'{}\' '.format(serial_port), end='')
                print('To start, type \'{}\' followed by the com port. '\
                        .format(current_file), end='')
                print('Ex: \'{} COM1\''.format(current_file))
    except KeyboardInterrupt:
        pass
    except serial.serialutil.SerialException:
        print("{0}: {1}\n".format(sys.exc_info()[0], sys.exc_info()[1]))


if __name__ == "__main__":
    main(sys.argv)
