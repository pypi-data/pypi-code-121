#!/tools/common/pkgs/python/3.6.3/bin/python3.6
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
'''
Created on Oct 24, 2021

@author: davidd
'''
import logging
import pickle
from numpy.core._multiarray_umath import arange
from urllib.parse import quote
import jwt
import numpy
import requests
from os import remove
from os import _exit, makedirs, mkdir, environ
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import pygubu
from threading import Thread, Lock
from time import sleep
import time
import csv
import datetime
from wiliot.wiliot_testers.sample.ConfigsGui import ConfigsGui, DEFAULT_CONFIGS, OUTPUT_DIR, CONFIGS_DIR
from wiliot.wiliot_testers.sample.ComConnect import ComConnect, GO, CONTINUE, CONNECT_HW, READ, FINISH, SEND, popup_message
from traceback import print_exc
from json import load, dump, loads
import argparse
import sys
from os.path import isfile, abspath, dirname, join, isdir, basename, exists
from wiliot.get_version import get_version
# sys.path.append(abspath(dirname(join('..', '..', '..', '..', 'pywiliot_internal'))))
from wiliot.wiliot_testers.tester_utils \
    import setLogger, changeFileHandler, removeFileHandler, CsvLog, HeaderType, TesterName, StreamToLogger, WiliotDir
from wiliot.packet_data_tools.process_encrypted_packets import estimate_diff_packet_time
from wiliot.packet_data_tools.multi_tag import MultiTag
from wiliot.packet_data_tools.packet_list import PacketList

LOG_LEVEL = 'INFO'

# default_log_file = join(abspath(dirname(__file__)), 'SampleTest.log')
default_log_file = join(OUTPUT_DIR, 'SampleTest.log')
logger = setLogger('sample', LOG_LEVEL, outputFile=default_log_file, file_mode='a+')
sys.stdout = StreamToLogger(logger, logging.INFO)
sys.stderr = StreamToLogger(logger, logging.ERROR)

addToDictMutex = Lock()
calibMutex = Lock()
recvDataMutex = Lock()
timerMutex = Lock()
mutex = Lock()

STOP = 'Stop'
FINISH = 'Finish'

RAW = 'raw'
TIME = 'time'

DEF_NUM_OF_TAGS = 2

PREAMBLE_BYTES = 10
NIBS_IN_BYTE = 2
ADV_ADDR_START = 0
ADV_ADDR_END = 6
CRC_START = 29
PAYLOAD_START = 8

CLOUD_TIMEOUT_POST = 10
CLOUD_TIMEOUT_RESOLVE = 2

CSV_DATABASE_COLUMNS = ['timestamp', 'tested', 'passed', 'responding[%]', 'packets', 'testTime[sec]',
                        'ttfpAvg[sec]', 'ttfpStd[sec]', 'ttfpMin[sec]', 'ttfpMax[sec]', 'tbpAvg[sec]',
                        'tbpStd[sec]', 'tbpMin[sec]', 'tbpMax[sec]', 'channel', 'energizing', 'antennaType',
                        'attenBle[db]', 'attenLoRa[db]', 'externalId', 'numberOfChambers', 'gwVersion', 'pyWiliotVersion']

TOKEN_FILE_NANE = '.token.pkl'

class SampleException(Exception):
    pass

class SampleTest(object):
    goButtonState = CONNECT_HW
    stopButtonState = STOP
    comConnect = None
    configsGui = None
    comTtk = None
    configsTtk = None
    testBarcodesThread = None
    finishThread = None
    finishTestThread = None
    closeChambersThread = None
    gatewayDataThread = None
    timerThread = None
    token = None
    claimSet = None
    testFinished = True
    post_data = True
    wiliotTags = False
    forceCloseRequested = False
    closeRequested = False
    debug_mode = False
    testGo = False
    stopTimer = False
    closeListener = False
    testConfig = ''
    reel_id = ''
    gtin = ''
    testDir = ''
    owner = ''
    station_name = ''
    pywiliot_version = ''
    testTime = 0
    # tagsCount = 0
    testStartTime = 0
    sleep = 0
    cur_atten = 0
    defaultDict = {}
    dataBaseDict = {}
    runDataDict = {}
    params = {}
    test_barcodes = {}
    barcodes_read = {}
    tagsFinished = {}
    packets_dict = {}
    badPreambles = []
    preamblesDict = {}
    totalBadPreambles = []
    add_to_dict_threads = []
    unknown_packets = []
    antenna = ''
    low = 0
    high = 0
    step = 1
    
    # numOfTags = ''
    multiTag = MultiTag()

    def __init__(self, debug_mode=False, calib=None, environment='', post_data=True):

        self.calib = calib
        self.environment = environment
        self.post_data = post_data
        self.pywiliot_version = get_version()
        logger.info(f'PyWiliot version: {self.pywiliot_version}')

        if isfile(join(CONFIGS_DIR, '.defaults.json')):
            with open(join(CONFIGS_DIR, '.defaults.json'), 'r') as defaultComs:
                self.defaultDict = load(defaultComs)

        self.check_token()
        self.popup_login()
        # self.get_token()

        self.builder = builder = pygubu.Builder()
        self.debug_mode = debug_mode

        self.comConnect = ComConnect(top_builder=builder, new_tag_func=self.add_tag_to_test, update_go=self.update_go_state, default_dict=self.defaultDict)
        self.update_data()
        self.configsGui = ConfigsGui(top_builder=builder)

    def gui(self):
        self.set_gui()

        self.ttk.mainloop()

    def set_gui(self):
        uifile = join(abspath(dirname(__file__)), 'utils', 'sample_test.ui')
        self.builder.add_from_file(uifile)

        img_path = join(abspath(dirname(__file__)), '.')
        self.builder.add_resource_path(img_path)
        img_path = join(abspath(dirname(__file__)), 'utils')
        self.builder.add_resource_path(img_path)

        missing_com_port = self.comConnect.choose_com_ports(self.defaultDict)

        if missing_com_port:
            popup_message('Default com ports not available, check connections.', title='Warning', log='warning')

        self.ttk = Tk()

        self.ttk.eval('tk::PlaceWindow . center')
        self.ttk.title("Wiliot Sample Test")
        self.mainWindow = self.builder.get_object('mainwindow', self.ttk)
        self.ttk.protocol("WM_DELETE_WINDOW", self.close)
        self.builder.connect_callbacks(self)
        
        self.builder.get_object('reelId').bind("<Key>", self.reelId)
        list_box = self.builder.get_object('scanned')
        scrollbar = self.builder.get_object('scrollbar1')
        list_box.configure(yscrollcommand=scrollbar.set)
        scrollbar.configure(command=list_box.yview)
        self.builder.get_object('scrollbar1').set(self.builder.get_object('scanned').index(ACTIVE),self.builder.get_object('scanned').index(END))

        self.set_gui_defaults()
        
        
    def choose_param(self, *args):
        var = args[0].widget['style'].split('.')[0]
        if self.builder.tkvariables.get(var) is not None:
            value = self.builder.get_object(var).get()
            if var not in self.defaultDict.keys():
                self.defaultDict[var] = []
            if value in self.defaultDict[var]:
                self.defaultDict[var].pop(self.defaultDict[var].index(value))
            self.defaultDict[var].insert(0, value)
        

    def go(self):
        if self.finishThread is not None and self.finishThread.is_alive():
            self.finishThread.join()
        self.goButtonState = goButtonState = self.builder.tkvariables.get('go').get()
        self.builder.get_object('stop')['state'] = 'disabled'
        self.update_params_state(state='disabled', group=GO)
        self.builder.get_variable('forceGo').set('0')
        recvDataMutex.acquire()
        self.forceCloseRequested = False
        recvDataMutex.release()
        if goButtonState == CONNECT_HW:
            self.connectThread = Thread(target=self.connect_all, args=([False]))
            self.connectThread.start()
        elif goButtonState == READ:
            if self.stopButtonState == SEND:
                self.remove_barcodes()
                self.stopButtonState = FINISH
                self.builder.tkvariables.get('stop').set(FINISH)
            indexes = self.get_missing_ids_chambers()
            self.testBarcodesThread = Thread(target=self.read_scanners_barcodes, args=([indexes]))
            self.testBarcodesThread.start()
        elif goButtonState == GO:
            self.numOfPackets = 0
            self.multiTag = MultiTag()
            self.totalBadPreambles = []
            self.badPreambles = []
            self.preamblesDict = {}
            self.builder.tkvariables.get('stop').set(STOP)
            self.stopButtonState = STOP
            # self.numOfTags = int(self.builder.tkvariables.get('numTags').get())
            self.testId = testId = time.time()
            self.testName = testName = self.builder.get_object('testName').get()
            # self.operator = operator = self.builder.get_object('operator').get()
            if not isdir(join(OUTPUT_DIR, testName)):
                makedirs(join(OUTPUT_DIR, testName))
            self.testDir = testDir = datetime.datetime.fromtimestamp(testId).strftime('%d%m%y_%H%M%S')
            mkdir(join(OUTPUT_DIR, testName, testDir))
            self.common_run_name = common_run_name = self.reel_id + '_' + testDir
            self.test_log_file = join(OUTPUT_DIR, testName, testDir, f'{common_run_name}.log')
            changeFileHandler(logger, self.test_log_file, append_handler=True)
            logger.info(f'Starts new test: {common_run_name}')
            removeFileHandler(logger, default_log_file)
            self.update_params()
            self.testStartTime = time.time()
            if self.calib:
                self.calibModeThread = Thread(target=self.calibThread, args=())
                self.calibModeThread.start()
                self.calibModeThread.join()
                self.calibModeThread = Thread(target=self.calib_mode, args=())
                self.calibModeThread.start()
            else:
                self.sendCommandThread = Thread(target=self.send_gw_commands, args=())
                self.sendCommandThread.start()

        elif goButtonState == CONTINUE:
            self.builder.tkvariables.get('stop').set(STOP)
            self.stopButtonState = STOP
            self.totalBadPreambles.extend(x for x in self.badPreambles if x not in self.totalBadPreambles)
            self.badPreambles = []
            self.preamblesDict = {}
            self.sendCommandThread = Thread(target=self.send_gw_commands, args=())
            self.sendCommandThread.start()
            
    def calibThread(self):
        self.popup_calib()
            
    def read_scanners_barcodes(self, indexes):
        self.comConnect.read_scanners_barcodes(indexes)
        # self.update_params_state(state='normal', group=CONTINUE)
            
    def connect_all(self, gui=True):
        self.comConnect.connect_all(gui=gui)
        self.builder.tkvariables.get('go').set(READ)
        # self.update_params_state(state='normal', group=READ)
        self.builder.get_object('read_qr')['state'] = 'normal'
        self.builder.get_object('reelId')['state'] = 'normal'
        self.builder.get_object('connect')['state'] = 'normal'

    def add_tag_to_test(self, cur_id, reel_id, scanner_index=0, add_to_test=False):
        mutex.acquire()
        if cur_id not in self.test_barcodes.keys() and cur_id not in self.barcodes_read.keys() and add_to_test:
            self.barcodes_read[cur_id] = {'chamber':scanner_index,
                                          'packets':[],
                                          'reel': self.reel_id,
                                          'ext ID': cur_id,
                                          'ttfp': -1,
                                          'tbp': -1,
                                          'rssi': -1,
                                          'preamble': [],
                                          'packetList': PacketList()}
            # self.test_barcodes[cur_id] = scanner_index
            self.builder.get_object('scanned').insert(END, f'{cur_id}, {scanner_index}')
            mutex.release()
        else:
            mutex.release()
            popup_message(f'Tag {cur_id} in chamber {scanner_index} already read.', title='Warning', log='warning')
            return False

        if self.reel_id != '' and self.reel_id != reel_id and self.wiliotTags:
            popup_message('Tag reel different from test reel.', title='Warning', log='error')
            
        return True

    def update_go_state(self, force_go=False):
        if (self.comConnect.get_num_of_barcode_scanners() == len(self.barcodes_read.keys()) or force_go) and\
                len(self.test_barcodes.keys()) > 0:
            self.builder.tkvariables.get('go').set(CONTINUE)
            self.update_params_state(state='normal', group=CONTINUE)
        elif self.comConnect.get_num_of_barcode_scanners() == len(self.barcodes_read.keys()) or force_go:
            self.builder.tkvariables.get('go').set(GO)
            self.update_params_state(state='normal', group=GO)
        else:
            self.builder.tkvariables.get('go').set(READ)
            self.update_params_state(state='normal', group=READ)
        # self.top_builder.get_object('go')['state'] = 'normal'

    def get_missing_ids_chambers(self):
        indexes = list(range(self.comConnect.get_num_of_barcode_scanners()))
        if len(self.barcodes_read.keys()) > 0:
            used_indexes = [barcode['chamber'] for barcode in self.barcodes_read.values()]
            indexes = [index for index in indexes if index not in used_indexes]
        return indexes

    def force_go(self):
        """
        enable go in the GUI even if some of the chambers are empty
        """
        if self.builder.get_variable('forceGo').get() == '1':
            self.builder.get_object('forceGo')['state'] = 'disabled'
            self.builder.get_object('stop')['state'] = 'disabled'
            self.builder.get_object('go')['state'] = 'disabled'
            self.builder.get_object('add')['state'] = 'disabled'
            self.builder.get_object('remove')['state'] = 'disabled'
            if self.closeChambersThread is not None and self.closeChambersThread.is_alive():
                self.closeChambersThread.join()
            self.closeChambersThread = Thread(target=self.force_go_close_chambers, args=())
            self.closeChambersThread.start()
        else:
            self.update_go_state()
            
    def force_go_close_chambers(self):
        indexes = self.get_missing_ids_chambers()
        self.comConnect.close_chambers(indexes)
        self.update_go_state(force_go=True)
        self.builder.get_object('forceGo')['state'] = 'normal'
        self.builder.get_object('stop')['state'] = 'normal'
        self.builder.get_object('go')['state'] = 'normal'

    def calib_mode(self):
        self.testFinished = False
        attenuations = arange(float(self.low), float(self.high) + float(self.step), float(self.step))
        for i in attenuations:
            calibMutex.acquire()
            self.total_num_of_unique = 0
            self.avg_unique = 1
            self.cur_atten = i
            self.preamblesDict = {}
            self.tagsFinished = {}
            self.testGo = True
            if self.antenna.lower() == 'ble':
                self.params['attenBle'] = self.cur_atten
                self.dataBaseDict['attenBle[db]'] = self.cur_atten
            elif self.antenna.lower() == 'lora':
                self.dataBaseDict['attenLoRa[db]'] = self.cur_atten
                self.params['attenLoRa'] = self.cur_atten
            self.sendCommandThread = Thread(target=self.send_gw_commands, args=())
            self.sendCommandThread.start()
            self.sendCommandThread.join()
            sleep(self.sleep)
            if self.forceCloseRequested:
                break

        calibMutex.acquire()
        self.calib_mode_post_process()
        self.comConnect.open_chambers()
        # self.builder.tkvariables.get('numTags').set(0)
        # self.builder.tkvariables.get('go').set(READ)
        # self.test_barcodes = {}
        # self.builder.get_object('connect')['state'] = 'normal'
        # self.builder.get_object('read_qr')['state'] = 'normal'
        calibMutex.release()
        self.finish_test(post_data=False, reset_tester=True, post_process=False)
        popup_message('Sample Test - Calib Mode Finished running.', title='Info', log='info')

    def calib_mode_post_process(self):
        common_run_name = self.reel_id + '_' + self.testDir
        unique_valid = []
        full_test_dir = join(OUTPUT_DIR, self.testName, self.testDir)
        with open(join(full_test_dir, f'{common_run_name}@packets_data_calib_mode.csv'), 'w+', newline='') as newCsv, \
             open(join(full_test_dir, f'{common_run_name}@unique_data.csv'), 'w+', newline='') as new_tagsCsv:
            writer = csv.DictWriter(newCsv, fieldnames=['advAddress', 'status', 'rawData', 'attenuation'])
            writer.writeheader()
            for atten, runData in self.packets_dict.items():
                for extId, data in runData.items():
                    if len(data['packets']) > 0:
                        for packet in data['packets']:
                            packet_raw = packet['raw'].split('(')[1].split(')')[0].strip(' "')
                            if 'packet' in packet.keys():
                                packet.pop('packet')
                            tag_row = {
                                       'advAddress':
                                            packet_raw[ADV_ADDR_START * NIBS_IN_BYTE:ADV_ADDR_END * NIBS_IN_BYTE],
                                       'status': 'PASSED',
                                       'rawData': packet,
                                       'attenuation': atten
                                       }
                            writer.writerows([tag_row])

                    unique_valid.append({
                                         'preamble': data['preamble'],
                                         'tbp': data['tbp'],
                                         'ttfp': data['ttfp'],
                                         'ext ID': data['ext ID'],
                                         'reel': data['reel'],
                                         'attenuation': atten
                                         })

            writer = csv.DictWriter(new_tagsCsv, fieldnames=unique_valid[0].keys())
            writer.writeheader()
            writer.writerows(unique_valid)
            
        self.barcodes_read = {}
        self.test_barcodes = {}
        self.builder.get_object('scanned').delete(0, END)
            
    def calib_mode_clean_barcodes(self):
        old_barcodes = self.barcodes_read.copy()
        self.barcodes_read = {}
        self.test_barcodes = {}
        self.builder.get_object('scanned').delete(0, END)
        for tag in old_barcodes.values():
            self.add_tag_to_test(tag['ext ID'], tag['reel'], tag['chamber'], add_to_test=True)

    def stop(self):
        """
        stop the test and run post process
        """
        if self.stopButtonState == STOP:
            self.forceCloseRequested = True
        
        elif self.stopButtonState == FINISH:
            # self.numOfTags = len(self.test_barcodes.keys())
            # self.finishThread = Thread(target=self.iteration_finished, args=([True]))
            # self.finishThread.start()
            self.builder.get_object('scanned').delete(0, END)
            self.builder.tkvariables.get('stop').set(SEND)
            self.stopButtonState = SEND
            for barcode in list(self.test_barcodes.keys()):
                self.builder.get_object('scanned').insert(END, barcode)
            
        elif self.stopButtonState == SEND:
            self.builder.get_object('go')['state'] = 'disabled'
            self.builder.get_object('stop')['state'] = 'disabled'
            self.builder.get_object('forceGo')['state'] = 'disabled'
            self.builder.get_object('add')['state'] = 'disabled'
            self.builder.get_object('remove')['state'] = 'disabled'
            self.finishThread = Thread(target=self.finish, args=())
            self.finishThread.start()

    def add(self):
        """
        add manually tag to the list
        """
        new_tag = self.builder.tkvariables.get('addTag').get()
        if self.builder.tkvariables.get('stop').get()!=SEND and not new_tag.split(',')[0].strip() in self.barcodes_read.keys():
            # self.builder.get_object('scanned').insert(END, new_tag)
            # self.barcodes_read[new_tag.split(',')[0].strip()] = new_tag.split(',')[1].strip()
            if len(new_tag.split(',')) < 2:
                popup_message(f'Missing chamber index, add chamber index after a comma.', title='Error', log='error')
                return
            cur_id = new_tag.split(',')[0].strip()
            scan_index = int(new_tag.split(',')[1].strip())
            if (scan_index + 1) > self.comConnect.get_num_of_barcode_scanners():
                popup_message(f'Chamber number {scan_index} not exists.', title='Error', log='error')
                return

            barcodes = self.builder.get_object('scanned').get(0, END)
            if any([barcode for barcode in barcodes if int(barcode.split()[1].strip()) == scan_index]):
                popup_message(f'Chamber {scan_index} tag already scanned.', title='Error', log='error')
                return
            # logger.info(scan_index)

            self.builder.tkvariables.get('addTag').set('')
            popup_thread = Thread(target=popup_message, args=('Chambers are closing!!\nWatch your hands!!!',
                                                              'Warning', ("Helvetica", 18), 'warning'))
            popup_thread.start()
            popup_thread.join()
            self.add_tag_to_test(cur_id, self.reel_id, scan_index, add_to_test=True)
            chambers = self.comConnect.get_chambers()
            if len(chambers) > scan_index and chambers[scan_index] is not None:
                chambers[scan_index].close_chamber()
            self.update_go_state()
        else:
            self.builder.get_object('scanned').insert(END, new_tag)
            self.builder.tkvariables.get('addTag').set('')
            


    def remove(self):
        """
        remove tag read from the list
        """
        tag = self.builder.get_object('scanned').get(ACTIVE)
        tags = list(self.builder.get_object('scanned').get(0, END))
        tag_index = tags.index(tag)
        self.builder.get_object('scanned').delete(tag_index, tag_index)
        tags.pop(tag_index)
        self.builder.tkvariables.get('addTag').set(tag)
        if self.stopButtonState != SEND:
            self.barcodes_read.pop(tag.split(',')[0].strip())
            self.comConnect.open_chambers(indexes=[int(tag.split(',')[1].strip())])
            self.update_go_state()
            

    def update_params_state(self, state='disabled', group=GO):
        if state=='disabled' or group==READ:
            self.builder.get_object('connect')['state'] = state
            
            if len(self.test_barcodes.keys())==0:
                self.builder.get_object('read_qr')['state'] = state
                self.builder.get_object('reelId')['state'] = state
                
            if self.reel_id!='':
                self.builder.get_object('go')['state'] = state
                self.builder.get_object('add')['state'] = state
                self.builder.get_object('remove')['state'] = state
                self.builder.get_object('addTag')['state'] = state
                self.builder.get_object('stop')['state'] = state
                self.builder.get_object('forceGo')['state'] = state
                
        
        if state=='disabled' or group==GO:
            self.builder.get_object('configs')['state'] = state
            self.builder.get_object('test_config')['state'] = state
            self.builder.get_object('testName')['state'] = state
            self.builder.get_object('operator')['state'] = state
            self.builder.get_object('inlay')['state'] = state
            self.builder.get_object('surface')['state'] = state
            
        if state=='disabled' or group==CONTINUE or group==GO:
            self.builder.get_object('connect')['state'] = state
            self.builder.get_object('go')['state'] = state
            self.builder.get_object('add')['state'] = state
            self.builder.get_object('remove')['state'] = state
            self.builder.get_object('addTag')['state'] = state
            self.builder.get_object('forceGo')['state'] = 'disabled'
            
            if len(self.test_barcodes.keys())==0:
                self.builder.get_object('read_qr')['state'] = state
                self.builder.get_object('reelId')['state'] = state
        
        if state=='disabled':
            self.builder.get_object('read_qr')['state'] = state
            self.builder.get_object('reelId')['state'] = state

    def set_gui_defaults(self):
        configs = self.configsGui.get_configs()
        
        self.builder.get_object('test_config')['values'] = \
            [key for key, item in configs.items() if isinstance(item, dict)]

        if 'testName' in self.defaultDict.keys():
            self.builder.get_object('testName')['values'] = self.defaultDict['testName']
            self.builder.get_object('testName').set(self.defaultDict['testName'][0])
            
        if 'operator' in self.defaultDict.keys():
            self.builder.get_object('operator')['values'] = self.defaultDict['operator']
            self.builder.get_object('operator').set(self.defaultDict['operator'][0])
            
        if 'inlay' in self.defaultDict.keys():
            self.builder.get_object('inlay')['values'] = self.defaultDict['inlay']
            self.builder.get_object('inlay').set(self.defaultDict['inlay'][0])
            
        if 'surface' in self.defaultDict.keys():
            self.builder.get_object('surface')['values'] = self.defaultDict['surface']
            self.builder.get_object('surface').set(self.defaultDict['surface'][0])
        # if 'numOfTags' in self.defaultDict.keys():
            # self.builder.tkvariables.get('numTags').set(self.defaultDict['numOfTags'])
        # else:
            # self.builder.tkvariables.get('numTags').set(DEF_NUM_OF_TAGS)
        self.builder.tkvariables.get('numTags').set(0)
            
        if self.token is None:
            self.builder.get_variable('sendToCloud').set('0')
        else:
            self.builder.get_variable('sendToCloud').set('1')
            
        if 'config' in self.defaultDict.keys():
            self.testConfig = self.defaultDict['config']
        else:
            self.testConfig = DEFAULT_CONFIGS[0]
        self.builder.get_object('test_config').set(self.testConfig)
        self.configsGui.set_default_config(self.testConfig)
        self.configsGui.set_params(self.testConfig)

    def open_configs(self):
        """
        open Configs GUI
        """
        if self.configsGui is not None and not self.configsGui.is_gui_opened():
            self.configsTtk = Toplevel(self.ttk)
            self.ttk.eval(f'tk::PlaceWindow {str(self.configsTtk)} center')
            self.configsGui.gui(self.configsTtk)

    def test_config(self, *args):
        """
        update the configs in Configs module according to the main GUI
        """
        self.configsGui.config_set(self.builder.get_object('test_config').get())

    def open_com_ports(self):
        """
        open ComConnect GUI
        """
        if self.comConnect is not None and not self.comConnect.is_gui_opened():
            self.comTtk = Toplevel(self.ttk)
            self.ttk.eval(f'tk::PlaceWindow {str(self.comTtk)} center')
            self.comConnect.gui(self.comTtk)

    def read_qr(self):
        barcode, reel = self.comConnect.read_barcode()
        if barcode is None:
            read_qr_thread = Thread(target=popup_message, args=(
                [f'Error reading external ID, try repositioning the tag.', 'Error', ("Helvetica", 10), 'error']))
            read_qr_thread.start()
            read_qr_thread.join()
            if not self.calib:
                return
            
        if reel is not None:
            reel_id = self.builder.tkvariables.get('reelId')
            reel_id.set(reel)
            self.reel_id = reel

        if 'config' in self.defaultDict.keys():
            self.testConfig = self.defaultDict['config']
        else:
            self.testConfig = DEFAULT_CONFIGS[0]
            
        self.builder.get_object('reelId').unbind("<Key>")
        self.update_params_state(state='normal', group=GO)
        self.builder.get_object('forceGo')['state'] = 'normal'

    def reelId(self, *args):
        reel = self.builder.tkvariables.get('reelId').get()
        if reel.strip() != '' and (str(args[0].type)!='KeyPress' or args[0].keysym=='Return'):
            self.reel_id = reel
            self.update_params_state(state='normal', group=GO)
            self.builder.get_object('reelId').unbind("<Key>")
            self.builder.get_object('forceGo')['state'] = 'normal'
            

    def update_params(self):
        self.runDataDict = {}
        self.dataBaseDict = {}
        self.params = params = self.configsGui.get_params()
        # self.operator = 
        # antenna_type = self.builder.get_object('test_config').get()
        self.testConfig = self.defaultDict['config'] = self.builder.get_object('test_config').get()
        self.update_data()
        # antenna_type = 'TIKI' if 'TIKI' in antenna_type.upper() else 'TEO'
        
        self.dataBaseDict['pyWiliotVersion'] = self.pywiliot_version
        # self.dataBaseDict['operator'] = self.runDataDict['operator'] = self.operator 
        self.dataBaseDict['operator'] = self.builder.get_object('operator').get() 
        # self.dataBaseDict['chambers'] = self.runDataDict['chambers'] = self.comConnect.get_num_of_barcode_scanners()
        # self.dataBaseDict['chambers'] = self.comConnect.get_num_of_barcode_scanners()
        self.dataBaseDict['timestamp'] = datetime.datetime.fromtimestamp(self.testId).strftime('%d/%m/%y %H:%M:%S')
        self.dataBaseDict['tested'] = self.builder.get_object('numTags').get()
        self.dataBaseDict['channel'] = params['channel']
        # self.dataBaseDict['total time'] = params['tTotal']
        # self.dataBaseDict['on time'] = params['tOn']
        # self.dataBaseDict['reel'] = self.builder.tkvariables.get('reelId').get()
        self.dataBaseDict['externalId'] = self.comConnect.get_reel_external()
        self.dataBaseDict['gwVersion'] = self.comConnect.get_gw_version()
        if 'sleep' in params.keys():
            self.sleep = int(params['sleep'])
        else:
            self.sleep = 0
        self.testTime = float(params['testTime'])
        
        self.runDataDict['runStartTime'] = self.dataBaseDict['runStartTime'] = time.strftime('%d/%m/%y %H:%M:%S')
        self.runDataDict['antennaType'] = self.dataBaseDict['antennaType'] = params['antennaType']
        self.runDataDict['bleAttenuation'] = self.dataBaseDict['attenBle[db]'] = params['attenBle']
        self.runDataDict['loraAttenuation'] = self.dataBaseDict['attenLoRa[db]'] = params['attenLoRa']
        self.runDataDict['energizingPattern'] = self.dataBaseDict['energizing'] = params['pattern']
        self.runDataDict['testTime'] = self.dataBaseDict['testTime[sec]'] = params['testTime']
        self.runDataDict['inlay'] = self.dataBaseDict['inlay'] = self.builder.get_object('inlay').get()
        self.runDataDict['surface'] = self.dataBaseDict['surface'] = self.builder.get_object('surface').get()
        self.runDataDict['testerStationName'] = self.station_name
        self.runDataDict['commonRunName'] = self.common_run_name
        self.runDataDict['testerType'] = 'sample'
        self.runDataDict['gwVersion'] = self.comConnect.get_gw_version()
        self.runDataDict['operator'] = self.dataBaseDict['operator'] = self.builder.get_object('operator').get()
        self.runDataDict['pyWiliotVersion'] = self.dataBaseDict['pyWiliotVersion'] = self.pywiliot_version
        self.runDataDict['testTimeProfilePeriod'] = self.dataBaseDict['testTimeProfilePeriod'] = params['tTotal']
        self.runDataDict['testTimeProfileOnTime'] = self.dataBaseDict['testTimeProfileOnTime'] = params['tOn']
        self.runDataDict['numChambers'] = self.dataBaseDict['numChambers'] = self.comConnect.get_num_of_barcode_scanners()

    def send_gw_commands(self):
        """
        send commands to the GW and start the packet listener
        """
        if self.sleep > 0:
            for i in range(self.sleep):
                sleep(1)
                if i % 3 == 0:
                    print('.', end='')
            print()
        self.recv_data_from_gw()
        self.testFinished = False
        
    def stop_state(self):
        self.builder.get_object('stop')['state'] = 'normal'

    def recv_data_from_gw(self):
        self.tagsFinished = {}
        self.testGo = True
        self.startTime = self.comConnect.get_gw_time()
        logger.info(f'Tags in the test: {",".join(list(self.barcodes_read.keys()))}')
        gw_passed = self.comConnect.send_gw_app(self.params)
        if not gw_passed:
            popup_message(f'Error sending GW commands.', 'Error', ("Helvetica", 10), 'error')
            return
        self.gatewayDataThread = Thread(target=self.stop_state(), args=())
        self.gatewayDataThread.start()
        last_time = time.time()
        self.targetTime = last_time + self.testTime
        if self.timerThread is not None:
            self.timerThread.join()
        self.timerThread = Thread(target=self.timer_count_down, args=([self.targetTime]))
        self.timerThread.start()
        self.sync_thread = Thread(target=self.threads_sync, args=())
        self.sync_thread.start()
        packets_list = []
        recvDataMutex.acquire()
        while True:
            sleep(0.001)
            try:
                if self.closeListener:
                    logger.info("DataHandlerProcess Stop")
                    break

                if self.comConnect.is_gw_data_available():

                    gw_data = self.comConnect.get_data()

                    for packet in gw_data.packet_list:
                        if packet.gw_data['time_from_start'].size>1:
                            for i in range(packet.gw_data['time_from_start'].size):
                                packetTime = packet.gw_data['time_from_start'][i]
                                packets_list.append({'raw':packet.get_packet_string(i), 'time':packetTime, 'packet': packet})
                        else:
                            packetTime = packet.gw_data['time_from_start'].item()
                            packets_list.append({'raw':packet.get_packet_string(0), 'time':packetTime, 'packet': packet})
                            
                        cur_time = time.time()
                        if cur_time - last_time > 2 and len(packets_list) > 0:
                            temp_thread = Thread(target=self.add_to_packet_dict, args=([packets_list.copy()]))
                            # temp_thread.start()
                            addToDictMutex.acquire()
                            self.add_to_dict_threads.append(temp_thread)
                            addToDictMutex.release()
                            packets_list = []
                            last_time = cur_time

            except BaseException:
                print_exc()
                pass
            
        self.comConnect.cancel_gw_commands()
        timerMutex.acquire()
        self.stopTimer = True
        timerMutex.release()
        # self.tagsCount += len(self.barcodes_read.keys())
        recvDataMutex.release()
        self.sync_thread.join()
        self.closeListener = False
        if not self.calib:
            self.builder.get_object('stop')['state'] = 'disabled'
            self.finishIterThread = Thread(target=self.iteration_finished, args=())
            self.finishIterThread.start()
        elif self.calib:
            self.post_process_iteration()
            self.packets_dict[self.cur_atten] = {}
            self.packets_dict[self.cur_atten].update(self.barcodes_read)
            self.calib_mode_clean_barcodes()
            calibMutex.release()
            
    def threads_sync(self):
        while not self.closeRequested and not self.forceCloseRequested and time.time() < self.targetTime:
            if len(self.add_to_dict_threads) > 0:
                addToDictMutex.acquire()
                thread = self.add_to_dict_threads.pop()
                addToDictMutex.release()
                thread.start()
                thread.join()
            sleep(0.1)
        self.closeRequested = False
        self.closeListener = True
        self.add_to_dict_threads = []

    def timer_count_down(self, target_time):
        """
        count down the test time
        """
        while True:
            if self.stopTimer:
                timerMutex.acquire()
                self.stopTimer = False
                timerMutex.release()
                break
            timer = int(target_time - time.time())
            update_timer_thread = Thread(target=self.update_timer, args=([timer]))
            update_timer_thread.start()
            update_timer_thread.join()
            sleep(1)
        self.builder.tkvariables.get('testTime').set(str(int(self.testTime)))

    def update_timer(self, timer):
        """
        update timer value in the GUI
        :type timer: int
        :param timer: remaining time to the test
        """
        self.builder.tkvariables.get('testTime').set(str(timer))

    def add_to_packet_dict(self, packets, post_run=False):
        self.process_packets(packets, post_run=post_run)
        
    def process_packets(self, packets, post_run=False):
        for packet in packets:
            packet_raw = packet['raw'].split('(')[1].split(')')[0].strip(' "')
            preamble = packet_raw[:ADV_ADDR_END * NIBS_IN_BYTE]
            self.numOfPackets += 1
                
            if preamble in self.badPreambles:
                continue
            
            elif preamble in self.preamblesDict.keys() and self.preamblesDict[preamble] is not None:
                ext_id = self.preamblesDict[preamble]
                
            else:
                full_data = None
                if self.token is not None:
                    full_data, success = self.get_packet_ext_id(packet, owner=self.owner, post_run=post_run)
                    
                    if not success:
                        if not post_run:
                            self.unknown_packets.append(packet)
                            if preamble not in self.preamblesDict.keys():
                                logger.error(f'Could not get external ID for preamble {preamble} from the cloud - saving data for post process')
                            self.preamblesDict[preamble] = None
                        else:
                            logger.error(f'Could not get external ID for preamble {preamble} from the cloud - dumping packet')
                        continue
                    
                    ext_id = full_data['barcode'] if full_data['barcode'] in self.barcodes_read.keys() else full_data['cur_id']
                    if (ext_id is not None or self.debug_mode is not None)\
                            and ext_id not in self.barcodes_read.keys():
                        logger.info(
                            f'Tag with preamble {preamble} and external ID {full_data["cur_id"]} detected but not belong to the test.')
                        self.badPreambles.append(preamble)
                        continue
                    
                    self.preamblesDict[preamble] = ext_id
                
                    if preamble not in self.barcodes_read[ext_id]['preamble']:
                        logger.info(f'New Tag detected with preamble {preamble} and external ID {full_data["cur_id"]}.')
                        self.barcodes_read[ext_id]['preamble'].append(preamble)
                
            self.barcodes_read[ext_id]['packets'].append(packet)
            self.barcodes_read[ext_id]['packetList'].append(packet['packet'])

            if self.barcodes_read[ext_id]['packetList'].get_statistics()['sprinkler_counter_max'] > 3 and not post_run:
                self.tagsFinished[ext_id] = True

            if len(self.tagsFinished.keys()) >= len(self.barcodes_read.keys()) and not post_run:
                self.closeRequested = True

    def iteration_finished(self, force_finish=False):
        self.testGo = False
        self.handle_unknown_packets()
        avg_tbp, avg_ttfp = self.post_process_iteration()
        self.test_barcodes = dict(list(self.test_barcodes.items()) + list(self.barcodes_read.items())) 
        self.comConnect.open_chambers()
        
        all_answered = all([False for ext_id in self.barcodes_read.values() if len(ext_id['packets']) == 0])
        dup_adva = [extId for extId, tag in self.barcodes_read.items() if len(tag['preamble'])>1]
        adva_warning = len(dup_adva) > 0
        serial_warning = '' if all_answered or len(self.badPreambles)==0 else 'Serialization warning!\n'
        serial_warning = serial_warning if not adva_warning else serial_warning + f'ADVA warning in tags: {dup_adva}\n'
        bg_color = None if all_answered or len(self.badPreambles)==0 else 'yellow'
        bg_color = bg_color if not adva_warning else 'yellow'
        stat = ''
        if avg_ttfp != 0:
            stat = f'Average TTFP: {avg_ttfp:.3f} [sec]\n' + \
                   f'Average TBP: {avg_tbp:.3f} [msec]'
        else:
            stat = 'No packets received'

        self.finish_test()

        # read_tags = ''
        # if self.tagsCount < self.numOfTags and not force_finish:
        read_tags = '\nReplace tags and click on "Read"'
            
        finishThread = Thread(target=popup_message, args=(f'{serial_warning}'
                      f'{stat}'
                      f'{read_tags}',
                      'info',
                      ("Helvetica", 10),
                      'info',
                      bg_color))
        finishThread.start()
        finishThread.join()
        
        # self.builder.tkvariables.get('numTags').set(self.numOfTags - self.tagsCount)
        self.builder.tkvariables.get('numTags').set(len(self.test_barcodes.keys()))
        self.builder.get_object('go')['state'] = 'normal'
        self.builder.get_object('add')['state'] = 'normal'
        self.builder.get_object('remove')['state'] = 'normal'
        self.builder.get_object('addTag')['state'] = 'normal'
        self.builder.tkvariables.get('addTag').set('')
        self.builder.get_object('connect')['state'] = 'normal'
        
        self.builder.tkvariables.get('go').set(READ)
        self.builder.get_object('stop')['state'] = 'normal'
        
        # if self.tagsCount < self.numOfTags and not force_finish:
        self.builder.get_object('stop')['state'] = 'normal'
        self.builder.get_object('forceGo')['state'] = 'normal'
        self.builder.get_object('scanned').delete(0, END)
        self.builder.tkvariables.get('stop').set(FINISH)
        self.stopButtonState = FINISH
        # else:
        #     self.builder.get_object('scanned').delete(0, END)
        #     self.builder.tkvariables.get('stop').set(SEND)
        #     self.stopButtonState = SEND
        #     for barcode in list(self.test_barcodes.keys()):
        #         self.builder.get_object('scanned').insert(END, barcode)
        
        self.barcodes_read = {}
        self.unknown_packets = []
        
    def remove_barcodes(self):
        final_barcodes = self.builder.get_object('scanned').get(0, END)
        self.builder.get_object('scanned').delete(0, END)
        test_barcodes = list(self.test_barcodes.keys()).copy()
        for barcode in test_barcodes:
            if barcode not in final_barcodes:
                self.test_barcodes.pop(barcode)
        
    def finish(self):
        self.remove_barcodes()
        self.finish_test(True, True)
        # self.finishTestThread = Thread(target=self.finish_test, args=([True, True]))
        # self.finishTestThread.start()
        
    def handle_unknown_packets(self):
        if len(self.unknown_packets) > 0 and self.token is not None:
            logger.info(f'Start handling unknown packets.')
            self.process_packets(self.unknown_packets, post_run=True)

    def post_process_iteration(self):
        tbp_count = 0
        ttfp_count = 0
        ttfp_avg = 0
        tbp_avg = 0
        
        for extId, tag in self.barcodes_read.items():
            stat = tag['packetList'].get_statistics()
            if 'ttfp' in stat.keys(): 
                tbp = stat['tbp_mean']
                tbp = tbp if type(tbp).__name__ != 'str' else -1
                if tbp != -1:
                    tbp_avg =  ((tbp_avg*tbp_count)+tbp)/(tbp_count+1)
                    tbp_count += 1
                    
                ttfp = stat['ttfp']
                ttfp_avg = ((ttfp_avg*ttfp_count)+ttfp)/(ttfp_count+1)
                self.barcodes_read[extId]['tbp'] = int(tbp)
                self.barcodes_read[extId]['ttfp'] = ttfp
                
                self.barcodes_read[extId]['rssi'] = int(stat["rssi_mean"])
        
        return tbp_avg, ttfp_avg

    def finish_test(self, post_data=False, reset_tester=False, post_process=True):
        if post_process:
            pass_barcodes = self.post_process()
            
            dup_adva = [extId for extId, tag in self.test_barcodes.items() if len(tag['preamble'])>1]
    
            pass_fail = ((len(pass_barcodes) / len(self.test_barcodes.keys())) * 100) >= \
                        int(self.params['respondingMu'])
            all_answered = all([False for ext_id in self.test_barcodes.values() if len(ext_id['packets']) == 0])
            serial_warning = (not all_answered) and len(self.totalBadPreambles)!=0
            adva_warning = len(dup_adva) > 0
            serial_warning = '' if not serial_warning else 'Serialization warning!\n'
            serial_warning = serial_warning if not adva_warning else serial_warning + f'ADVA warning in tags: {dup_adva}\n'
            bg_color = 'green' if not (serial_warning or adva_warning) else 'yellow'
            bg_color = bg_color if pass_fail else 'red'
            pass_fail = 'Passed' if pass_fail else 'Failed'
    
            self.files_and_cloud(post_data)
            
        if reset_tester and post_process:
            popup_message(f'Test {self.common_run_name} has {pass_fail}\n' +
                          f'{serial_warning}' +
                          f'Average TTFP: {self.dataBaseDict["ttfpAvg"]} [sec]\n' +
                          f'Average TBP: {self.dataBaseDict["tbpAvg"]} [msec]\n' +
                          f'STD TBP: {self.dataBaseDict["tbpStd"]} [msec]\n' +
                          f'Yield: {self.dataBaseDict["responding[%]"]}', title='Finished test', bg=bg_color, log='info')

        if reset_tester:
            # self.tagsCount = 0
            self.builder.get_object('reelId').bind("<Key>", self.reelId)
            self.builder.tkvariables.get('numTags').set(0)
            self.builder.tkvariables.get('go').set(READ)
            self.testFinished = True
            self.packets_dict = {}
            self.test_barcodes = {}
            self.barcodes_read = {}
            self.reel_id = ''
            self.gtin = ''
            self.builder.tkvariables.get('reelId').set('')
            
            changeFileHandler(logger, default_log_file, file_mode='a+', append_handler=True)
            logger.info(f'Test {self.common_run_name} ended.')
            removeFileHandler(logger, self.test_log_file)
            self.update_params_state(state='normal', group=READ)
            self.builder.tkvariables.get('stop').set(STOP)
            self.builder.get_object('stop')['state'] = 'disabled'

    def files_and_cloud(self, post_data=False):
        self.runDataDict['runEndTime'] = self.dataBaseDict['runEndTime'] = time.strftime('%d/%m/%y %H:%M:%S')

        run_data_path = abspath(join(OUTPUT_DIR, self.testName, self.testDir, f'{self.common_run_name}@run_data.csv'))
        if exists(run_data_path):
            remove(run_data_path)
        run_csv = CsvLog(HeaderType.RUN, run_data_path, tester_type=TesterName.SAMPLE)
        run_csv.open_csv()
        run_csv.append_dict_as_row([self.runDataDict])


        tags_data_path = abspath(join(OUTPUT_DIR, self.testName, self.testDir, f'{self.common_run_name}@packets_data.csv'))
        if exists(tags_data_path):
            remove(tags_data_path)
        packets_csv = CsvLog(HeaderType.PACKETS, tags_data_path, tester_type=TesterName.SAMPLE)
        packets_csv.open_csv()
        
        for extId, data in self.test_barcodes.items():
            if data['packetList'].packet_list.size > 0:
                for sprinkler in data['packetList'].packet_list:
                    for i in range(sprinkler.gw_data['gw_packet'].size):
                        if sprinkler.gw_data["time_from_start"].size > 1:
                            # print(f'commonRunName: {self.common_run_name}, encryptedPacket: {sprinkler.get_packet_string(i)}, time: {sprinkler.gw_data["time_from_start"][i]}, externalId: {extId}')
                            tag_row = {'commonRunName': self.common_run_name,
                                       'encryptedPacket': sprinkler.get_packet_string(i),
                                       'time': sprinkler.gw_data["time_from_start"][i],
                                       'externalId': extId}
                        else:
                            # print(f'commonRunName: {self.common_run_name}, encryptedPacket: {sprinkler.get_packet_string(i)}, time: {sprinkler.gw_data["time_from_start"].item()}, externalId: {extId}')
                            tag_row = {'commonRunName': self.common_run_name,
                                       'encryptedPacket': sprinkler.get_packet_string(i),
                                       'time': sprinkler.gw_data["time_from_start"].item(),
                                       'externalId': extId}
                            
                        packets_csv.append_dict_as_row([tag_row])


            
        with open(join(OUTPUT_DIR, self.testName, self.testDir, f'{self.common_run_name}@configs_data.csv'),\
                  'w+', newline='') as newCsv:
            # writer = csv.DictWriter(newCsv, fieldnames=CSV_DATABASE_COLUMNS)
            writer = csv.DictWriter(newCsv, fieldnames=self.dataBaseDict.keys())
            writer.writeheader()
            writer.writerows([self.dataBaseDict])

        with open(join(OUTPUT_DIR, self.testName, self.testDir, f'{self.common_run_name}@tags_data.csv'),\
                  'w+', newline='') as newCsv:
            ids_dict = self.test_barcodes
            tags = []
            for extId, tag in ids_dict.items():
                temp_dict = {}
                temp_dict['chamber'] = tag['chamber']
                temp_dict['reel'] = tag['reel']
                temp_dict['ext_id'] = extId
                temp_dict['ttfp'] = tag['ttfp']
                temp_dict['tbp'] = tag['tbp']
                temp_dict['preamble'] = tag['preamble']                    
                temp_dict['state(tbp_exists:0,no_tbp:-1,no_ttfp:-2,dup_preamble:-3)'] = \
                                                                        -3 if len(temp_dict['preamble'])>1 else \
                                                                        -2 if temp_dict['ttfp'] == -1 else \
                                                                        -1 if temp_dict['tbp'] == -1 else \
                                                                        0
                temp_dict['testName'] = self.testName
                temp_dict['rssi'] = tag['rssi']
                    
                tags.append(temp_dict)
            
            writer = csv.DictWriter(newCsv, fieldnames=tags[0].keys())
            writer.writeheader()
            writer.writerows(tags)
            
        if post_data and self.post_data:
            post_run_success = self.post_to_cloud(run_data_path, destination='runs-indicators', environment=self.environment)
            if post_run_success:
                post_tags_success = self.post_to_cloud(tags_data_path, destination='packets-indicators', environment=self.environment)
                if not post_tags_success:
                    popup_message(f'Failed uploading tags data, Upload manually:\n' +
                                  f'{self.common_run_name}@packets_data.csv.', log='warning')
            else:
                popup_message(f'Failed uploading run and tags data, Upload manually:\n' +
                              f'{self.common_run_name}@run_data.csv\n' +
                              f'{self.common_run_name}@packets_data.csv', log='warning')
            

    def get_packet_ext_id(self, packet, owner='wiliotmnf', environment='', post_run=False):
        """
        get external ID of a tag by sending an example packet to the cloud.
        :type packet: dict
        :param packet: contains the raw and time of the packet.
        :type owner: string
        :param owner: owner of the tag (wiliot, wiliotmnf, wiliot-ops).
        :return: external ID of the tag, and the external ID parsed when it's wiliot tag.
        """
        if not self.check_token(self.token, log=False):
            logger.error('Token has expired.')
            self.popup_login() 
            
        packet_time = packet['time']
        packet_raw = packet['raw'].split('(')[1].split(')')[0].strip(' "')
        packet_payload = packet_raw[PAYLOAD_START * NIBS_IN_BYTE:]
        packet_payload = packet_payload[: CRC_START * NIBS_IN_BYTE]

        payload = '{\"gatewayType\":\"Manufacturing\",\"gatewayId\":\"manufacturing-gateway-id\",\"timestamp\":'\
                  + str(time.time())\
                  + ',\"packets\":[{\"timestamp\":'\
                  + str(packet_time * (10 ** 6))\
                  + ',\"payload\":\"'\
                  + packet_payload\
                  + '\"}]}'

        headers = {
            'accept': "application/json",
            'authorization': "Bearer " + self.token['access_token'] + "",
            'content-type': "application/json"
        }

        url = f'https://api.wiliot.com/{environment}v1/owner/{owner}/resolve'
        
        full_data = {'barcode': None, 'cur_id': None, 'reel_id': None, 'gtin': None}
        data = {}
        success = False
        first_iter = True
        
        while not success:
            if not first_iter:
                popup_yes_no(f'Could not get external ID from the cloud, try again?')
            try:
                response = requests.request("POST", url, headers=headers, data=payload,
                                            timeout=CLOUD_TIMEOUT_RESOLVE)
                data = loads(response.text)
                if 'data' not in data.keys() or 'externalId' not in data['data'][0].keys():
                    raise
                success = True
            except:
                first_iter = False
            
            if not post_run:
                break
        
        if 'data' in data.keys() and 'externalId' in data['data'][0].keys():
            if data['data'][0]['externalId'] != 'unknown':
                full_data['barcode'] = data['data'][0]['externalId']
                full_data['cur_id'] = full_data['reel_id'] = full_data['gtin'] = full_data['barcode']
                try:
                    tag_data = full_data['barcode'].split(')')[2]
                    full_data['gtin'] = ')'.join(full_data['barcode'].split(')')[:2]) + ')'
                    full_data['cur_id'] = tag_data.split('T')[1].strip("' ")
                    full_data['reel_id'] = tag_data.split('T')[0].strip("' ")
                except:
                    pass
        return full_data, success
    

    def post_to_cloud(self, file_path, destination, environment='test/'):
        """
        post file to the cloud
        :type file_path: string
        :param file_path: the path to the uploaded file
        :type destination: string
        :param destination: the destination in the cloud (runs-indicators, packets-indicators)
        :type environment: string
        :param environment: the environment in the cloud (dev, test, prod, etc.)
        :return: bool - True if succeeded, False otherwise
        """
        success = False
        first_iter = True
        while not success:
            if not first_iter:
                try_again = popup_yes_no(f'Could not post data to cloud, try again?')
                if not try_again:
                    return False
                
            success = self.post_request(file_path, destination, environment)
            first_iter = False
            
        return success
        
    def post_request(self, file_path, destination, environment='test/'):
        """
        post file to the cloud
        :type file_path: string
        :param file_path: the path to the uploaded file
        :type destination: string
        :param destination: the destination in the cloud (runs-indicators, packets-indicators)
        :type environment: string
        :param environment: the environment in the cloud (dev, test, prod, etc.)
        :return: bool - True if succeeded, False otherwise
        """
        try:
            if self.token is not None:
                
                if not self.check_token(self.token, log=False):
                    logger.error('Token has expired.')
                    self.popup_login()
                
                url = f'https://api.wiliot.com/{environment}' \
                      f'v1/manufacturing/upload/testerslogs/sample-test/{destination}'
                payload = {}
                files = [
                  ('file', (basename(file_path), open(file_path, 'rb'), 'text/csv'))
                ]
                headers = {
                  'Authorization': f"Bearer {self.token['access_token']}"
                }
                response = requests.request("POST", url, headers=headers, data=payload, files=files,
                                            timeout=CLOUD_TIMEOUT_POST)
                logger.info(response.text)
                data = loads(response.text)
                if 'data' not in data.keys() or 'success' not in data['data']:
                    post_state = False
                post_state = True
                return post_state
        except:
            return False

    def post_process(self):
        tbp_arr = [tag['tbp'] for extId,tag in self.test_barcodes.items() if tag['tbp'] != -1]
        ttfp_arr = [tag['ttfp'] for extId,tag in self.test_barcodes.items() if tag['ttfp'] != -1]
        rssi_arr = [tag['rssi'] for extId,tag in self.test_barcodes.items() if tag['rssi'] != -1]
        
        pass_barcodes = [extId for extId,tag in self.test_barcodes.items() if tag['tbp'] != -1]
        tested_barcodes = len(self.test_barcodes.keys())
        num_of_answered = len(pass_barcodes)
        self.dataBaseDict['packets'] = self.numOfPackets
        self.dataBaseDict['tested'] = self.runDataDict['tested'] = tested_barcodes
        self.dataBaseDict['passed'] = self.runDataDict['passed'] = num_of_answered
        self.dataBaseDict['responding[%]'] = self.runDataDict['yield'] = f'{int((num_of_answered/tested_barcodes)*100)}%'

        avg_ttfp = sum(ttfp_arr) / len(ttfp_arr) if len(ttfp_arr) > 0 else -1
        ttfp_arr = ttfp_arr if len(ttfp_arr) > 0 else [-1]
        
        self.dataBaseDict['ttfpStd'] = f'{numpy.std(ttfp_arr):.3f}'
        self.runDataDict['ttfpAvg'] = self.dataBaseDict['ttfpAvg'] = f'{avg_ttfp:.3f}'
        self.dataBaseDict['ttfpMin'] = f'{min(ttfp_arr):.3f}'
        self.runDataDict['maxTtfp'] = self.dataBaseDict['ttfpMax'] = f'{max(ttfp_arr):.3f}'
        # self.dataBaseDict['ttfpMax'] = f'{max(ttfp_arr):.3f}'

        avg_tbp = sum(tbp_arr) / len(tbp_arr) if len(tbp_arr) > 0 else -1
        tbp_arr = tbp_arr if len(tbp_arr) > 0 else [-1]
            
        self.dataBaseDict['tbpStd'] = f'{numpy.std(tbp_arr):.3f}'
        self.runDataDict['tbpAvg'] = self.dataBaseDict['tbpAvg'] = f'{avg_tbp:.3f}'
        self.dataBaseDict['tbpMin'] = f'{min(tbp_arr):.3f}'
        self.dataBaseDict['tbpMax'] = f'{max(tbp_arr):.3f}'
        
        avg_rssi = sum(rssi_arr) / len(rssi_arr) if len(rssi_arr) > 0 else -1
        rssi_arr = rssi_arr if len(rssi_arr) > 0 else [-1]
        
        self.runDataDict['rssiAvg'] = self.dataBaseDict['rssiAvg'] = str(avg_rssi)
                
        return pass_barcodes

    def reset(self):
        """
        reset the tester (fully available only when running from bat file)
        """
        if popup_yes_no(f'Reset Sample test?'):
            self.ttk.destroy()
            _exit(1)
        else:
            pass

    def close(self):
        """
        close the gui and destroy the test
        """
        self.ttk.destroy()
        _exit(0)

    def update_data(self):
        """
        update station name and owner in json file, for future usage.
        """
        # temp_coms = {}
        # if isfile(join(CONFIGS_DIR, '.defaults.json')):
        #     with open(join(CONFIGS_DIR, '.defaults.json'), 'r') as defaultComs:
        #         temp_coms = load(defaultComs)
        # temp_coms.update(self.defaultDict)
        temp_coms = self.comConnect.get_default_dict()
        if self.station_name.strip() != '':
            temp_coms['stationName'] = self.station_name
        if self.owner.strip() != '':
            temp_coms['owner'] = self.owner
        if self.testConfig != '':
            temp_coms['config'] = self.testConfig
        if self.calib:
            temp_coms[f'{self.antenna}_calib'] = {'low': self.low, 'high': self.high, 'step': self.step}
            
        with open(join(CONFIGS_DIR, '.defaults.json'), 'w+') as defaultComs:
            dump(temp_coms, defaultComs, indent=4)

    def popup_login(self):
        """
        popup to insert fusion auth credentials, and choosing owner.
        """
        default_font = ("Helvetica", 10)
        popup = Tk()
        popup.eval('tk::PlaceWindow . center')
        popup.wm_title('Login')

        def quit_tester():
            popup.destroy()
            _exit(0)

        popup.protocol("WM_DELETE_WINDOW", quit_tester)

        def update_owner():
            owners = list(self.claimSet['owners'].keys())
            c1['values'] = owners
            c1['state'] = 'normal'
            if 'owner' in self.defaultDict.keys() and self.defaultDict['owner'] in owners:
                def_owner = self.defaultDict['owner']
            else:
                def_owner = owners[0]
            c1.set(def_owner)
            b3['state'] = 'active'

        def login():
            logger.info('Requesting token...')
            username = e1.get()
            password = e2.get()
            if username.strip() != '' and password.strip() != '':
                environ['FUSION_AUTH_USER'] = username
                environ['FUSION_AUTH_PASSWORD'] = password
                # logger.info(username)
                # logger.info(password)
            self.get_token()
            if self.token is not None:
                update_owner()
            # popup.destroy()

        def ok():
            self.owner = c1.get()
            self.station_name = e3.get()
            popup.destroy()

        if self.token is None:
            l1 = Label(popup, text='Enter FusionAuth User-Name and Password:', font=default_font)
            l1.grid(row=2, column=0, padx=10, pady=10, columnspan=3)
            l2 = Label(popup, text='Username:', font=default_font)
            l2.grid(row=3, column=0, padx=10, pady=10)
            e1 = Entry(popup)
            e1.grid(row=3, column=1, padx=10, pady=5)
            l3 = Label(popup, text='Password:', font=default_font)
            l3.grid(row=4, column=0, padx=10, pady=10)
            e2 = Entry(popup, show='*')
            e2.grid(row=4, column=1, padx=10, pady=5)
            b1 = Button(popup, text="Quit", command=quit_tester, height=1, width=10)
            b1.grid(row=5, column=0, padx=10, pady=10)
            b2 = Button(popup, text="Login", command=login, height=1, width=10)
            b2.grid(row=5, column=2, padx=10, pady=10)
        else:
            l1 = Label(popup, text='Choose owner and station name:', font=default_font)
            l1.grid(row=2, column=0, padx=10, pady=10, columnspan=3)
        l4 = Label(popup, text='Owner:', font=default_font)
        l4.grid(row=6, column=0, padx=10, pady=10)
        c1 = ttk.Combobox(popup, state='disabled')
        c1.grid(row=6, column=1, padx=10, pady=15)
        l5 = Label(popup, text='Station Name:', font=default_font)
        l5.grid(row=7, column=0, padx=10, pady=10)
        e3 = Entry(popup)
        if 'stationName' in self.defaultDict.keys():
            e3.insert(0, self.defaultDict['stationName'])
        e3.grid(row=7, column=1, padx=10, pady=5)
        b3 = Button(popup, text="OK", command=ok, height=1, width=10)
        b3.grid(row=8, column=1, padx=10, pady=10)

        if self.claimSet is not None:
            update_owner()

        popup.mainloop()

    def get_token(self):
        """
        get new token using username and password stored in environment variables
        :return: the new token
        """
        try:
            username = environ.get('FUSION_AUTH_USER')
            username = quote(username)
            password = environ.get('FUSION_AUTH_PASSWORD')
            password = quote(password)
            
            headers = {'accept': "application/json"}
            url = f'https://api.wiliot.com/v1/auth/token?password={password}&username={username}'
            
            response = requests.request("POST", url, headers=headers,timeout=CLOUD_TIMEOUT_POST)
            tokens = loads(response.text)
            
            if 'access_token' not in tokens.keys() and 'error' in tokens.keys():
                popup_message(f'Error requesting token:\n{tokens["error_description"]}', title='Error', log='error')
                
            self.token = token = tokens
            self.claimSet = jwt.decode(token['access_token'], options={"verify_signature": False})
            self.save_token(tokens)
            logger.info('Token received successfully.')
        except:
            self.token = None
            logger.error('Could not generate token, check username and password.')
            token = None
        return token

    def check_token(self, token=None, log=True):
        """
        upload the last token from pickle file, check its status
        if the token is outdated and the refresh token still alive, refresh the token.
        """
        if token is None:
            if isfile(join(CONFIGS_DIR, TOKEN_FILE_NANE)):
                f = open(join(CONFIGS_DIR, TOKEN_FILE_NANE), "rb")
                token = pickle.load(f)
                f.close()
                
        if token is not None and 'access_token' not in token.keys():
            return False
            
        if token is not None and (datetime.datetime.now() - token['issue_date']).days < 1\
                and (datetime.datetime.now() - token['issue_date']).seconds < 6 * 60 * 60:
            self.token = token
            self.claimSet = jwt.decode(token['access_token'], options={"verify_signature": False})
            if log:
                logger.info('Token loaded successfully.')
            return True
        elif token is not None and (datetime.datetime.now() - token['issue_date']).days < 7:
            self.refresh_token(token['refresh_token'])
            return True
        else:
            return False

    def refresh_token(self, refresh_token):
        """
        refresh the token if the token is less than week old.
        :type refresh_token: string
        :param refresh_token: the refresh token of the last token generated.
        :return: the new token
        """
        try:
            headers = {'accept': "application/json"}
            url = f'https://api.wiliot.com/v1/auth/refresh?refresh_token={refresh_token}'
            
            response = requests.request("POST", url, headers=headers,timeout=CLOUD_TIMEOUT_POST)
            
            tokens = loads(response.text)
            
            if 'access_token' not in tokens.keys() and 'error' in tokens.keys():
                popup_message(f'Error refreshing token:\n{tokens["error_description"]}', title='Error', log='error')
            
            self.save_token(tokens)
            # logger.info(tokens)
            self.token = token = tokens
            self.claimSet = jwt.decode(token['access_token'], options={"verify_signature": False})
            logger.info('Token refreshed successfully.')
            # logger.info(token)
        except:
            # print_exc()
            self.token = None
            logger.info('Could not refresh token.')
            token = None
        return token

    def save_token(self, token):
        token['issue_date'] = datetime.datetime.now()
        pickle.dump(token, open(join(CONFIGS_DIR, TOKEN_FILE_NANE), "wb"))

    def popup_calib(self):
        """
        popup to choose calib mode parameters
        """
        default_font = ("Helvetica", 10)
        popup = Tk()
        popup.eval('tk::PlaceWindow . center')
        popup.wm_title('Login')
        
        # defaultDict = {}
        # if isfile(join(CONFIGS_DIR, '.defaults.json')):
        #     with open(join(CONFIGS_DIR, '.defaults.json'), 'r') as defaultComs:
        #         defaultDict = load(defaultComs)
    
        def quit_calib():
            popup.destroy()
            
        popup.protocol("WM_DELETE_WINDOW", quit_calib)
    
        def ok():
            # global low, high, step
            self.low = e2.get()
            self.high = e3.get()
            self.step = e4.get()
            popup.destroy()
            
        def update_antenna_params(*args):
            self.antenna = antenna = c2.get().lower()
            if f'{antenna}_calib' in self.defaultDict.keys():
                antennaDict = self.defaultDict[f'{antenna}_calib']
                e2.delete(0,END)
                e3.delete(0,END)
                e4.delete(0,END)
                e2.insert(0,antennaDict['low'])
                e3.insert(0,antennaDict['high'])
                e4.insert(0,antennaDict['step'])
                
        l1 = Label(popup, text='Enter calibration parameters:', font=default_font)
        l1.grid(row=1, column=0, padx=10, pady=10, columnspan=3)
        l2 = Label(popup, text='Antenna Type:', font=default_font)
        l2.grid(row=2, column=0, padx=10, pady=10)
        c2 = ttk.Combobox(popup, values=['BLE', 'LoRa'])
        c2.grid(row=2, column=1, padx=10, pady=10)
        c2.bind("<FocusOut>", update_antenna_params)
        c2.bind("<<ComboboxSelected>>", update_antenna_params)
        l3 = Label(popup, text='Low value:', font=default_font)
        l3.grid(row=3, column=0, padx=10, pady=10)
        e2 = Entry(popup)
        e2.grid(row=3, column=1, padx=10, pady=5)
        l4 = Label(popup, text='High value:', font=default_font)
        l4.grid(row=4, column=0, padx=10, pady=10)
        e3 = Entry(popup)
        e3.grid(row=4, column=1, padx=10, pady=5)
        l5 = Label(popup, text='Step:', font=default_font)
        l5.grid(row=5, column=0, padx=10, pady=10)
        e4 = Entry(popup)
        e4.grid(row=5, column=1, padx=10, pady=5)
        b1 = Button(popup, text="Quit", command=quit_calib, height=1, width=10)
        b1.grid(row=6, column=0, padx=10, pady=10)
        b2 = Button(popup, text="Ok", command=ok, height=1, width=10)
        b2.grid(row=6, column=2, padx=10, pady=10)
    
        popup.mainloop()
        
        # return antenna, low, high, step


def popup_yes_no(question):
    root = Tk()
    root.wm_withdraw()
    result = messagebox.askquestion("Sample Test", question, icon='warning')
    root.destroy()
    if result == 'yes':
        return True
    else:
        return False


def float_precision(num, prec=2):
    dot_pos = str(num).index('.')
    first_idx = [i for i in range(len(str(num))) if str(num)[i] != '0' and str(num)[i] != '.']
    first_idx = first_idx[0] if first_idx[0] > 0 else first_idx[0] + 1
    after_dot = first_idx - dot_pos + prec
    if after_dot > 0:
        eval_str = '{:.%sf}' % (str(first_idx - dot_pos + prec))
    else:
        eval_str = '{:.0f}'
    return float(eval_str.format(num))


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Run PixieParser')
    parser.add_argument('-d', '--debug', action='store_true', default='False', help='Debug mode')
    parser.add_argument('-c', '--calib', help='Calibration mode', action='store_true')
    # parser.add_argument('-a', '--antenna', help='Calibration mode, attenuator type', default='')
    # parser.add_argument('-low', '--low', help='lower value of attenuation')
    # parser.add_argument('-high', '--high', help='higher value of attenuation')
    # parser.add_argument('-step', '--step', help='attenuation step')
    parser.add_argument('-e', '--environment', help='Environment: test or not', default='')
    parser.add_argument('-p', '--post_data', help='Post data to the cloud', default='True')
    args = parser.parse_args()
    calib = args.calib
    # antenna = args.antenna.lower()
    # low = args.low
    # high = args.high
    # step = args.step
    post_data = False if args.post_data.lower() == 'false' else True
    # if calib and (args.antenna == '' or low is None or high is None or step is None):
    #     try:
    #         popup_calib()
    #         if antenna not in ['ble', 'lora']:
    #             raise SampleException('Unknown Antenna')
    #         int(low)
    #         int(high)
    #         float(step)
    #     except:
    #         logger.info('Warning - Missing values for calibration mode. Switching to test mode.')
    #         calib = False
    #         antenna = low = high = step = ''
        
    # Run the UI
    if calib:
        logger.warning(f'Sample Test - calibration mode active.')
    app_folder = abspath(join(dirname(__file__), '..'))
    try:
        sampleTest = SampleTest(debug_mode=args.debug, calib=calib, environment=args.environment, post_data=post_data)
        sampleTest.gui()
    except BaseException:
        print_exc()
    sys.exit(0)
