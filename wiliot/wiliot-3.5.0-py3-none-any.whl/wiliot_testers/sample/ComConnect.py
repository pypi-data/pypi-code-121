"""
  Copyright (c) 2016- 2021, Wiliot Ltd. All rights reserved.

  Redistribution and use of the Software in source and binary forms, with or without modification,
   are permitted provided that the following conditions are met:

     1. Redistributions of source code must retain the above copyright notice,
     this list of conditions and the following disclaimer.

     2. Redistributions in binary form, except as used in conjunction with
     Wiliot's Pixel in a product or a Software update for such product, must reproduce
     the above copyright notice, this list of conditions and the following disclaimer in
     the documentation and/or other materials provided with the distribution.

     3. Neither the name nor logo of Wiliot, nor the names of the Software's contributors,
     may be used to endorse or promote products or services derived from this Software,
     without specific prior written permission.

     4. This Software, with or without modification, must only be used in conjunction
     with Wiliot's Pixel or with Wiliot's cloud service.

     5. If any Software is provided in binary form under this license, you must not
     do any of the following:
     (a) modify, adapt, translate, or create a derivative work of the Software; or
     (b) reverse engineer, decompile, disassemble, decrypt, or otherwise attempt to
     discover the source code or non-literal aspects (such as the underlying structure,
     sequence, organization, ideas, or algorithms) of the Software.

     6. If you create a derivative work and/or improvement of any Software, you hereby
     irrevocably grant each of Wiliot and its corporate affiliates a worldwide, non-exclusive,
     royalty-free, fully paid-up, perpetual, irrevocable, assignable, sublicensable
     right and license to reproduce, use, make, have made, import, distribute, sell,
     offer for sale, create derivative works of, modify, translate, publicly perform
     and display, and otherwise commercially exploit such derivative works and improvements
     (as applicable) in conjunction with Wiliot's products and services.

     7. You represent and warrant that you are not a resident of (and will not use the
     Software in) a country that the U.S. government has embargoed for use of the Software,
     nor are you named on the U.S. Treasury Department's list of Specially Designated
     Nationals or any other applicable trade sanctioning regulations of any jurisdiction.
     You must not transfer, export, re-export, import, re-import or divert the Software
     in violation of any export or re-export control laws and regulations (such as the
     United States' ITAR, EAR, and OFAC regulations), as well as any applicable import
     and use restrictions, all as then in effect

   THIS SOFTWARE IS PROVIDED BY WILIOT "AS IS" AND "AS AVAILABLE", AND ANY EXPRESS
   OR IMPLIED WARRANTIES OR CONDITIONS, INCLUDING, BUT NOT LIMITED TO, ANY IMPLIED
   WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY, NONINFRINGEMENT,
   QUIET POSSESSION, FITNESS FOR A PARTICULAR PURPOSE, AND TITLE, ARE DISCLAIMED.
   IN NO EVENT SHALL WILIOT, ANY OF ITS CORPORATE AFFILIATES OR LICENSORS, AND/OR
   ANY CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
   OR CONSEQUENTIAL DAMAGES, FOR THE COST OF PROCURING SUBSTITUTE GOODS OR SERVICES,
   FOR ANY LOSS OF USE OR DATA OR BUSINESS INTERRUPTION, AND/OR FOR ANY ECONOMIC LOSS
   (SUCH AS LOST PROFITS, REVENUE, ANTICIPATED SAVINGS). THE FOREGOING SHALL APPLY:
   (A) HOWEVER CAUSED AND REGARDLESS OF THE THEORY OR BASIS LIABILITY, WHETHER IN
   CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE);
   (B) EVEN IF ANYONE IS ADVISED OF THE POSSIBILITY OF ANY DAMAGES, LOSSES, OR COSTS; AND
   (C) EVEN IF ANY REMEDY FAILS OF ITS ESSENTIAL PURPOSE.
"""
from threading import Thread
'''
Created on Oct 31, 2021

@author: davidd
'''
import logging
import serial
import threading
from time import sleep, time
from tkinter import *
from serial import tools
import pygubu
from sys import path
from os.path import abspath, dirname, join, isfile
from json import load, dump
# path.append(abspath(dirname(join('..', '..', '..', '..', 'pywiliot_internal'))))
from wiliot.wiliot_testers.test_equipment import *
from wiliot.gateway_api.gateway import WiliotGateway, ActionType, DataType
from ConfigsGui import OUTPUT_DIR, CONFIGS_DIR

logger = logging.getLogger('sample')

path.append(abspath(join(dirname(__file__), '..', '..', '..', '..', 'wiliot-debug-jtag-tool')))

barcodeMutex = threading.Lock()

CONNECT_HW = 'Connect HW'
GO = 'Go'
CONTINUE = 'Continue'
READ = 'Read'
FINISH = 'Finish'
SEND = 'Send'

ADD = 'ADD'
REMOVE = 'REMOVE'

GW_CANCEL = '!reset'

# gateway
GW_RESET = '!reset'
GW_VERSION = 'Gateway version: '
GW_AVAILABLE_VERSION = 'Available Version: '
GW_PARAMETERS = ['tTotal', 'tOn', 'channel', 'pattern', 'attenuation']

GW_APP = '!gateway_app'
GW_APP_ETC = '2480 0 2402'
GW_APP_PARAMS = {'prefix': GW_APP, 'channel': '',
                 'tTotal': '', 'tOn': '', 'etc': GW_APP_ETC}

GW_ENERGIZING = '!set_energizing_pattern'
GW_ENERGIZING_PARAMS = {'prefix': GW_ENERGIZING, 'pattern': ''}

# attenuator
ATTENUATION = 'atten'

BLE = 'Ble'
LORA = 'LoRa'

BARCODES = 'Barcodes'
ATTENUATORS = 'Atten'
CHAMBERS = 'Chambers'

GW_TBP_VERSION = '2.5.1'


class ComConnect(object):
    '''
    classdocs
    '''
    isGui = False
    hwConnected = False
    cur_gw_tbp_version = False
    missing_com_port = False
    wiliotTags = False
    gateway = None
    attenuator = None
    chambers_move_com = ''
    barcodes_move_com = ''
    gwVersion = ''
    reel_id = ''
    gtin = ''
    barcodes_state = ADD
    chambers_state = ADD
    barcodes_serials = {}
    chambers_serials = {}
    atten_serials = {}
    used_ports = []
    gw_com_port = []
    barcode_error = []
    chambers_to_close = []
    gw_latest_version = ['']
    gw_update_status = 'disabled'
    start_time = 0

    def __init__(self, top_builder=None, new_tag_func=None, update_go=None, default_dict=None):
        '''
        Constructor
        '''
        self.gateway = WiliotGateway(logger_name='sample')
        # self.gateway = WiliotGateway(verbose=False)
        self.top_builder = top_builder
        self.add_tag_to_test = new_tag_func
        self.update_go_state = update_go
        self.default_dict = default_dict
        # self.chamber = Tescom('COM3')

    def __del__(self):
        if self.gateway is not None and self.is_gw_serial_open():
            self.gateway.close_port()

        for com_port, barcode in self.barcodes_serials.items():
            if barcode is not None and barcode.is_open():
                barcode.close_port()

        for com_port, chamber in self.chambers_serials.items():
            if chamber is not None and chamber.is_connected():
                chamber.open_chamber()
                chamber.close_port()

        # for com_port, atten in self.atten_serials.items():
        #     if atten!=None and 'serial' in atten.keys() and atten['serial']!=None and atten:
        #         atten.disconnect()

    def gui(self, ttk_frame=None):
        self.builder = builder = pygubu.Builder()
        ui_file = join(abspath(dirname(__file__)), 'utils', 'com_connect.ui')
        self.builder.add_from_file(ui_file)

        img_path = join(abspath(dirname(__file__)), '.')
        builder.add_resource_path(img_path)
        img_path = join(abspath(dirname(__file__)), 'utils')
        builder.add_resource_path(img_path)

        self.ttk = ttk_frame

        self.ttk.title("ComConnect")

        self.mainwindow = self.builder.get_object('mainwindow', self.ttk)

        self.builder.connect_callbacks(self)
        self.isGui = True
        self.find_com_ports()
        self.set_gui_defaults()

        self.ttk.protocol("WM_DELETE_WINDOW", self.close)
        self.ttk.lift()
        self.ttk.attributes("-topmost", True)
        self.ttk.attributes("-topmost", False)

        # self.set_gui_defaults()

        self.ttk.mainloop()

    def find_com_ports(self, *args):
        com_ports = [s.device for s in tools.list_ports.comports()]
        if len(com_ports) == 0:
            com_ports = [s.name for s in tools.list_ports.comports()]
        available_ports = [com_port for com_port in com_ports if com_port not in self.used_ports]
        
        self.update_com_gui(available_ports, com_ports)

    def set_gui_defaults(self):

        if self.serials_connected(CHAMBERS):
            self.builder.get_object('connect_chambers').configure(text='Disconnect')
            self.builder.get_object('chosenChambers')['state'] = 'disabled'
            self.builder.get_object('availableChambers')['state'] = 'disabled'
            self.builder.get_object('chambers_up')['state'] = 'disabled'
            self.builder.get_object('chambers_down')['state'] = 'disabled'
            self.builder.get_object('addChambers')['state'] = 'disabled'
        else:
            self.builder.get_object('connect_chambers').configure(text='Connect')

        ble_atten = ''
        lora_atten = ''
        for com_port, atten in self.atten_serials.items():
            ble_atten = com_port if atten['type'] == BLE else ble_atten
            lora_atten = com_port if atten['type'] == LORA else lora_atten

        self.builder.get_object('attenComBle').set(ble_atten)
        self.builder.get_object('attenComLoRa').set(lora_atten)
        if self.serials_connected(ATTENUATORS):
            self.builder.get_object('connect_atten').configure(text='Disconnect')
            self.builder.get_object('attenComBle')['state'] = 'disabled'
            self.builder.get_object('attenComLoRa')['state'] = 'disabled'
        else:
            self.builder.get_object('connect_atten').configure(text='Connect')
        pass

    def update_com_gui(self, available_ports, com_ports):
        self.builder.get_object('gwCom')['values'] = available_ports + ['']
        self.builder.get_object('attenComBle')['values'] = available_ports + ['']
        self.builder.get_object('attenComLoRa')['values'] = available_ports + ['']
        self.update_multi_serials(available_ports, BARCODES)
        self.update_multi_serials(available_ports, CHAMBERS)
        
        self.missing_com_port = False
        
        self.check_chosen_ports(com_ports)
        self.check_opened_ports()

    def check_chosen_ports(self, com_ports):
        if len(self.gw_com_port)==0 or self.gw_com_port[0] not in com_ports:
            self.gw_com_port = ['']
            self.builder.get_object('gwCom').set('')
            self.missing_com_port = True
            
        i = 0
        while i < len(self.atten_serials.keys()):
            port = list(self.atten_serials.keys())[i]
            atten = list(self.atten_serials.values())[i]
            if port != '' and port not in com_ports:
                self.atten_serials.pop(port)
                self.builder.get_object(f"attenCom{atten['type']}").set('')
                self.missing_com_port = True
                continue
            i += 1
            
        self.check_multi_coms(BARCODES, com_ports)
        self.check_multi_coms(CHAMBERS, com_ports)
                
    def check_multi_coms(self, obj, com_ports):
        self.builder.get_object(f'chosen{obj}').delete(0, END)
        ports = getattr(self, f'{obj.lower()}_serials')
        for port in ports.keys():
            if port in com_ports:
                self.builder.get_object(f'chosen{obj}').insert(END, port)
            else:
                self.missing_com_port = True
                
    def check_opened_ports(self):
        if self.is_gui_opened():
            self.check_gw_open()
            self.check_multi_open(BARCODES)
            self.check_multi_open(CHAMBERS)
            self.check_atten_open()
            
    def check_multi_open(self, obj):
        if self.serials_connected(obj):
            self.builder.get_object(f'connect_{obj.lower()}').configure(text='Disconnect')
            self.builder.get_object(f'chosen{obj}')['state'] = 'disabled'
            self.builder.get_object(f'available{obj}')['state'] = 'disabled'
            self.builder.get_object(f'{obj.lower()}_up')['state'] = 'disabled'
            self.builder.get_object(f'{obj.lower()}_down')['state'] = 'disabled'
            self.builder.get_object(f'add{obj}')['state'] = 'disabled'
        else:
            self.builder.get_object(f'connect_{obj.lower()}').configure(text='Connect')
            self.builder.get_object(f'chosen{obj}')['state'] = 'normal'
            self.builder.get_object(f'available{obj}')['state'] = 'normal'
            self.builder.get_object(f'{obj.lower()}_up')['state'] = 'normal'
            self.builder.get_object(f'{obj.lower()}_down')['state'] = 'normal'
            self.builder.get_object(f'add{obj}')['state'] = 'normal'
        
    def check_gw_open(self):    
        if len(self.gw_com_port) > 0 and self.gw_com_port[0]!='':
            self.builder.get_object('gwCom').set(self.gw_com_port[0])
        if self.is_gw_serial_open():
            self.builder.get_object('connect_gw').configure(text='Disconnect')
            self.builder.get_object('gwCom')['state'] = 'disabled'
            self.builder.get_object('version').configure(text=GW_VERSION + self.gwVersion[0])
            self.builder.get_object('latestVersion').configure(text=GW_AVAILABLE_VERSION + self.gw_latest_version[0])
            self.builder.get_object('update_gw')['state'] = self.gw_update_status
        else:
            self.builder.get_object('connect_gw').configure(text='Connect')
            self.builder.get_object('gwCom')['state'] = 'normal'
            self.builder.get_object('version').configure(text=GW_VERSION)
            self.builder.get_object('latestVersion').configure(text=GW_AVAILABLE_VERSION)
            self.builder.get_object('update_gw')['state'] = 'disabled'
            
    def check_atten_open(self):
        connected = False
        for com, atten in self.atten_serials.items():
            if atten['serial'] is not None and atten['serial'].GetActiveTE().is_open():
                connected = True
        if connected:
            self.builder.get_object(f'connect_atten').configure(text='Disconnect')
            self.builder.get_object(f'attenComLoRa')['state'] = 'disabled'
            self.builder.get_object(f'attenComBle')['state'] = 'disabled'
        else:
            self.builder.get_object(f'connect_atten').configure(text='Connect')
            self.builder.get_object(f'attenComLoRa')['state'] = 'normal'
            self.builder.get_object(f'attenComBle')['state'] = 'normal'
            
    def choose_com_ports(self, default_dict):
        com_ports = [s.device for s in tools.list_ports.comports()]
        if len(com_ports) == 0:
            com_ports = [s.name for s in tools.list_ports.comports()]
        
        if 'gw' in default_dict.keys() and default_dict['gw'] in com_ports:
            self.gw_com_port = [default_dict['gw']]
            self.used_ports.append(default_dict['gw'])
        else:
            self.gw_com_port = ['']
            self.missing_com_port = True
        if 'atten' in default_dict.keys() and BLE in default_dict['atten'].keys() and default_dict['atten'][BLE]\
                in com_ports:
            self.atten_serials[default_dict['atten'][BLE]] = {}
            self.atten_serials[default_dict['atten'][BLE]]['type'] = BLE
            self.atten_serials[default_dict['atten'][BLE]]['serial'] = None
            self.used_ports.append(default_dict['atten'][BLE])
        elif 'atten' in default_dict.keys() and BLE in default_dict['atten'].keys()\
                and default_dict['atten'][BLE].strip() != '':
            self.missing_com_port = True
        if 'atten' in default_dict.keys() and LORA in default_dict['atten'].keys() and default_dict['atten'][LORA]\
                in com_ports:
            self.atten_serials[default_dict['atten'][LORA]] = {}
            self.atten_serials[default_dict['atten'][LORA]]['type'] = LORA
            self.atten_serials[default_dict['atten'][LORA]]['serial'] = None
            self.used_ports.append(default_dict['atten'][LORA])
        elif 'atten' in default_dict.keys() and LORA in default_dict['atten'].keys()\
                and default_dict['atten'][LORA].strip() != '':
            self.missing_com_port = True

        if 'barcodes' in default_dict.keys():
            self.barcodes_serials = dict.fromkeys([barcode for barcode in default_dict['barcodes'] if barcode
                                                  in com_ports], None)
            self.used_ports += list(self.barcodes_serials.keys()) 
            
        if 'chambers' in default_dict.keys():
            self.chambers_serials = dict.fromkeys([chamber for chamber in default_dict['chambers'] if chamber
                                                  in com_ports], None)
            self.used_ports += list(self.chambers_serials.keys()) 

        missing_barcodes = []
        missing_chambers = []
        if 'barcodes' in default_dict.keys():
            missing_barcodes = [barcode for barcode in default_dict['barcodes'] if barcode not in com_ports]
        if 'chambers' in default_dict.keys():
            missing_chambers = [chamber for chamber in default_dict['chambers'] if chamber not in com_ports]
        if any(missing_barcodes + missing_chambers):
            self.missing_com_port = True

        return self.missing_com_port

    def choose_gw(self, *args):
        if len(self.gw_com_port) > 0 and self.gw_com_port[0]!='':
            self.used_ports.pop(self.used_ports.index(self.gw_com_port[0]))
        self.gw_com_port = [self.builder.get_object('gwCom').get()]
        self.used_ports.append(self.gw_com_port[0])

    def choose_ble_atten(self, *args):
        ble_com = self.builder.get_object('attenComBle').get()
        ble_last_com = [com for com, item in self.atten_serials.items() if item['type'] == BLE]
        if len(ble_last_com) > 0: 
            self.atten_serials.pop(ble_last_com[0])
            self.used_ports.pop(self.used_ports.index(ble_last_com[0]))
        if ble_com.strip() != '':
            self.atten_serials[ble_com] = {}
            self.atten_serials[ble_com]['type'] = BLE
            self.atten_serials[ble_com]['serial'] = None
            self.used_ports.append(ble_com)

    def choose_lora_atten(self, *args):
        lora_com = self.builder.get_object('attenComLoRa').get()
        lora_last_com = [com for com, item in self.atten_serials.items() if item['type'] == LORA]
        if len(lora_last_com) > 0: 
            self.atten_serials.pop(lora_last_com[0])
            self.used_ports.pop(self.used_ports.index(lora_last_com[0]))
        if lora_com.strip() != '':
            self.atten_serials[lora_com] = {}
            self.atten_serials[lora_com]['type'] = LORA
            self.atten_serials[lora_com]['serial'] = None
            self.used_ports.append(lora_com)


    def connect_all(self, gui=True):
        if not self.is_gw_serial_open():
            success = self.connect_gw(gui)
            if not success:
                return
        if not self.serials_connected(ATTENUATORS):
            self.connect_atten(gui)
        if not self.serials_connected(BARCODES):
            self.connect_barcodes(gui)
        if not self.serials_connected(CHAMBERS):
            self.connect_chambers(gui)
        self.hwConnected = True

    def connect_gw(self, gui=True, disconnect=False):
        if not self.is_gw_serial_open() and not disconnect:
            if len(self.gw_com_port) == 0 or self.gw_com_port[0].strip() == '':
                popup_message('No default com port for GW, please choose GW com port.', title='Error', log='error')
                return False
            com_port = self.gw_com_port[0]
            self.gateway.open_port(port=com_port, baud=921600)
            if self.is_gw_serial_open():
                self.start_listener(not_print_str=True)
                logger.info(f'GW is connected on port: {com_port}.')
                self.gateway.reset_gw()
                sleep(1)
                version = self.gateway.get_gw_version()
                numeric_filter = filter(str.isdigit, version[0])
                version = [".".join(numeric_filter)]
                self.gwVersion = version
                self.gw_latest_version = latest_version = self.gateway.get_latest_version_number()
                cur_version = int(version[0].replace('.', ''))
                self.gw_update_status = 'normal' if cur_version < int(latest_version[0].replace('.', ''))\
                    else 'disabled'
                if cur_version >= int(GW_TBP_VERSION.replace('.', '')):
                    self.cur_gw_tbp_version = True
        else:
            self.gateway.close_port()
            self.builder.get_object('connect_gw').configure(text='Connect')
            self.builder.get_object('version').configure(text=GW_VERSION)
            self.builder.get_object('latestVersion').configure(text=GW_AVAILABLE_VERSION)
            self.builder.get_object('gwCom')['state'] = 'normal'
        if gui:
            self.check_gw_open()

        return True

    def connect_barcodes(self, gui=True):
        self.connect_multi_serials(BARCODES, gui=gui)

    def connect_chambers(self, gui=True):
        self.connect_multi_serials(CHAMBERS, gui=gui)

    def connect_atten(self, gui=True):
        is_connected = self.connect_multi_serials(ATTENUATORS, gui=gui)
        if gui:
            atten_state = 'disabled' if is_connected else 'normal'
            self.builder.get_object('attenComLoRa')['state'] = atten_state
            self.builder.get_object('attenComBle')['state'] = atten_state

    def connect_multi_serials(self, obj, gui=True):
        serials = getattr(self, f'{obj.lower()}_serials')
        is_connected = False
        if self.serials_connected(obj):
            self.close_serials(obj, serials)
            self.builder.get_object(f'connect_{obj.lower()}').configure(text='Connect')
            try:
                self.builder.get_object(f'chosen{obj}')['state'] = 'normal'
                self.builder.get_object(f'available{obj}')['state'] = 'normal'
                self.builder.get_object(f'add{obj}')['state'] = 'normal'
            except:
                pass
        elif len(serials.keys()) > 0:
            self.open_serials(obj, serials)
            if self.serials_connected(obj) and gui:
            # if gui:
                is_connected = True
                self.builder.get_object(f'connect_{obj.lower()}').configure(text='Disconnect')
                try:
                    self.builder.get_object(f'chosen{obj}')['state'] = 'disabled'
                    self.builder.get_object(f'available{obj}')['state'] = 'disabled'
                    self.builder.get_object(f'add{obj}')['state'] = 'disabled'
                except:
                    pass
        if gui:
            self.find_com_ports()
        # self.update_go_state()
        return is_connected

    def open_serials(self, obj, serials):
        threads = []
        for com_port, com_serial in serials.items():
            if 'barcode' in obj.lower():
                if com_serial is not None and com_serial.is_open():
                    continue
                com_serial = BarcodeScanner(com=com_port, log_type='LOG_NL')
                if com_serial.is_open():
                    # self.used_ports.append(com_port)
                    serials[com_port] = com_serial
            elif 'chamber' in obj.lower():
                if com_serial is not None and com_serial.is_connected():
                    continue
                temp_thread = Thread(target=self.connect_chamber, args=([com_port, serials]))
                temp_thread.start()
                threads.append(temp_thread)
            elif 'atten' in obj.lower():
                if com_serial['serial'] is not None or com_port.strip() == '':
                    #8 if serial['serial']!=None and
                    # serial['serial'].GetActiveTE().s.is_open():
                    continue
                com_serial = Attenuator('API', comport=com_port)
                if com_serial.GetActiveTE().is_open():
                    # self.used_ports.append(com_port)
                    serials[com_port]['serial'] = com_serial
                
        for thread in threads:
            thread.join()

    def close(self):
        if self.is_gw_serial_open() and self.serials_connected(ATTENUATORS) and self.serials_connected(BARCODES):
            self.hwConnected = True
            self.enable_hw_connected()
        if self.isGui:
            self.isGui = False
            self.ttk.destroy()
        return self.hwConnected

    def save(self):
        # default_dict = {}
        # if isfile(join(CONFIGS_DIR, '.defaults.json')):
        #     with open(join(CONFIGS_DIR, '.defaults.json'), 'r') as defaultComs:
        #         default_dict = load(defaultComs)
        self.default_dict['gw'] = self.gw_com_port[0]
        self.default_dict['atten'] = {}
        for com_port, atten in self.atten_serials.items():
            self.default_dict['atten'][atten['type']] = com_port
        self.default_dict['barcodes'] = list(self.barcodes_serials.keys())
        self.default_dict['chambers'] = list(self.chambers_serials.keys())
        with open(join(CONFIGS_DIR, '.defaults.json'), 'w+') as defaultComs:
            dump(dict(self.default_dict), defaultComs, indent=4)
            
        logger.info(f'Com ports saved successfully.')

    def focus_barcode_available(self, *args):
        self.focus_available(BARCODES)

    def focus_barcode_chosen(self, *args):
        self.focus_chosen(BARCODES)

    def focus_chamber_available(self, *args):
        self.focus_available(CHAMBERS)

    def focus_chamber_chosen(self, *args):
        self.focus_chosen(CHAMBERS)

    def focus_available(self, obj):
        self.builder.get_object(f'add{obj}').configure(text='>')
        setattr(self, f'{obj.lower()}_state', ADD)

    def focus_chosen(self, obj):
        self.builder.get_object(f'add{obj}').configure(text='<')
        setattr(self, f'{obj.lower()}_state', REMOVE)
        setattr(self, f'{obj.lower()}_move_com', '')

    def add_barcode(self):
        if getattr(self, f'{BARCODES.lower()}_state') == ADD:
            com_chosen = self.builder.get_object(f'available{BARCODES}').get(ACTIVE)
            temp_barcode = BarcodeScanner()
            if not temp_barcode.check_com_port(com_chosen):
                popup_message(f'{com_chosen} is not barcode scanner', title='Error', log='error')
        self.add(BARCODES)
        self.find_com_ports()

    def add_chamber(self):
        self.add(CHAMBERS)
        self.find_com_ports()

    def add(self, obj):
        if getattr(self, f'{obj.lower()}_state') == ADD:
            sending = self.builder.get_object(f'available{obj}')
            receiving = self.builder.get_object(f'chosen{obj}')
        else:
            sending = self.builder.get_object(f'chosen{obj}')
            receiving = self.builder.get_object(f'available{obj}')

        com_list = list(sending.get(0, END))
        com_chosen = sending.get(ACTIVE)
        receiving.insert(END, com_chosen)
        com_index = com_list.index(com_chosen)
        sending.delete(com_index, com_index)

        serials = getattr(self, f'{obj.lower()}_serials')
        com_ports = self.builder.get_object(f'chosen{obj}').get(0, END)
        old_ports = [port for port in serials.keys() if port not in com_ports]
        new_serials = dict(zip(com_ports, [None]*len(com_ports)))
        self.used_ports = [port for port in self.used_ports if port not in old_ports] + list(com_ports)
        setattr(self, f'{obj.lower()}_serials', new_serials)

    def chamber_up(self):
        self.up(CHAMBERS)

    def chamber_down(self):
        self.down(CHAMBERS)

    def barcode_up(self):
        self.up(BARCODES)

    def barcode_down(self):
        self.down(BARCODES)

    def up(self, obj):
        com_list = list(self.builder.get_object(f'chosen{obj}').get(0, END))
        if getattr(self, f'{obj.lower()}_move_com') == '':
            chosen_com = self.builder.get_object(f'chosen{obj}').get(ACTIVE)
            setattr(self, f'{obj.lower()}_move_com', chosen_com)
        else:
            chosen_com = getattr(self, f'{obj.lower()}_move_com')
        com_index = com_list.index(chosen_com)
        if com_index > 0:
            com_list.pop(com_list.index(chosen_com))
            com_list.insert(com_index - 1, chosen_com)
            self.builder.get_object(f'chosen{obj}').delete(0, END)
            for com in com_list:
                self.builder.get_object(f'chosen{obj}').insert(END, com)
            self.builder.get_object(f'chosen{obj}').select_set(com_index - 1)

    def down(self, obj):
        com_list = list(self.builder.get_object(f'chosen{obj}').get(0, END))
        if getattr(self, f'{obj.lower()}_move_com') == '':
            chosen_com = self.builder.get_object(f'chosen{obj}').get(ACTIVE)
            setattr(self, f'{obj.lower()}_move_com', chosen_com)
        else:
            chosen_com = getattr(self, f'{obj.lower()}_move_com')
        com_index = com_list.index(chosen_com)
        if com_index < (len(com_list) - 1):
            com_list.pop(com_list.index(chosen_com))
            com_list.insert(com_index + 1, chosen_com)
            self.builder.get_object(f'chosen{obj}').delete(0, END)
            for com in com_list:
                self.builder.get_object(f'chosen{obj}').insert(END, com)
            self.builder.get_object(f'chosen{obj}').select_set(com_index + 1)

    def update_multi_serials(self, available_ports, obj):
        self.builder.get_object(f'available{obj}').delete(0, END)
        for port in available_ports:
            if port not in self.used_ports:
                self.builder.get_object(f'available{obj}').insert(END, port)
        
    def update_atten_serials(self, available_ports):
        for com, item in self.atten_serials.items():
            if item['serial'] is None or not item['serial'].is_open():
                self.builder.get_object(f'attenCom{item["type"]}')['values'] = available_ports
            else:
                self.builder.get_object(f'attenCom{item["type"]}').set(com)
            
    def connect_chamber(self, com_port, serials):
        com_serial = Tescom(com_port)
        if com_serial.is_connected():
            # self.used_ports.append(com_port)
            serials[com_port] = com_serial
            if not com_serial.is_door_open():
                com_serial.open_chamber()

    def close_serials(self, obj, serials):
        if 'atten' in obj.lower():
            for serial in serials.values():
                # serial['serial'].GetActiveTE.s.close_port()
                if serial['serial'] is not None and serial['serial'].GetActiveTE().is_open():
                    serial['serial'].GetActiveTE().close_port()
                serial['serial'] = None
                # self.used_ports.remove(com_port)
        else:
            for com_serial in serials.values():
                if 'chamber' in obj.lower():
                    com_serial.open_chamber()
                com_serial.close_port()
                # self.used_ports.remove(com_port)
                # serials.pop(com_port)

    def serials_connected(self, obj):
        serials = getattr(self, f'{obj.lower()}_serials')
        if 'atten' in obj.lower():
            serials = dict(zip(serials.keys(), [atten['serial'] for atten in serials.values()]))
        connected_serials = 0
        for com_port, com_serial in serials.items():
            if com_serial is not None:
                if 'barcode' in obj.lower() and com_serial.is_open():
                    connected_serials += 1
                if 'chamber' in obj.lower() and com_serial.is_connected():
                    connected_serials += 1
                if 'atten' in obj.lower():
                    connected_serials += 1
            # if com_port.strip()=='':
            #     connected_serials += 1
        if connected_serials > 0 and connected_serials == len(serials.keys()):
            return True
        else:
            return False

    def get_data(self, actionType=ActionType.ALL_SAMPLE, dataType=DataType.PACKET_CLASS):
        return self.gateway.get_packets(action_type=actionType, data_type=dataType)

    def read_barcode(self, scanner_index=0, close_chamber=False, add_to_test=False):
        scanner = list(self.barcodes_serials.values())[scanner_index]
        full_data, cur_id, reel_id, gtin = scanner.scan_ext_id(scanDur=5)

        cur_id = cur_id if cur_id is not None else full_data
        reel_id = reel_id if reel_id is not None else full_data
        gtin = gtin if gtin is not None else ''
        if reel_id is not None:
            self.reel_id = reel_id
            self.gtin = gtin
        if cur_id is None:
            barcodeMutex.acquire()
            if close_chamber:
                self.barcode_error.append(scanner_index)
            barcodeMutex.release()
            return None, None

        if not close_chamber:
            reel_id_obj = self.top_builder.tkvariables.get('reelId')
            reel_id_obj.set(self.reel_id)

        else:
            success = self.add_tag_to_test(cur_id, reel_id, scanner_index=scanner_index, add_to_test=add_to_test)
            if success:
                self.chambers_to_close.append(scanner_index)

        return cur_id, reel_id

    def read_scanners_barcodes(self, indexes=()):
        if len(indexes) == 0:
            indexes = list(range(len(self.barcodes_serials.values())))
        scanner_threads = []
        self.barcode_error = []
        self.chambers_to_close = []

        for i in indexes:
            t = threading.Thread(target=self.read_barcode, args=(i, True, True))
            scanner_threads.append(t)
            t.start()
        for i in range(len(scanner_threads)):
            t = scanner_threads[i]
            t.join()

        read_message = ''
        title = 'Warning'
        font = 18
        if len(self.barcode_error) > 0:
            read_message += f'Error reading external ID from chambers {self.barcode_error}, try repositioning the tags.\n'
            title = 'Error'
            font = 16
            
        if len(self.chambers_to_close)>0:
            read_message += f'Chambers are closing!!\nWatch your hands!!!'
            
        popupThread = threading.Thread(target=popup_message, args=(read_message, title,("Helvetica", font), title.lower()))
        popupThread.start()
        popupThread.join()
        
        if len(self.chambers_to_close)>0:
            self.close_chambers(self.chambers_to_close)
        
        self.update_go_state()

    def enable_hw_connected(self):
        self.top_builder.get_object('read_qr')['state'] = 'normal'
        self.top_builder.get_object('reelId')['state'] = 'normal'
        if self.top_builder.tkvariables.get('go').get() == CONNECT_HW:
            self.top_builder.tkvariables.get('go').set(READ)
            self.top_builder.get_object('go')['state'] = 'disabled'

    def send_gw_app(self, params):
        str_rsp = []
        self.gateway.reset_buffer()
        self.gateway.clear_rsp_str_input_q()
        temp_gw_params = GW_APP_PARAMS
        temp_gw_energizing = GW_ENERGIZING_PARAMS
        
        self.gateway.reset_start_time()
            
        for param, value in params.items():
            if temp_gw_energizing.get(param) is not None:
                temp_gw_energizing[param] = value
            if temp_gw_params.get(param) is not None:
                temp_gw_params[param] = value
            if param.startswith(ATTENUATION):
                for com_port, atten in self.atten_serials.items():
                    if param.lower().endswith(atten['type'].lower()):
                        try:
                            attenuation = atten['serial'].GetActiveTE().Setattn(float(value))
                            logger.info(f"{atten['type']} Attenuation set to: {str(attenuation).strip()}")
                        except:
                            logger.error(f"{atten['type']} Attenuator error: try reconnect the attenuator.")
                            return False
                            
                        
        self.start_time = time()
        try:
            str_rsp.append(self.gateway.write(b'!set_packet_filter_off'))
            sleep(0.1)
            str_rsp.append(self.gateway.write(b'!set_pacer_interval 0'))
            sleep(0.1)
            str_rsp.append(self.gateway.write(b'!listen_to_tag_only 1'))
            sleep(0.1)
            if self.cur_gw_tbp_version:
                logger.info('TBP calculation using GW time.')
                tester_mode_command = '!set_tester_mode 1'
                self.gateway.write(tester_mode_command)
                sleep(0.1)

            gw_energizing_command = ' '.join(list(temp_gw_energizing.values()))
            str_rsp.append(self.gateway.write(gw_energizing_command))
            sleep(0.1)
    
            gw_app_command = ' '.join(list(temp_gw_params.values()))
            str_rsp.append(self.gateway.write(gw_app_command))
            
        except:
            logger.error(f'Gateway error: try reconnect the gateway.')
            return False
        
        for command in str_rsp:
            if "Command Complete Event" not in command['raw'] and "Energizing" not in command['raw']:
                logger.error(f'Gateway response: {command["raw"]}')
                return False

        return True

    def connect_and_close(self):
        self.connect_all()
        self.close()

    def get_reel_id(self):
        return self.reel_id

    def get_gtin(self):
        return self.gtin

    def get_reel_external(self):
        return self.gtin + self.reel_id

    def is_gw_serial_open(self):
        serial_open, _, _ = self.gateway.get_connection_status()
        return serial_open

    def is_gw_data_available(self):
        return self.gateway.is_data_available()

    def is_gui_opened(self):
        return self.isGui

    def get_gw_version(self):
        return self.gwVersion[0]

    def update_gw(self):
        self.gateway.update_version()

    def get_gw_time(self):
        return self.start_time

    def cancel_gw_commands(self):
        # self.gateway.write(GW_CANCEL)
        self.gateway.reset_gw()
        # self.gateway.stop_continuous_listener()
        # self.gateway.reset_buffer()
        sleep(0.1)
        
    def start_listener(self, not_print_str=True):
        # self.gateway.start_continuous_listener(not_print_str)
        self.gateway.start_continuous_listener()

    def is_hw_connected(self):
        return self.hwConnected
        
    def get_chambers(self):
        return list(self.chambers_serials.values())

    def open_chambers(self, indexes=()):
        chambers_threads = []
        chambers = list(self.chambers_serials.values())
        if len(indexes) == 0:
            indexes = list(range(len(chambers)))
        for index in indexes:
            if len(chambers) > index and chambers[index] is not None:
                temp_thread = Thread(target=chambers[index].open_chamber, args=())
                temp_thread.start()
                chambers_threads.append(temp_thread)
                
        for thread in chambers_threads:
            thread.join()

    def close_chambers(self, indexes=()):
        chambers = list(self.chambers_serials.values())
        chambers_threads = []
        if len(indexes) == 0:
            indexes = list(range(len(chambers)))
        for index in indexes:
            if len(chambers) > index and chambers[index] is not None:
                t = threading.Thread(target=chambers[index].close_chamber, args=())
                chambers_threads.append(t)
                t.start()
        for thread in chambers_threads:
            thread.join()

    def get_num_of_barcode_scanners(self):
        return len(self.barcodes_serials.keys())

    def get_error_barcode(self):
        return self.barcode_error

    def gw_tbp_version(self):
        return self.cur_gw_tbp_version
    
    def gw_get_packets(self):
        self.gateway.get_packets(action_type=ActionType.ALL_SAMPLE, data_type=DataType.PROCESSED)
        
    def get_default_dict(self):
        return self.default_dict


def popup_message(msg, title='Error', font=("Helvetica", 10), log='info', bg=None):
    popup = Tk()
    popup.eval('tk::PlaceWindow . center')
    popup.wm_title(title)
    if bg is not None:
        popup.configure(bg=bg)
    getattr(logger, log)(f'{title} - {msg}')

    def popup_exit():
        popup.destroy()

    label = Label(popup, text=msg, font=font)
    label.pack(side="top", fill="x", padx=10, pady=10)
    b1 = Button(popup, text="Okay", command=popup_exit)
    b1.pack(padx=10, pady=10)
    popup.mainloop()
