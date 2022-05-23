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
     nor are you named on the U.S. Treasury Department’s list of Specially Designated
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
from datetime import datetime

import numpy as np
import pandas as pd
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import socket
import pyqtgraph as pg
from queue import Queue
from wiliot.gateway_api.gateway import *
from wiliot.wiliot_testers.test_equipment import BarcodeScanner
from wiliot.wiliot_testers.tester_utils import *
from wiliot.wiliot_testers.offline.offline_utils import *

import time
import os
import threading
import json
from datetime import timedelta
from wiliot.get_version import get_version
import copy
from numpy import mean
import pandas
import traceback

# a global variable which will be in the log_file name that says the R2R code version
R2R_code_version = '13'
# running parameters
tested = 0
passed = 0
under_threshold = 0
missing_labels = 0
black_list_size = 0
last_pass_string = 'No tag has passed yet :('

desired_pass_num = 999999999  # this will be set to the desired pass that we want to stop after
desired_tags_num = 999999999  # this will be set to the desired tags that we want to stop after
reel_name = ''
common_run_name = ''
log_path = ''
run_data_path = ''
tags_data_path = ''
debug_tags_data_path = ''
packets_data_path = ''
is_debug_mode = True
debug_tags_data_log = None
packets_data_log = None
tags_data_log = None
run_data_log = None
temperature_sensor_enable = False
problem_in_locations_hist = None
run_data_list = []
run_data_dict = {}
run_start_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
failed_tags = None  # tags that failed in serialization (updated at the end of the run)
qr_que_list = []
external_id_for_printer = 999999999
yield_over_time = 0
calculate_interval = 10
calculate_on = 50

lock_print = threading.Lock()


class QRThread(threading.Thread):
    def __init__(self, events, ports_and_guis):
        """
        Initialize Constants
        """
        super(QRThread, self).__init__(daemon=True)
        self.exception_queue = Queue()
        self.events = events
        self.ports_and_guis = ports_and_guis
        self.qr_enable = self.ports_and_guis.Tag_Value['QRRead']
        self.qr_comport = self.ports_and_guis.Tag_Value['QRcomport']
        self.qr_max_bad_tags = int(self.ports_and_guis.Tag_Value['maxQRWrongTags'])

        try:
            if self.Tag_Value['printingFormat'] == 'Test' or self.Tag_Value['printingFormat'] == 'SGTIN':
                self.sgtin_num = self.ports_and_guis.Tag_Printing_Value['stringBeforeCounter']
                self.reel_num = self.sgtin_num[-4:]
        except Exception:
            self.reel_num = '0000'
        self.scanner = BarcodeScanner(com=self.qr_comport)
        self.read_out_attempts = 2
        self.failed_qr_list = []
        self.max_wrong_readouts = 3

        # ('(01)00850027865010(21)001jT2766', '2766', '001j', '(01)00850027865010(21)') #output from QR scan
        # scanner.scan_ext_id() #command to start scanning

    @pyqtSlot()
    def run(self):
        """
        runs the thread
        """
        global qr_que_list
        die = False

        while not die:
            try:
                self.events.start_qr_scan.wait()  # Wait for QR scan flag
                self.tag_comparted = qr_que_list.pop(0)  # Pop from tested tags the last value
                self.events.start_qr_scan.clear()  # Clear the QR scan flag to avoid overwrite the last tested value pop
                scan_compare = True
                retry_scan = True
                qr_fail = False
                fail_read = False
                while scan_compare:
                    sleep(0.3)
                    self.qr_tag = self.scanner.scan_ext_id()  # Scan the QR

                    if self.qr_tag[1] is None:
                        if self.tag_comparted['status'] == 'Fail':
                            msg = 'Compare of tag: {} was successful - tag is fail'.format(
                                str(self.tag_comparted['externalID']))
                            printing_func(msg, 'QRThread', lock_print, logger_type='debug')
                            self.events.qr_read_success.set()
                            scan_compare = False
                            break

                        else:
                            msg = 'Comparing went wrong, QR scanned failed tag while first list value is: {}, Trying to scan again'.format(
                                self.tag_comparted['externalID'])
                            printing_func(msg, 'QRThread', lock_print, logger_type='warning')
                            self.failed_qr_list.append(self.tag_comparted['externalID'])
                            qr_fail = True
                            fail_read = True

                    # if self.qr_tag[1] is not None: #able to read
                    else:
                        if str(self.reel_num) != str(
                                self.qr_tag[2]):  # check if reel_num is equal to check printing quality
                            if str(self.reel_num) != '0000':  # check if its in 'no print' mode
                                msg = 'Printing went wrong - reel number is unreadable'
                                printing_func(msg, 'QRThread', lock_print, logger_type='warning')
                                qr_fail = True

                        if self.tag_comparted['status'] == 'Pass':
                            if self.tag_comparted['externalID'][-4:] == self.qr_tag[1]:
                                msg = 'Compare of tag: {} was successful'.format(str(self.tag_comparted['externalID']))
                                printing_func(msg, 'QRThread', lock_print, logger_type='debug')
                                self.events.qr_read_success.set()
                                scan_compare = False
                                break

                            else:
                                msg = 'Comparing went wrong, QR read: {} and trying to compare it to {}, Trying to scan again'.format(
                                    self.qr_tag[1], self.tag_comparted['externalID'][-4:])
                                printing_func(msg, 'QRThread', lock_print, logger_type='warning')
                                qr_fail = True

                        else:
                            msg = 'QR reader read the value: {} but the value compared is fail, trying to scan again'.format(
                                self.qr_tag[1])
                            printing_func(msg, 'QRThread', lock_print, logger_type='warning')
                            qr_fail = True

                    if retry_scan and qr_fail:
                        for qr_attemp_number in range(self.read_out_attempts):
                            print('in for loop for the {} time'.format(str(qr_attemp_number)))
                            self.temp_qr = self.qr_tag
                            self.qr_tag = self.scanner.scan_ext_id()
                            sleep(0.05)
                            retry_scan = False
                            if self.temp_qr[1] == self.qr_tag[1]:
                                qr_fail = True
                                retry_scan = False
                            else:
                                msg = 'New scan detected - Good QR readout'
                                printing_func(msg, 'QRThread', lock_print, logger_type='warning')
                                scan_compare = True
                                retry_scan = False
                                qr_fail = False
                                break

                    if qr_fail and not retry_scan and not fail_read:
                        msg = 'QR Scan was failed, please check printed values'
                        printing_func(msg, 'QRThread', lock_print, logger_type='warning')
                        scan_compare = False
                        die = True

                    if fail_read and qr_fail and not retry_scan:
                        msg = 'QR Scanner wasnt able to detect the QR code for tag: {}, please check if tag print was ok'
                        printing_func(msg, 'QRThread', lock_print, logger_type='warning')
                        self.events.qr_read_success.set()
                        scan_compare = False
                        break

                    if len(self.failed_qr_list) > self.qr_max_bad_tags:
                        die = True
                        logging.warning('Maximum wrong QR readouts reached - Run will pause')
                        break


            except Exception:
                msg = 'Pausing run because comparing went wrong with exception'
                printing_func(msg, 'QRThread', lock_print, logger_type='warning')
                exception_details = sys.exc_info()
                self.exception_queue.put(exception_details)
                self.events.stop_to_r2r_thread.set()  # to avoid from the run to continue printing in this case
                self.events.pause_to_tag_thread.set()
                # MainWindow.pause_fn()

        if die:
            msg = 'Pausing run because comparing went wrong'
            printing_func(msg, 'QRThread', lock_print, logger_type='warning')
            self.events.pause_to_tag_thread.set()
            self.events.stop_to_r2r_thread.set()


class Printer(threading.Thread):
    """
    thread that turns printer on, checks that the print was successful after every tag,

    Parameters:
    @type start_value: int
    @param start_value: first external ID to print on first tag
    @type pass_job_name: str
    @param pass_job_name: the printer pass job name
    @type events: class MainEvents (costume made class that has all of the Events of the program threads)
    @param events: has all of the Events of the program threads
    @type ports_and_guis: class PortsAndGuis (costume made class that has all of the ports and gui inputs for the
                        program threads)
    @param ports_and_guis: has all of the ports and gui inputs for the program threads

    Exceptions:
    @except PrinterNeedsResetException: means that we need to close the program:
            'The printer initialization process has failed in command:...',
            'Printer failed to switch to running mode',
            'The printer over-all-state is Shutdown',
            'The printer over-all-state is Starting up',
            'The printer over-all-state is Shutting down',
            'The printer over-all-state is Offline',
            'reopen_sock() failed'
    @except Exception: operate according to the description:
            'The printer error-state is Warnings present',
            'The printer error-state is Faults present',
            'The printer printed Fail to the previous tag',
            'The printer have not printed on the last tag'

    Events:
        listen/ waits on:
            events.r2r_ready_or_done2tag    => user pressed Stop (end the program)
            events.done_to_printer_thread             => user pressed Stop (end the program) - to avoid deadlock
            events.cont_to_printer_thread             => continue was pressed by user
            events.r2r_ready                => printing was made
            events.was_pass_to_printer      => the last printing was pass
        sets:
            events.printer_error            => the last print was not successful, will cause pause to this run
                                                (and will trigger exception according to the situation)
            events.printer_success          => the last print was successful

    Logging:
        the logging from this thread will be also to logging.debug()
    """

    def __init__(self, start_value, pass_job_name, events, ports_and_guis):
        """
        Initialize Constants
        """
        super(Printer, self).__init__()
        try:
            self.ports_and_guis = ports_and_guis
            self.TCP_BUFFER = self.ports_and_guis.configs_for_printer_values['TCP_BUFFER']
            self.job_name = ''
            self.line_number = ''
            self.sgtin = 'sgtin'
            self.reel_num = 'reel_num'
            self.first_tag_counter = 'tag_number'
            self.pass_counter = 0
            self.fail_counter = 0
            self.printer_response_timeout = 1.5  # time in seconds for printer to answer with updated printing value
            self.timer_is_done = False
            self.exception_queue = Queue()
            self.printing_format = self.ports_and_guis.Tag_Value['printingFormat']
            self.roll_sgtin = self.ports_and_guis.Tag_Printing_Value['stringBeforeCounter']
            self.events = events
            self.r2r_ready_or_done2tag_or_done_to_printer_thread = or_event_set(events.r2r_ready_or_done2tag,
                                                                                events.done_to_printer_thread)
            self.start_value = start_value
            self.cur_value = 0
            self.pass_job_name = pass_job_name
            self.fail_job_name = self.ports_and_guis.Tag_Printing_Value['failJobName']

            # open the socket & config the printer
            self.initialization()

        except Exception:
            exception_details = sys.exc_info()
            self.exception_queue.put(exception_details)

    def initialization(self, use_current_value=False):
        """
        Initialize Constants and socket
        @param use_current_value: will indicate that this is not the first initialization at this run
                                    (make the next print to continue from the last printed value)
        """
        try:
            cmds = []
            self.ports_and_guis.open_printer_socket()  # will open and connect the socket
            self.set_printer_to_running()
            # after printer crash - make sure the continue will be from a the old counter
            if use_current_value:
                global external_id_for_printer
                config_start_value = external_id_for_printer
            else:
                config_start_value = self.start_value
            # initialization protocol
            if self.printing_format == 'Test':
                cmds = ['CAF\r\n', 'CQI\r\n', 'CLN|1|\r\n', 'CLN|2|\r\n',
                        'LAS|' + str(self.pass_job_name) + '|2|' + str(self.sgtin) + '=' +
                        str(self.roll_sgtin[:18]) + '|' + str(self.reel_num) + '=' + str(self.roll_sgtin[18:26]) +
                        'T' + '|' + str(self.first_tag_counter) + '=' + str(config_start_value) + '|\r\n']
                if self.fail_job_name == self.pass_job_name:
                    cmds.append('LAS|' + str(self.fail_job_name) + '|1|' + str(self.sgtin) + '=' +
                                str(self.roll_sgtin[:18]) + '|' + str(self.reel_num) + '=' +
                                str(self.roll_sgtin[18:26]) + 'T' + '|' + str(self.first_tag_counter) + '=' +
                                str(config_start_value) + '|\r\n')
                else:
                    cmds.append('LAS|' + self.fail_job_name + '|1|\r\n')
            elif self.printing_format == 'SGTIN':
                # SGTIN_QR has field for reel_num + 'T' and field for sgtin,
                # SGTIN_only acts the same (the QR will not be in the sticker itself)
                if self.pass_job_name == 'SGTIN_QR' or self.pass_job_name == 'SGTIN_only' or \
                        self.pass_job_name == 'devkit_TEO' or self.pass_job_name == 'devkit_TIKI' \
                        or self.pass_job_name == 'empty':
                    cmds = ['CAF\r\n', 'CQI\r\n', 'CLN|1|\r\n', 'CLN|2|\r\n',
                            'LAS|' + str(self.pass_job_name) + '|2|' + str(self.sgtin) + '=' + str(
                                self.roll_sgtin[:18]) + '|'
                            + str(self.reel_num) + '=' + str(self.roll_sgtin[18:26]) + 'T' + '|'
                            + str(self.first_tag_counter) + '=' + str(config_start_value) + '|\r\n']
                    if self.fail_job_name == self.pass_job_name:
                        cmds.append('LAS|' + str(self.fail_job_name) + '|1|' + str(self.sgtin) + '=' +
                                    str(self.roll_sgtin[:18]) + '|' + str(self.reel_num) + '=' +
                                    str(self.roll_sgtin[18:26]) + 'T' + '|' + str(self.first_tag_counter) + '=' +
                                    str(config_start_value) + '|\r\n')
                    else:
                        cmds.append('LAS|' + self.fail_job_name + '|1|\r\n')

            else:
                printing_func('The print Job Name inserted is not supported at the moment, You will need to press Stop',
                              'PrinterThread', lock_print, logger_type='debug')

            for cmd in cmds:
                value = self.query(cmd)
                time.sleep(0.1)
                # check if the return value is good, if not retry again for 10 times
                counter = 0
                while counter < 10:
                    # 'CQI' fails if the queue is empty
                    if value == 'ERR' and 'CQI' not in cmd:
                        counter += 1
                        time.sleep(0.1)
                        value = self.query(cmd)
                    else:
                        break
                if counter >= 10:
                    self.events.printer_error.set()
                    raise PrinterNeedsResetException('The printer initialization process has failed in command: ' + cmd)
            # get the current counter value
            value = self.query(self.get_state_request())
            if value == 'ERR':
                self.events.printer_error.set()
                raise PrinterNeedsResetException(
                    'The printer initialization process has failed in command: ' + self.get_state_request())
            else:
                parts = [p for p in value.split("|")]
                self.cur_value = int(parts[5])

            if not self.events.printer_error.isSet():
                printing_func('printer thread is ready after initialization',
                              'PrinterThread', lock_print, logger_type='debug')
                self.events.printer_success.set()
        except Exception:
            exception_details = sys.exc_info()
            self.exception_queue.put(exception_details)

    def set_printer_to_running(self):
        """
        sets the printer to running mode
        Zipher Text Communications Protocol
        printer state machine:
           0 -> 1                      shutdown
           1 -> 4 (automatically)      starting-up
           2 -> 0 (automatically)      shutting-down
           3 -> 2, 4                   running
           4 -> 2, 3                   offline
        @except: PrinterNeedsResetException('Printer failed to switch to running mode')
        @return: None
        """
        res = self.query(self.get_state_request())
        parts = [p for p in res.split("|")]
        if parts[1] == '0':  # (Shut down)
            res = self.query(self.set_state_command('1'))
            if res == 'ACK':
                while True:
                    time.sleep(1)
                    res = self.query(self.set_state_command('3'))
                    if res == 'ACK':
                        return
        elif parts[1] == '3':  # (Running)
            return
        elif parts[1] == '4':  # (Offline)
            res = self.query(self.set_state_command('3'))
            if res == 'ACK':
                return

        self.events.printer_error.set()
        raise PrinterNeedsResetException('Printer failed to switch to running mode')

    def run(self):
        """
        runs the thread
        """
        global passed
        # this flag will tell the printer to restart its run() (for a case of connectionError)
        do_the_thread_again = True
        while do_the_thread_again:
            do_the_thread_again = False
            logging.debug('starts printer inner loop')
            while not self.events.done_to_printer_thread.isSet():
                try:
                    self.r2r_ready_or_done2tag_or_done_to_printer_thread.wait()
                    if self.events.done_to_printer_thread.isSet():
                        break

                    # for a case of pause - the printing test should not happen (printing should not happen)
                    if self.events.pause_to_tag_thread.isSet():
                        self.events.cont_to_printer_thread.wait()

                    # to avoid wrong counter in edge cases of printer crash
                    if self.events.cont_to_printer_thread.isSet():
                        self.events.cont_to_printer_thread.clear()
                        # get the current counter value
                        value = self.query(self.get_state_request())
                        if value == 'ERR':
                            self.events.printer_error.set()
                            raise PrinterNeedsResetException(
                                'The printer initialization process has failed in command: ' + self.get_state_request())
                        else:
                            parts = [p for p in value.split("|")]
                            self.cur_value = int(parts[5])

                    self.events.r2r_ready.wait()
                    self.events.r2r_ready.clear()
                    self.cur_value += 1
                    self.printer_status()
                    # self.printing_happened_as_expected()

                except Exception:
                    exception_details = sys.exc_info()
                    self.exception_queue.put(exception_details)
                    exc_type, exc_obj, exc_trace = exception_details
                    self.events.printer_error.set()  # to avoid deadlocks
                    # ConnectionResetError => exc_obj = 'An existing connection was forcibly closed by the remote host'
                    if isinstance(exc_obj, PrinterNeedsResetException):
                        self.r2r_ready_or_done2tag_or_done_to_printer_thread.wait()
                        break
                    elif isinstance(exc_obj, ConnectionResetError):
                        self.r2r_ready_or_done2tag_or_done_to_printer_thread.wait()
                        try:
                            self.reopen_sock()
                            do_the_thread_again = True
                            self.events.done_to_printer_thread.clear()
                            continue
                        except Exception:
                            exception_details = sys.exc_info()
                            printing_func(
                                'self.reopen_sock() in printer thread failed, will end this run. {}'.format(format_exception_details(exception_details)),
                                'PrinterThread', lock_print, logger_type='debug')
                            self.exception_queue.put(exception_details)
                            exc_type, exc_obj, exc_trace = exception_details
                            self.events.printer_error.set()  # to avoid deadlocks
                            if isinstance(exc_obj, PrinterNeedsResetException):
                                self.r2r_ready_or_done2tag_or_done_to_printer_thread.wait()
                                break
                    else:
                        self.r2r_ready_or_done2tag_or_done_to_printer_thread.wait()

        self.closure()
        printing_func("Exited the while loop of printer thread", 'PrinterThread', lock_print, logger_type='debug')
        return

    def printer_status(self):
        """
        checks if the printing value matches the values registered to the logs
        should be called only after self.events.r2r_ready was set
        Exceptions:
            @except Exception('The printer printed Pass to the previous tag'):
                    printer printed pass while it should have been print fail
            @except Exception('The printer printed Fail to the previous tag')
                    printer printed fail while it should have been print pass
            @except Exception('The printer have not printed on the last tag')
                    printer did not print while it should have been
        """

        time.sleep(0.4)  # Added delay in order to give the printer extra time for respond

        try:
            res = self.query(
                self.get_state_request())  # STS|<overallstate>|<errorstate>|<currentjob>|<batchcount>|<totalcount>
            parts = [p for p in res.split("|")]

            if parts[1] == '3':
                if parts[2] == '0':
                    self.events.printer_success.set()
                    logging.debug('Printer status is online')
                else:
                    if parts[2] == '1':
                        self.events.printer_error.set()
                        raise Exception('The printer error-state is Warnings present')
                    if parts[2] == '2':
                        self.events.printer_error.set()
                        raise Exception('The printer error-state is Faults present')

            else:
                if parts[1] == '0':
                    self.events.printer_error.set()
                    raise PrinterNeedsResetException('The printer over-all-state is Shutdown')
                if parts[1] == '1':
                    self.events.printer_error.set()
                    raise PrinterNeedsResetException('The printer over-all-state is Starting up')
                if parts[1] == '2':
                    self.events.printer_error.set()
                    raise PrinterNeedsResetException('The printer over-all-state is Shutting down')
                if parts[1] == '4':
                    self.events.printer_error.set()
                    raise PrinterNeedsResetException('The printer over-all-state is Offline')
                if parts[2] == '1':
                    self.events.printer_error.set()
                    raise Exception('The printer error-state is Warnings present')
                if parts[2] == '2':
                    self.events.printer_error.set()
                    raise Exception('The printer error-state is Faults present')

        except Exception:
            logging.warning('Problem with receiving data from printer, please check if its working')

    def printing_happened_as_expected(self):
        """
        checks if the printing value matches the values registered to the logs
        should be called only after self.events.r2r_ready was set
        Exceptions:
            @except Exception('The printer printed Pass to the previous tag'):
                    printer printed pass while it should have been print fail
            @except Exception('The printer printed Fail to the previous tag')
                    printer printed fail while it should have been print pass
            @except Exception('The printer have not printed on the last tag')
                    printer did not print while it should have been
        """
        increase = False
        self.timer = threading.Timer(self.printer_response_timeout, self.end_of_time)
        self.timer.start()
        printing_on_last_tag_happened = False

        # time.sleep(0.15)  # Empiric tests have shown the answer will not be received until 150ms have passed
        time.sleep(0.5)  # Added delay in order to give the printer extra time for respond
        """if operators add time delay for printer, 
        we need to extend the Timer thread in the beginning of the function"""
        # will try to get the printing status until timer will end
        while not self.timer_is_done and not self.events.done_to_printer_thread.isSet() and \
                not printing_on_last_tag_happened:
            res = self.query(self.get_state_request())
            parts = [p for p in res.split("|")]
            if parts[1] != '3':
                self.timer.cancel()
                self.timer_is_done = False
                if parts[1] == '0':
                    self.events.printer_error.set()
                    raise PrinterNeedsResetException('The printer over-all-state is Shutdown')
                if parts[1] == '1':
                    self.events.printer_error.set()
                    raise PrinterNeedsResetException('The printer over-all-state is Starting up')
                if parts[1] == '2':
                    self.events.printer_error.set()
                    raise PrinterNeedsResetException('The printer over-all-state is Shutting down')
                if parts[1] == '4':
                    self.events.printer_error.set()
                    raise PrinterNeedsResetException('The printer over-all-state is Offline')
            if parts[2] != '0':
                self.timer.cancel()
                self.timer_is_done = False
                if parts[2] == '1':
                    self.events.printer_error.set()
                    raise Exception('The printer error-state is Warnings present')
                if parts[2] == '2':
                    self.events.printer_error.set()
                    raise Exception('The printer error-state is Faults present')
                self.events.printer_error.set()
                break

            # the counter is correct
            if int(parts[5]) == self.cur_value:
                printing_on_last_tag_happened = True
                # the prev tag passed
                if self.events.was_pass_to_printer.isSet():
                    self.events.was_pass_to_printer.clear()
                    # pass was printed
                    if parts[3] == self.pass_job_name:
                        self.events.printer_success.set()
                    else:
                        self.timer.cancel()
                        self.timer_is_done = False
                        self.events.printer_error.set()
                        raise Exception('The printer printed Fail to the previous tag')

                    self.ports_and_guis.update_printer_gui_inputs()  # will add one to last printing value

                # the prev tag failed
                else:
                    self.events.was_fail_to_printer.clear()
                    # fail was printed
                    if parts[3] == self.fail_job_name:
                        self.events.printer_success.set()
                    else:
                        self.timer.cancel()
                        self.timer_is_done = False
                        self.events.printer_error.set()
                        raise Exception('The printer printed Pass to the previous tag')
            else:
                printing_func('Failed comparison of printer ID {} with current expected ID {}'.format(int(parts[5]),
                                                                                                      self.cur_value),
                              'PrinterThread', lock_print, logger_type='info')
                print(str((int(parts[5]) - self.cur_value == 1)) + str(increase))
                if (int(parts[5]) - self.cur_value == 1) and not increase:
                    print('increament the inner counter')
                    self.cur_value += 1
                    increase = True

            time.sleep(0.05)

        self.timer.cancel()
        self.timer_is_done = False

        if not printing_on_last_tag_happened:
            self.events.printer_error.set()
            raise Exception('The printer have not printed on the last tag')

    def end_of_time(self):
        """
        is triggered at the end of timer
        """
        self.timer_is_done = True

    def query(self, cmd, print_and_log=True):
        """Send the input cmd string via TCPIP Socket
        @type cmd: string
        @param cmd: command to send to printer
        @type print_and_log: bool
        @param print_and_log: if true print and log the communication
        @return: the reply string
        """
        if print_and_log:
            msg = "Sent command to printer: " + cmd.strip('\r\n')
            printing_func(msg, 'PrinterThread', lock_print, logger_type='debug')
        self.ports_and_guis.Printer_socket.send(cmd.encode())
        data = self.ports_and_guis.Printer_socket.recv(int(self.TCP_BUFFER))
        value = data.decode("utf-8")
        # Cut the last character as the device returns a null terminated string
        value = value[:-1]
        if print_and_log:
            msg = "Received answer from printer: " + str(value.strip('\r\n'))
            printing_func(msg, 'PrinterThread', lock_print, logger_type='debug')

        return value

    def closure(self):
        """
        set printer to shutting down and close the socket
        """
        try:
            self.query(self.set_state_command('2'))  # for regular closure (not when connection error happens)
            self.ports_and_guis.Printer_socket.close()
        except Exception:
            try:
                self.ports_and_guis.Printer_socket.close()
            except Exception:
                printing_func('s.close() failed', 'PrinterThread', lock_print, logger_type='warning')
                pass

    def reopen_sock(self):
        """
        close and reopens the printer sock
        """
        try:
            self.closure()
            time.sleep(1)  # to make sure the socket is closed when we start the reopen
            self.initialization()
        except Exception:
            printing_func('reopen_sock() failed, please end this run', 'PrinterThread',
                          lock_print, logger_type='warning')
            raise (PrinterNeedsResetException('reopen_sock() failed'))

    def line_assigment(self, job_name, line_number, field_name, field_value):
        """
        builds the command to send to printer for configuration of the printing format
        @param job_name: (string) what is the job name (should be the same as in the printer)
        @param line_number: what is the line to assign to (2 = pass, 1 = fail)
        @param field_name: field name in the printer
        @param field_value: what to put in this field
        @return: the cmd to send to printer
        """
        # Send Line Assignment Command: job name + line number+starting value
        cmd = 'LAS|' + str(job_name) + '|' + str(line_number) + '|' + str(field_name) + '=' + str(
            field_value) + '|\r\n'
        # changing to bytes
        return cmd

    def clear_line(self, line_number):
        """
        builds the command to send to printer for clearing a line
        @param line_number: the line to clear
        @return: the cmd to send to printer
        """
        # On success, returns the default success response (ACK). On failure, returns the default failure response (ERR)
        cmd = 'CLN|' + str(line_number) + '|\r\n'
        return cmd

    def set_state_command(self, desired_state):
        """
        builds the command to send to printer for setting a printer state
        @param desired_state: the state to enter to, according to the following description
        0 Shut down
        1 Starting up
        2 Shutting down
        3 Running
        4 Offline
        @return: the cmd to send to printer
        """
        cmd = 'SST|' + str(desired_state) + '|\r\n'
        return cmd

    def get_job_name(self):
        """
        gets the last job that were used by the printer
        @return: the name of the current job in the printer in the following format:
            JOB|<job name>|<line number>|<CR>
        """
        cmd = 'GJN\r\n'
        return cmd

    def get_state_request(self):
        """
        gets the situation of the printer
        @return: the situation in the printer in the following format:
            STS|<overallstate>|<errorstate>|<currentjob>|<batchcount>|<totalcount>|<
        """
        cmd = 'GST\r\n'
        return cmd


class TagThread(threading.Thread):
    """
    Thread that controls the gateway, tests each tag and saves data to csv output file
    Parameters:
        @type events: class MainEvents (costume made class that has all of the Events of the program threads)
        @param events: has all of the Events of the program threads
        @type ports_and_guis: class PortsAndGuis (costume made class that has all of the ports and gui inputs for the
                            program threads)
        @param ports_and_guis: has all of the ports and gui inputs for the program threads

    Exceptions:
        @except Exception: 'Exception happened in Tag thread initialization. need to kill this run'
                means that connecting to GW or temperature sensor failed, the run will pause and wait for
                stop button from user

        @except Exception: 'tag_checker_thread got an Exception, press Continue or Stop'
                exception details will be printed

        @except (OSError, serial.SerialException):
                Problems with GW connection, requires user to press "Stop" and end the run

        @except Exception: exception occurred while testing a tag (inside new_tag function)

        @except Exception('R2R moved before timer ended') :
                Either R2R moved before or received packet is not valid tag packet
                The run will pause

        @except Exception: 'Warning: packet_decoder could not decode packet, will skip it'
                In case encrypted_packet_decoder() failed in decoding packet, packet is skipped and
                threads waits for next packet.
                Run won't pause in that case. If tag reaches timeout, it will marked as fail

    Events:
        listen/ waits on:
            events.r2r_ready_or_done2tag => user pressed Stop (end the program) or r2r has finished to write the command
            events.done_or_printer_event => waits for printer event or for done_to_tag_thread (closes TagThread)
            events.done_to_tag_thread => closes TagThread at the end of the run
            events.cont_to_tag_thread => wait for continue from MainWindow thread
            events.pause_to_tag_thread => pauses thread if exception happened of user pressed Pause
            events.printer_error => the last print was not successful, will cause pause to this run
                                                (and will trigger exception according to the situation)

        sets:
            events.cont_to_main_thread => send continue from TagThread to MainWindow thread
            events.tag_thread_is_ready_to_main => notifies MainWindow thread TagThread is ready
            events.pause_to_tag_thread => pauses thread if exception happened of user pressed Pause
            events.was_pass_to_printer => tag has passed. report "Pass" to printer
            events.was_fail_to_printer => tag has failed. report "Fail" to printer
            events.disable_missing_label_to_r2r_thread => if set, the run will pause if missing label is detected
            events.enable_missing_label_to_r2r_thread => if set, the run will not pause if missing label is detected
                                                        (up to maxMissingLabels set by user)
            events.start_to_r2r_thread => enable/disable R2R movement. Sends pulse on "Start/Stop machine" GPIO line
            events.stop_to_r2r_thread => stops the R2R from running in case of end of run or exception
            events.pass_to_r2r_thread => notify if current tag passed. if set, send pulse on "Pass" GPIO line,
                                         The R2R will advance to next tag
            events.fail_to_r2r_thread => notify if current tag failed. if set, send pulse on "Fail" GPIO line,
                                         The R2R will advance to next tag

    Logging:
        logging to logging.debug(), logging.info() and logging.warning()
    """

    def __init__(self, events, ports_and_guis, management_client):
        """
        Initialize Constants
        """
        super(TagThread, self).__init__(daemon=True)
        self.ports_and_guis = ports_and_guis
        self.events = events
        # self.test_times_up = False
        self.r2r_response_times_up = False
        self.test_suite_times_up = False
        self.duplication_handling_timer_is_done = False
        self.serialize_status = True
        self.ttfgp_list = []
        self.tag_list_len = 5000  # TODO - decide how many tags to use here
        self.adv_addr = ''
        self.rssi = 0
        self.tbp = -1
        self.ttfp = -1
        self.time_for_duplication_handling = 20  # time in seconds for duplication handling procedure
        self.management_client = management_client
        self.fatal_gw_error = False
        # variables for using serialization API

        self.num_of_tags_per_upload_batch = 10
        self.serialization_data_for_all_run = []  # list of data_to_upload lists
        # the tags that have not been started the upload yet

        self.next_batch_to_serialization = {'response': '', 'upload_data': [], 'failed_already': False}
        self.serialization_threads_working = []  # the actual threads that do the serialization

        self.pass_job_name = ''  # will be set inside config
        self.to_print = False
        self.printing_value = {'passJobName': None, 'stringBeforeCounter': None, 'digitsInCounter': 10,
                               'firstPrintingValue': '0'}  # will be set in config()
        self.done_or_printer_event = or_event_set(self.events.done_to_tag_thread, self.events.printer_event)
        self.fetal_error = False
        self.exception_queue = Queue()
        self.qr_enable = self.ports_and_guis.Tag_Value['QRRead']
        self.qr_offset = self.ports_and_guis.Tag_Value['QRoffset']
        self.qr_max_bad_tags = int(self.ports_and_guis.Tag_Value['maxQRWrongTags'])

        try:
            self.GwObj, self.t = self.config()
        except Exception as e:
            exception_details = sys.exc_info()
            self.exception_queue.put(exception_details)
            printing_func(
                'Exception happened in Tag thread initialization. need to kill this run. {}'.format(format_exception_details(exception_details)),
                'TagThread', lock_print, logger_type='warning')
            # to pause the run if exception happens
            self.events.cont_to_tag_thread.wait()
            self.events.cont_to_tag_thread.clear()
            self.events.pause_to_tag_thread.clear()
            self.events.cont_to_main_thread.set()
        self.r2r_timer = None
        self.test_suites_timer = None
        self.timer_for_curr_test = ''
        self.printed_external_id = ''
        self.timer_for_duplication_handling = None
        self.fail_tags_with_same_packet_within_secs = False

        self.tag_location = 0
        self.events.tag_thread_is_ready_to_main.set()
        file_path, user_name, password, owner_id, is_successful = check_user_config_is_ok()

    @pyqtSlot()
    def run(self):
        """
        runs the thread
        """
        if self.value['missingLabel'] == 'No':
            self.events.disable_missing_label_to_r2r_thread.set()
            self.is_missing_label_mode = False
        elif self.value['missingLabel'] == 'Yes':
            self.events.enable_missing_label_to_r2r_thread.set()
            self.is_missing_label_mode = True

        self.events.tag_thread_is_ready_to_main.set()
        die = False
        self.missing_labels_in_a_row = 0

        while not die:
            try:
                if self.ports_and_guis.do_serialization:
                    self.serialize_status = check_serialization_exception_queues(self.serialization_threads_working,
                                                                                 printing_lock=lock_print)
                self.events.r2r_ready_or_done2tag.wait()
                if self.events.done_to_tag_thread.is_set():
                    logging.warning('Job is done')
                    die = True
                else:  # the r2r_ready event happened , done_or_printer_event.wait will happen after start GW
                    # start of tags loop ###########################
                    # the long timer (will cause +1 missing label)
                    self.r2r_response_times_up = False
                    # will wait 10 seconds after the tag timer should have ended
                    # and then will enforce a start_r2r & fail_r2r
                    self.time_out_to_missing_label = float(self.value['testTime']) + 5
                    self.r2r_timer = threading.Timer(self.time_out_to_missing_label, self.end_of_time,
                                                     ['r2r is stuck'])
                    self.r2r_timer.start()
                    if self.ports_and_guis.do_serialization:
                        # check if the serialization process so far are OK
                        self.serialize_status = check_serialization_exception_queues(self.serialization_threads_working,
                                                                                     printing_lock=lock_print)
                        check_serialization_response(self.serialization_threads_working)
                    # new_tag will set the events (pass_to_r2r_thread, fail_to_r2r_thread)
                    result = self.new_tag(self.t)
                    if result == 'Exit':
                        logging.warning('Job is done')
                        die = True
                    self.tag_location += 1
                    # end of tags loop ###############################
                # will upload a batch at the end of the run or after self.num_of_tags_per_upload_batch
                if (len(self.next_batch_to_serialization['upload_data']) ==
                    self.num_of_tags_per_upload_batch or
                    (die and len(self.next_batch_to_serialization['upload_data']) > 0)) \
                        and self.to_print and self.ports_and_guis.do_serialization:
                    self.serialization_data_for_all_run.append(self.next_batch_to_serialization)
                    self.next_batch_to_serialization = {'response': '', 'upload_data': [], 'failed_already': False}
                    self.serialize_status = check_serialization_exception_queues(self.serialization_threads_working,
                                                                                 printing_lock=lock_print)

                    self.serialization_threads_working.append(
                        SerializationAPI(batch_dictionary=self.serialization_data_for_all_run[-1], to_logging=True,
                                         security_client=self.management_client.auth_obj,
                                         try_serialize_again=self.events.try_serialize_again, printing_lock=lock_print,
                                         env=self.ports_and_guis.env))
                    self.serialization_threads_working[-1].start()

                if not self.serialize_status:
                    msg = 'Serialization failed'
                    printing_func(msg, 'TagThread', lock_print, logger_type='warning')


            except (OSError, serial.SerialException):
                if self.events.done_to_tag_thread.is_set():
                    logging.warning('Job is done')
                    die = True
                exception_details = sys.exc_info()
                self.exception_queue.put(exception_details)
                printing_func("Problems with gateway serial connection - click on Stop and exit the app. {}".format(format_exception_details(exception_details)),
                              'TagThread', lock_print, logger_type='warning')
                self.fetal_error = True
            except Exception:
                if self.events.done_to_tag_thread.is_set():
                    logging.warning('Job is done')
                    die = True
                exception_details = sys.exc_info()
                self.exception_queue.put(exception_details)
                # wait until user press Continue
                if self.r2r_timer is not None:
                    self.r2r_timer.cancel()

                if not die:
                    self.events.cont_to_tag_thread.wait()
                self.events.cont_to_tag_thread.clear()
                self.events.pause_to_tag_thread.clear()
                self.events.cont_to_main_thread.set()
        self.closure_fn()

    def end_of_time(self, kind):
        """
        sets the correct flag to True when a timer is done
        @param kind: the kind of the timer
        """
        if kind == 'tag':
            self.test_suite_times_up = True
            printing_func("Tag reached Time-Out",
                          'TagThread', lock_print, logger_type='debug')
        if kind == 'r2r is stuck':
            self.r2r_response_times_up = True
            printing_func("R2R is stuck, Tag reached Time-Out",
                          'TagThread', lock_print, logger_type='debug')
            logging.debug("R2R is stuck, Tag reached Time-Out")
        if kind == 'duplication handling':
            self.duplication_handling_timer_is_done = True
            printing_func("Duplication handling timer is over",
                          'TagThread', lock_print, logger_type='debug')

    def reset_and_init_gw(self):
        self.GwObj.reset_gw()
        self.fatal_gw_error = False
        self.GwObj.start_continuous_listener()
        # self.GwObj.write('!set_energizing_pattern 52')
        # time.sleep(0.1)
        # self.GwObj.write('!set_energizing_pattern 51')
        # time.sleep(0.1)

        print(self.GwObj.write('!set_tester_mode 1'))
        time.sleep(0.1)
        print(self.GwObj.write('!enable_brg_mgmt 0'))
        time.sleep(0.1)
        # +30 to let us see the high rssi packets in the PC (will be captured in the encrypted_packet_filter())
        self.GwObj.config_gw(rssi_thr_val=int(self.tests_suite['rssiThreshold']) + 30, energy_pattern_val=18,
                             output_power_val='pos3dBm', time_profile_val='0,6', filter_val=False,
                             pacer_val=0, received_channel=37, pl_delay_val=self.tests_suite['plDelay'], start_gw_app=False)
        # time.sleep(0.01)
        # self.GwObj.check_current_config()  # for debugging

    def config(self):
        """
        configuration of GW, logging and run_data
        @return:  Gw's Com port Obj, temperature sensor
        """
        self.value = self.ports_and_guis.Tag_Value
        if self.value['comments'] == '':
            self.value['comments'] = None

        self.tests_suite = self.ports_and_guis.tests_suite

        if 'rssiThreshold' in self.tests_suite:
            if self.tests_suite['rssiThreshold'] == '':
                self.tests_suite['rssiThreshold'] = 65
        else:
            self.tests_suite['rssiThreshold'] = 65
            
        self.tests_suite['rssiThreshold'] = int(self.tests_suite['rssiThreshold'])
        self.num_of_tests = len(self.tests_suite['tests'])
        for test_num in range(self.num_of_tests):
            if not 'absGwTxPowerIndex' in self.tests_suite['tests'][test_num]:
                if 'tbpTarget' in self.tests_suite['tests'][test_num]:
                    top_score = get_calibration_results(target_tbp=self.tests_suite['tests'][test_num]['tbpTarget'],
                                                        energy_pattern=[self.tests_suite['tests'][test_num]['energizingPattern']])
                else:
                    logging.info(
                        'Problem with generating tbp best power from config file will work with default calibration knee')
                    top_score = get_calibration_results(target_tbp=0, energy_pattern=[
                        self.tests_suite['tests'][test_num]['energizingPattern']])

                self.tests_suite['tests'][test_num]['absGwTxPowerIndex'] = top_score['absGwTxPowerIndex'].item()
                if not 'timeProfile' in self.tests_suite['tests'][test_num]:
                    self.tests_suite['tests'][test_num]['timeProfile'][0] = top_score['time_profile_on'].item()
                    self.tests_suite['tests'][test_num]['timeProfile'][1] = top_score['time_profile_period'].item()
                if not 'rssiThreshold' in self.tests_suite:
                    self.tests_suite['rssiThreshold'] = int(top_score['rssi_max'].item()) + 6

                logging.info('values set for test {} are: tbp_target = {}, top score index = {}, rssi_threshold = {}'.format(str(test_num),
                                                                                                        str(top_score[
                                                                                                                'tbp_mean'].item()),
                                                                                                        str(
                                                                                                            self.tests_suite[
                                                                                                                'tests'][
                                                                                                                test_num][
                                                                                                                'absGwTxPowerIndex']),str(self.tests_suite['rssiThreshold'])))
                if (not 'absGwTxPowerIndex' in self.tests_suite['tests'][test_num]) and (
                not 'tbpTarget' in self.tests_suite['tests'][test_num]):
                    logging.warning('Please setup test suite tests or calibrate machine')

            else:
                logging.info('values set for test {} are: top score index = {}'.format(str(test_num), str(
                    self.tests_suite['tests'][test_num]['absGwTxPowerIndex'])))

        # TODO: needs to be edited before next gen cloud post process:
        self.internal_value = {"energizingPattern": "-1", "timeProfile": "-1", "txPower": "-1", "rssiThreshold":
            str(self.tests_suite['rssiThreshold']), "plDelay": str(self.tests_suite['plDelay'])}
        self.tags_handling = TagsHandling(self.tag_list_len, lock_print=lock_print,
                                          rssi_threshold=int(self.tests_suite['rssiThreshold']),
                                          logging_thread='TagThread', only_add_tags_after_location_ends=True,
                                          add_to_black_list_after_locations=int(self.value['blackListAfter']))
        # for the case we do not print
        self.externalId = 0
        self.pass_job_name = ''
        global problem_in_locations_hist
        problem_in_locations_hist = self.tags_handling.problem_in_locations_hist
        if self.value['toPrint'] == 'Yes':
            self.to_print = True
            self.printing_value, is_OK = self.ports_and_guis.Tag_Printing_Value, self.ports_and_guis.Tag_is_OK
            self.externalId = int(self.printing_value['firstPrintingValue'])
            self.pass_job_name = self.printing_value['passJobName']

        # setting up the global variables ###################################################
        global desired_pass_num
        global desired_tags_num
        desired_tags_num = int(self.value['desiredTags'])
        desired_pass_num = int(self.value['desiredPass'])

        # config GW, temp sens and classifier ###############################################
        self.GwObj = self.ports_and_guis.GwObj
        self.reset_and_init_gw()

        global temperature_sensor_enable
        if temperature_sensor_enable:
            t = self.ports_and_guis.Tag_t
        else:
            t = None
        self.internal_value['testerStationName'] = self.ports_and_guis.tag_tester_station_name

        global run_data_list
        run_data_list.append(self.value)
        run_data_list.append(self.internal_value)
        run_data_list.append(self.printing_value)
        # run_data_list.append(self.ports_and_guis.test_configs)             # TODO - add this field to run_data
        # run_data_list.append({'wiliotPackageVersion': version('wiliot')})  # TODO - add this field to run_data
        printing_func("wiliot's package version = " + str(get_version()), 'TagThread', lock_print=lock_print,
                      do_log=True)
        global run_start_time
        logging.info('Start time is: ' + run_start_time + ', User set up is: %s, %s, %s',
                     self.value, self.internal_value, self.printing_value)
        global run_data_dict
        global run_data_log

        if run_data_log is None:
            global run_data_path
            run_data_log = CsvLog(header_type=HeaderType.RUN, path=run_data_path, tester_type=TesterName.OFFLINE)
            run_data_log.open_csv()
            printing_func("run_data log file has been created",
                          'TagThread', lock_print, logger_type='debug')
        for dic in run_data_list:
            for key in dic.keys():
                if key in run_data_log.header:
                    run_data_dict[key] = dic[key]

        run_data_dict['commonRunName'] = common_run_name
        run_data_dict['testerType'] = 'offline'
        sw_version, _ = self.GwObj.get_gw_version()
        run_data_dict['gwVersion'] = sw_version
        global yield_over_time
        global calculate_interval
        global calculate_on
        global passed
        global tested
        run_data_dict['yieldOverTime'] = yield_over_time
        run_data_dict['yieldOverTimeInterval'] = calculate_interval
        run_data_dict['yieldOverTimeOn'] = calculate_on
        run_data_dict['passed'] = passed
        run_data_dict['tested'] = tested
        if tested > 1:  # avoid division by zero
            run_data_dict['yield'] = passed / (tested - 1)
        if tested == 0:
            run_data_dict['yield'] = -1.0
            run_data_dict['includingUnderThresholdPassed'] = -1
            run_data_dict['includingUnderThresholdYield'] = -1.0
        run_data_log.append_list_as_row(run_data_log.dict_to_list(run_data_dict))
        return self.GwObj, t

    def get_curr_timestamp_in_sec(self):
        return (datetime.datetime.now() - self.start_time).total_seconds()

    def is_gw_respond_with_stat_param_zero(self,chosen_tag_packets):
        chosen_tag_packets_df = chosen_tag_packets.get_df()
        return len(chosen_tag_packets_df[chosen_tag_packets_df['stat_param'] == 0]) > 1

    def new_tag(self, t):
        """
        will run a loop to count the packets for 1 tag and decide pass/fail
        @param t: temperature sensor
        """
        global tags_data_log, debug_tags_data_log, tags_data_path, debug_tags_data_path
        global packets_data_log, packets_data_path
        global under_threshold, missing_labels, temperature_sensor_enable
        global is_debug_mode
        global qr_que_list
        chosen_tag_data_list = []
        debug_chosen_tag_data_list = []
        self.timer, self.timer_for_curr_test, raw_data = '', '', ''
        self.timer_for_duplication_handling = None
        self.start_GW_happened = False  # will say if the r2r is in place, if not -> busy wait in the while loop
        # self.test_times_up = False
        self.test_suite_times_up = False
        self.duplication_handling_timer_is_done = False
        temperature_from_sensor = 0
        self.tag_appeared_before = False
        self.need_to_check_tbp = False
        self.chosen_tag_in_location = None
        self.tbp = -1
        self.ttfp = -1
        self.tag_is_certain = True
        fail_this_tag = False
        # TODO: remove from here:
        if self.qr_enable == 'Yes':
            # logging.debug(qr_que_list)
            if len(qr_que_list) > int(self.qr_offset):
                self.events.start_qr_scan.set()  # start qr readout
                # logging.debug('Go to QR was set')
            else:
                self.events.qr_read_success.set()
                # logging.debug('Still not 3 in que')
        #######################################

        self.tests_suite['rssiThreshold'] = float(self.tests_suite['rssiThreshold'])
        num_of_tests = len(self.tests_suite['tests'])
        test_suite_results = [False] * num_of_tests
        all_tests_packets = PacketList()
        packets_data = {}

        # TODO: support attenuation:
        curr_atten = 0

        # For debug:
        timing_prints = False

        def clear_timers():
            if self.test_suites_timer is not None:
                self.test_suites_timer.cancel()
                self.test_suite_times_up = False
            # if not self.timer_for_curr_test == '':
            #     self.timer_for_curr_test.cancel()
            #     self.test_times_up = False
            if self.r2r_timer is not None:
                self.r2r_timer.cancel()
                self.r2r_response_times_up = False
            if self.timer_for_duplication_handling is not None:
                self.timer_for_duplication_handling.cancel()
                self.duplication_handling_timer_is_done = False

        def check_if_should_end_test(test_done_flag):
            """
            :type test_done_flag: bool
            :param test_done_flag: the value that was already assigned to test_done
            """
            tags_stats_internal, test_done_internal, rssi_diff_internal = None, False, np.inf

            min_rssi = np.inf
            best_tag = None

            if curr_test_packets.get_num_packets() > 0:
                tags_stats_internal = curr_test_packets.get_group_statistics('adv_address')
                # get the necessary chosen tag details to continue
                if self.chosen_tag_in_location is None or not self.tag_is_certain:
                    if len(tags_stats_internal.keys()) == 1:
                        self.chosen_tag_in_location = list(tags_stats_internal.keys())[0]
                        self.adv_addr = self.chosen_tag_in_location
                        self.tbp = tags_stats_internal[self.chosen_tag_in_location]['tbp_mean']
                        self.tag_is_certain = True

                    else:
                        for curr_tag in tags_stats_internal.keys():
                            if tags_stats_internal[curr_tag]['rssi_mean'] < min_rssi and tags_stats_internal[curr_tag][
                                'num_packets'] >= test_params['minPackets']:
                                if best_tag is not None:
                                    rssi_diff_internal = tags_stats_internal[curr_tag]['rssi_mean'] - \
                                                         tags_stats_internal[best_tag]['rssi_mean']
                                min_rssi = tags_stats_internal[curr_tag]['rssi_mean']
                                best_tag = curr_tag

                        if best_tag is not None:
                            self.chosen_tag_in_location = best_tag
                            # TODO: get this parameter from file\calibration\GUI:
                            self.tag_is_certain = rssi_diff_internal > 10
                            self.tbp = tags_stats_internal[self.chosen_tag_in_location]['tbp_mean']
            if self.chosen_tag_in_location is not None:
                if self.fail_tags_with_same_packet_within_secs:
                    chosen_tag_packets_internal = curr_test_packets.filter_packet_by(values=self.chosen_tag_in_location)
                    num_chosen_packets_internal = chosen_tag_packets_internal.get_num_packets()
                    if num_chosen_packets_internal > 1:
                        for j in range(1, len(chosen_tag_packets_internal.raw_packet_map_list)):
                            prev_packet_internal = chosen_tag_packets_internal[j - 1].packet_data['raw_packet']
                            curr_packet_internal = chosen_tag_packets_internal[j].packet_data['raw_packet']
                            if curr_packet_internal != prev_packet_internal:
                                printing_func("tag {} transmitted two different packets, will move to next location "
                                              "without waiting to complete packet threshold".
                                              format(self.chosen_tag_in_location),
                                              'TagThread', lock_print, do_log=True, logger_type='info')
                                test_done_internal = True

                if curr_test_packets.get_num_packets() >= test_params['minPackets'] > 0 and not test_done_internal:
                    if self.chosen_tag_in_location is None or not self.tag_is_certain:
                        if len(tags_stats_internal.keys()) == 1:
                            printing_func(f'Tag reached packet Threshold, only one tag found '
                                          f'{self.chosen_tag_in_location}',
                                          'TagThread', lock_print, do_log=True, logger_type='debug')
                        elif best_tag is not None:
                            printing_func(f'Tag reached packet Threshold, found best tag {self.chosen_tag_in_location} '
                                          f'among {len(list(tags_stats_internal.keys()))} tags',
                                          'TagThread', lock_print, do_log=True, logger_type='info')

                    if self.chosen_tag_in_location is not None and self.tag_is_certain:
                        # if self.ttfp<0:
                        #     self.ttfp = tags_stats_internal[self.chosen_tag_in_location]['ttfp']
                        #     if self.ttfp > float(self.value['maxTtfp']):
                        #         #failed because of ttfp:
                        #         test_done_internal = True
                        #         curr_test_fail_reasons += f"TTFP =
                        #         {self.ttfp}, bigger than maximum allowed in GUI {float(self.value['maxTtfp'])};"
                        #         self.curr_test_pass = False
                        if test_params['passTestModePacketsOnly'] == 1:
                            if len(tags_stats_internal.keys()) == 1:
                                if int(tags_stats_internal[list(tags_stats_internal)[0]]['num_packets']) >= \
                                        test_params['minPackets']:
                                    printing_func('Tag reached packet Threshold', 'TagThread', lock_print,
                                                  do_log=False,
                                                  logger_type='info')
                                    test_done_internal = True
                            elif len(tags_stats_internal.keys()) < 1:
                                printing_func('no tag has responded with acceptable data',
                                              'TagThread', lock_print,
                                              do_log=False,
                                              logger_type='info')
                                test_done_internal = False
                            else:
                                printing_func('more than 1 tag has responded with acceptable data',
                                              'TagThread', lock_print,
                                              do_log=False,
                                              logger_type='info')
                                test_done_internal = True

                        elif self.chosen_tag_in_location in tags_stats_internal and \
                                tags_stats_internal[self.chosen_tag_in_location]['num_packets'] >= test_params['minPackets']:
                            #TODO: how can we get here without haveing the tag in tags_stats_internal?? Tomer,15.5.2022
                            printing_func('Tag reached packet Threshold', 'TagThread', lock_print, do_log=False,
                                          logger_type='info')
                            test_done_internal = True

            return tags_stats_internal, test_done_internal or test_done_flag, rssi_diff_internal

        printing_func('************ new tag test ************', 'TagThread',
                      lock_print, logger_type='debug')

        # self.GwObj.reset_buffer()
        self.GwObj.reset_listener()
        self.start_time = datetime.datetime.now()
        if timing_prints:
            printing_func(
                "after reset, time is {}".format(self.GwObj.get_curr_timestamp_in_sec()), 'TagThread',
                lock_print, logger_type='debug')

        try:
            clear_timers()
        except Exception as e:
            print("Failed to clear timers")
            pass
        current_tag_is_certain = True
        # set_attn_power_offline(self.attn_obj, 0)

        # self.GwObj.check_current_config()  # for debugging

        sample_dt = 0.005  # sampling time for pause\stop response, consider to remove...
        # wait until the GPIO is triggered /max time is done. ignore all packets until done
        while (not self.r2r_response_times_up and not self.start_GW_happened) and \
                not self.events.pause_to_tag_thread.is_set() and \
                not self.events.cont_to_tag_thread.is_set() and not self.events.done_to_tag_thread.is_set():
            time.sleep(0)  # to prevent run slowdown by gateway_api
            gw_answer = self.GwObj.read_specific_message(msg="Start Production Line GW", read_timeout=sample_dt,
                                                         clear=False)
            if gw_answer == '':
                if self.GwObj.get_curr_timestamp_in_sec() > self.time_out_to_missing_label:
                    self.r2r_response_times_up = True  # will be treated as missing label
            else:
                self.start_GW_happened = True

        if timing_prints:
            printing_func(
                "after getting GW R2R response, time is {}".format(self.GwObj.get_curr_timestamp_in_sec()), 'TagThread',
                lock_print, logger_type='debug')

        # R2R moved to new location - start testing #################################################################
        if self.start_GW_happened:
            global tested
            tested += 1
            self.missing_labels_in_a_row = 0
            self.printed_external_id, is_OK = get_printed_value(self.printing_value['stringBeforeCounter'],
                                                                self.printing_value['digitsInCounter'],
                                                                str(self.externalId),
                                                                self.value['printingFormat'])
            if not is_OK:
                msg = 'printing counter reached a value that is bigger than the counter possible space.' \
                      ' the program will exit now'
                printing_func(msg, 'TagThread', lock_print, logger_type='warning')
                sys.exit(0)
            msg = "----------------- Tag location: " + str(self.tag_location) + \
                  " ----------------- expected tag external ID is: " + str(self.printed_external_id)
            printing_func(msg, 'TagThread', lock_print, logger_type='info')

            msg = "New Tag timer started (" + self.value['testTime'] + " secs)"
            printing_func(msg, 'TagThread', lock_print, logger_type='debug')
            all_tests_time = 0
            all_delays = 0
            self.sprinkler_counter_max = -1
            for test_num in range(num_of_tests):
                if 'delayBeforeNextTest' in self.tests_suite['tests'][test_num].keys():
                    all_delays += \
                        float(self.tests_suite['tests'][test_num]['delayBeforeNextTest'])
            for test_num in range(len(self.tests_suite['tests'])):
                all_tests_time += self.tests_suite['tests'][test_num]['maxTime']
            if "sprinkler_counter_max" in self.tests_suite.keys():
                self.sprinkler_counter_max = int(self.tests_suite["sprinkler_counter_max"][-1])
            if "numOfIterations" in self.tests_suite.keys():
                all_tests_time = (all_tests_time + all_delays) * int(self.tests_suite["numOfIterations"])
            else:
                all_tests_time += all_delays

            if all_tests_time > 90:
                raise ValueError(f"Duration of all tests {all_tests_time}s is longer than allowed -  90 seconds.")
            # set timer for new tag
            self.test_suites_timer = threading.Timer(all_tests_time + 5, self.end_of_time, ['tag'])
            self.test_suites_timer.start()

            self.tags_handling.set_new_location()
            global black_list_size
            black_list_size = self.tags_handling.get_black_list_size()
            chosen_tag_data_list = []
            debug_chosen_tag_data_list = []

            if temperature_sensor_enable:
                temperature_from_sensor = t.get_currentValue()

            # look for packets as long as user not interrupts AND
            # (test not over OR duplication handling procedure happening)
            num_of_iterations = 1
            if "numOfIterations" in self.tests_suite.keys():
                num_of_iterations = int(self.tests_suite['numOfIterations'])
            for iteration in range(num_of_iterations):
                for test_num in range(num_of_tests):
                    test_params = self.tests_suite['tests'][test_num]
                    if 'rxChannel' in self.tests_suite['tests'][test_num].keys():
                        test_params['rxChannel'] = int(self.tests_suite['tests'][test_num]['rxChannel'])
                    else:
                        test_params['rxChannel'] = 37
                    if 'delayBeforeNextTest' in self.tests_suite['tests'][test_num].keys():
                        test_params['delayBeforeNextTest'] = \
                            float(self.tests_suite['tests'][test_num]['delayBeforeNextTest'])
                    else:
                        test_params['delayBeforeNextTest'] = 0
                    if 'passTestModePacketsOnly' in self.tests_suite['tests'][test_num].keys():
                        test_params['passTestModePacketsOnly'] = \
                            self.tests_suite['tests'][test_num]['passTestModePacketsOnly']
                    else:
                        test_params['passTestModePacketsOnly'] = 0
                    if 'minPackets' not in test_params:
                        raise ValueError("minPackets is not defined for test {}".format(test_params['name']))
                    self.fail_tags_with_same_packet_within_secs = False
                    if "failTagsWithSamePacketWithinSecs" in self.tests_suite['tests'][test_num].keys():
                        self.fail_tags_with_same_packet_within_secs = True
                    try:
                        msg = "".join(["-"] * 20) + " Tag location: " + str(self.tag_location) + " Starting test #" + \
                              str(test_num) + ", test name " + test_params['name'] + ", test params = " + \
                              str(test_params) + " " + "".join(["-"] * 20)
                    except Exception:
                        msg = "".join(["-"] * 20) + " Tag location: " + str(self.tag_location) + " Starting test #" + \
                              str(test_num) + ", test name " + test_params['name'] + ", test params = " + \
                              str(test_params) + " " + "".join(["-"] * 20)
                    printing_func(msg, 'TagThread', lock_print, logger_type='info')
                    test_done = False
                    remained_packets_collected = False
                    # curr_test_results = {'packet_list':PacketList()}

                    curr_test_dur = test_params['maxTime']
                    curr_test_packets = PacketList()
                    curr_test_fail_reasons = ''
                    self.curr_test_pass = True
                    # self.timer_for_curr_test = threading.Timer(float(curr_test_dur), self.end_of_time,
                    #                                            ['test {} timeout before packet threshold'.format
                    #                                            (test_params['name'])])
                    # self.timer_for_curr_test.start()
                    # reseting the listener will also reset the GW timer- each test will calculates its own values:
                    self.GwObj.reset_listener()
                    curr_test_start_time = self.GwObj.get_curr_timestamp_in_sec()

                    if 'absGwTxPowerIndex' in test_params:
                        power_index = test_params['absGwTxPowerIndex']
                        if isinstance(power_index, str):
                            if power_index.upper() == 'MAX':
                                power_index = -1
                            else:
                                power_index = int(power_index)
                        elif not isinstance(power_index, int):
                            power_index = test_params['absGwTxPowerIndex'].item()
                        if isinstance(power_index, int):
                            self.ports_and_guis.GwObj.set_gw_output_power_by_index(power_index)
                        else:
                            raise ValueError(
                                "absGwTxPowerIndex is set for test {} and is not an integer!".format(
                                    test_params['name']))

                    # elif 'tbpTarget' in test_params and 'tbpTarget' != '':
                    #     top_score = get_calibration_results(target_tbp= test_params['tbpTarget'], energy_pattern=test_params['energizingPattern'])
                    #     power_index = int(top_score['absGwTxPowerIndex'].item())
                    #     if isinstance(power_index, int):
                    #         self.ports_and_guis.GwObj.set_gw_output_power_by_index(power_index)
                    #     else:
                    #         raise ValueError(
                    #             "absGwTxPowerIndex is set for test {} and is not an integer!".format(
                    #                 test_params['name']))

                    else:
                        # max output power..
                        power_index = -1
                    curr_tx_power = self.GwObj.valid_output_power_vals[power_index]['abs_power']

                    self.GwObj.config_gw(energy_pattern_val=test_params['energizingPattern'],
                                         received_channel=test_params['rxChannel'],
                                         time_profile_val=test_params['timeProfile'])
                    # GW starts to transmit
                    if timing_prints:
                        printing_func(
                            "after 1st config, time is {}".format(self.GwObj.get_curr_timestamp_in_sec()), 'TagThread',
                            lock_print, logger_type='debug')
                    printing_func(
                        'Changed the GW duty cycle to ' + str(test_params['timeProfile']) + ", energy pattern " + str(
                            test_params['energizingPattern']), 'TagThread',
                        lock_print, logger_type='debug')

                    # self.GwObj.check_current_config()  # for debugging
                    hard_stop = False
                    tags_stats = None
                    while not remained_packets_collected:
                        time.sleep(0)  # to prevent run slowdown by gateway_api

                        # not ((not self.test_suite_times_up \
                        #  and not self.test_times_up or not current_tag_is_certain) and \
                        # not self.duplication_handling_timer_is_done and \
                        # not self.events.pause_to_tag_thread.is_set() and \
                        # not self.events.cont_to_tag_thread.is_set() and not self.events.done_to_tag_thread.is_set()):

                        # Check R2R didn't move:
                        msg_check = self.GwObj.read_specific_message(msg="Start Production Line GW", read_timeout=0,
                                                                     clear=False)
                        if msg_check != '' and self.start_GW_happened:
                            msg = "gw answer is:" + str(gw_answer)
                            printing_func(msg, 'TagThread', lock_print, logger_type='warning')
                            clear_timers()  # verify times are cleared before next tag
                            raise Exception('R2R moved before timer ended')

                        if timing_prints:
                            printing_func("before waiting for packet, time is {}".format(
                                self.GwObj.get_curr_timestamp_in_sec()), 'TagThread',
                                lock_print, logger_type='debug')

                        if test_done:
                            # test completed, turn off energy and collect all remaining packets:
                            time_profile = '0,15'
                            self.GwObj.config_gw(time_profile_val=time_profile, start_gw_app=False)
                            if not hard_stop:  # If not hard stop from timeout or user
                                # get remaining packets - if exists..:
                                if timing_prints:
                                    printing_func("waiting for delayBeforeNextTest to end", 'TagThread',
                                                  lock_print, logger_type='debug')
                                time.sleep(test_params[
                                               'delayBeforeNextTest'])
                                # get remaining packets- give time for uart + CCA (in case some other GW around)
                                if timing_prints:
                                    printing_func("delayBeforeNextTest is done", 'TagThread',
                                                  lock_print, logger_type='debug')
                            gw_answer_list = self.GwObj.get_packets(action_type=ActionType.ALL_SAMPLE,
                                                                    data_type=DataType.PROCESSED, max_time=None)
                            remained_packets_collected = True
                        else:
                            # wait for n packets or timeout:
                            # if we received a packet we will process it and add it to the tag data list
                            gw_answer_list = self.GwObj.get_packets(action_type=ActionType.ALL_SAMPLE,
                                                                    data_type=DataType.PROCESSED, max_time=sample_dt)

                        if gw_answer_list:
                            if timing_prints:
                                printing_func(
                                    "after waiting for packet, time is {}".format(
                                        self.GwObj.get_curr_timestamp_in_sec()), 'TagThread',
                                    lock_print, logger_type='debug')

                            for gw_answer in gw_answer_list:
                                if gw_answer and gw_answer['is_valid_tag_packet']:
                                    # for the tag to keep running until the end of main timer if there was any packet
                                    # self.timer_for_curr_test.cancel()
                                    # in packet decoder we will decide the correct way to decode the packet
                                    try:
                                        proc_packet = Packet(gw_answer)

                                        self.rssi = proc_packet.gw_data['rssi'].take(0)
                                        self.adv_addr = proc_packet.packet_data['adv_address']
                                        if test_params['passTestModePacketsOnly'] == 1:
                                            if not proc_packet.packet_data['adv_address'][2:10].lower() == 'ffffffff':
                                                continue
                                            else:
                                                self.adv_addr = proc_packet.packet_data['adv_address'][:2] + \
                                                                proc_packet.packet_data['nonce'] + \
                                                                proc_packet.packet_data['adv_address'][10:]
                                                proc_packet.packet_data['adv_address'] = self.adv_addr
                                                gw_answer['adv_address'] = self.adv_addr

                                        raw_data = encrypted_packet_decoder(gw_answer)
                                        raw_data['tagLocation'] = self.tag_location
                                        raw_data['commonRunName'] = common_run_name
                                        raw_data['externalId'] = self.printed_external_id
                                        raw_data['rssi'] = self.rssi
                                        raw_data['advAddr'] = self.adv_addr
                                        raw_data['advAddress'] = self.adv_addr
                                        raw_data['gw_time'] = int(raw_data['raw_data'][76:80], 16)
                                        raw_data['packet_data'] = raw_data['raw_data'][:74]
                                        logging.info('packet_decoder result is: ' + str(raw_data))
                                    except Exception:
                                        msg = f'Warning: packet_decoder could not decode packet, will skip {gw_answer}'
                                        printing_func(msg, 'TagThread', lock_print, logger_type='warning')
                                        continue
                                    # this will make sure that we do not have any duplication
                                    # count when there are two new tags simultaneously
                                    self.is_good_packet, self.need_to_check_tbp, packet_status = \
                                        self.tags_handling.encrypted_packet_filter(
                                            gw_answer, test_params['passTestModePacketsOnly'] == 1)

                                    if temperature_sensor_enable:
                                        logging.info('%s' % gw_answer + ', temperatureFromSensor = ' +
                                                     str(temperature_from_sensor))
                                        raw_data['temperatureFromSensor'] = t.get_currentValue()
                                    '''Tomer,16.5.2022, removed- not needed..
                                    # # to open longer timer for understanding what is the current tag
                                    # if self.need_to_check_tbp and current_tag_is_certain:
                                    #     current_tag_is_certain = False
                                    #     clear_timers()
                                    #     self.timer_for_duplication_handling = threading.Timer(
                                    #         self.time_for_duplication_handling,
                                    #         self.end_of_time,
                                    #         ['duplication handling'])
                                    #     self.timer_for_duplication_handling.start()
                                    #     msg = "Need more time to decide what tag is transmitting " \
                                    #           "(due to duplication/ no singularization issue) will open a long timer " \
                                    #           "(" + str(self.time_for_duplication_handling) + \
                                    #           " seconds) for this location and will proceed when it is done"
                                    #     printing_func(msg, 'TagThread', lock_print, do_log=True, logger_type='warning')
                                    '''
                                    raw_data['packetStatus'] = packet_status
                                    raw_data['attenuation'] = curr_atten
                                    raw_data['test_num'] = test_num
                                    raw_data['test_duration'] = curr_test_dur
                                    raw_data['gw_tx_power'] = curr_tx_power
                                    raw_data['rxChannel'] = test_params['rxChannel']

                                    if self.is_good_packet:

                                        curr_test_packets.append(proc_packet)
                                        curr_sprinkler = curr_test_packets.get_sprinkler(proc_packet)
                                        raw_data['tbp'] = curr_sprinkler.get_tbp()
                                        raw_data['packet_count_in_sprinkler'] = len(curr_sprinkler)

                                        chosen_tag_data_list.append(raw_data)
                                        if 'advAddress' in raw_data.keys():
                                            msg = "------- Tag location: " + str(self.tag_location) + " -------" + \
                                                  "------- Tag advAddress: " + str(raw_data['advAddress']) + " -------"
                                            printing_func(msg, 'TagThread', lock_print, do_log=True, logger_type='info')

                                        printing_func(str(gw_answer), 'TagThread', lock_print, do_log=True,
                                                      logger_type='info')

                                    # Debug list contains all packets:
                                    if is_debug_mode:
                                        debug_raw_data = copy.deepcopy(raw_data)
                                        debug_raw_data['packetStatus'] = packet_status
                                        debug_chosen_tag_data_list.append(debug_raw_data)
                                        if self.is_good_packet:
                                            debug_raw_data['tbp'] = raw_data['tbp']

                        # Add test performance check ############################
                        # Get selected tag- if not chosen at prev tests:
                        if self.events.pause_to_tag_thread.is_set() or self.events.cont_to_tag_thread.is_set() or \
                                self.events.done_to_tag_thread.is_set() or \
                                (self.GwObj.get_curr_timestamp_in_sec() - curr_test_start_time > curr_test_dur):
                            # TODO: consider adding or over timeouts- not sure if needed..
                            test_done = True
                            # TODO: add hard stop to shorten tail of last test
                            # hard_stop = True

                        tags_stats, test_done, rssi_diff = check_if_should_end_test(test_done)
                    # Finalize this test results:
                    printing_func("tags_stats = " + str(tags_stats), 'TagThread', lock_print, do_log=True,
                                  logger_type='debug')
                    if test_done and remained_packets_collected:
                        printing_func(f'Anaylizing test results, test_done = {test_done}, remained_packets_collected = '
                                      f'{remained_packets_collected}, chosen tag is  {self.chosen_tag_in_location}',
                                      'TagThread', lock_print, do_log=True, logger_type='debug')
                        all_tests_packets = all_tests_packets + curr_test_packets

                        if self.chosen_tag_in_location is not None:
                            chosen_tag_packets = curr_test_packets.filter_packet_by(
                                values=self.chosen_tag_in_location)
                            num_chosen_packets = chosen_tag_packets.get_num_packets()
                            if num_chosen_packets > 0:
                                if self.sprinkler_counter_max != -1:
                                    if tags_stats[self.chosen_tag_in_location]['sprinkler_counter_max'] < \
                                            self.sprinkler_counter_max:
                                        fail_this_tag = True
                                        printing_func("tag {} will fail because it transmitted more packets than"
                                                      " allowed in 'sprinkler_counter_max'".
                                                      format(self.chosen_tag_in_location),
                                                      'tagResult', lock_print, do_log=True, logger_type='info')
                                if num_chosen_packets > 1 and self.fail_tags_with_same_packet_within_secs:
                                    # filter tags that are not in battery flow (packets are close to each other
                                    for i in range(1, len(chosen_tag_packets.raw_packet_map_list)):
                                        prev_packet = chosen_tag_packets[i - 1].packet_data['raw_packet']
                                        curr_packet = chosen_tag_packets[i].packet_data['raw_packet']
                                        if curr_packet != prev_packet:
                                            # for handling the case of 1 packet
                                            try:
                                                prev_time = float(chosen_tag_packets[i - 1].
                                                                  gw_data['time_from_start'][-1])
                                            except Exception:
                                                prev_time = float(chosen_tag_packets[i - 1].gw_data['time_from_start'])
                                            try:
                                                curr_time = float(chosen_tag_packets[i].gw_data['time_from_start'][0])
                                            except Exception:
                                                curr_time = float(chosen_tag_packets[i].gw_data['time_from_start'])
                                            if (curr_time - prev_time) < \
                                                    self.tests_suite['tests'][test_num][
                                                        'failTagsWithSamePacketWithinSecs']:
                                                fail_this_tag = True
                                                printing_func("tag {} will fail because it is not in "
                                                              "battery flow".format(self.chosen_tag_in_location),
                                                              'tagResult', lock_print, do_log=True, logger_type='info')

                                chosen_tag_statistics = chosen_tag_packets.get_statistics()
                                self.ttfp = chosen_tag_statistics['ttfp']
                                self.tbp = chosen_tag_statistics['tbp_mean']
                                self.rssi = chosen_tag_statistics['rssi_mean']
                                self.tag_appeared_before = self.tags_handling.is_tag_appeared_before(
                                    self.chosen_tag_in_location)
                                printing_func("test {} loc {} chosen tag {} statistics:{} status: {}".format
                                              (test_num, self.tag_location, self.chosen_tag_in_location,
                                               chosen_tag_statistics, test_suite_results[test_num]),
                                              'tagResult', lock_print, do_log=True, logger_type='info')
                            else:
                                printing_func("test {} loc {} chosen tag {} statistics: {}, "
                                              "status: {}".format(test_num, self.tag_location,
                                                                  self.chosen_tag_in_location, "no_packets",
                                                                  test_suite_results[test_num]),
                                              'tagResult', lock_print, do_log=True, logger_type='info')

                            # Check current tag results ##########
                            chosen_tag_packets = curr_test_packets.filter_packet_by(
                                values=self.chosen_tag_in_location)
                            num_chosen_packets = chosen_tag_packets.get_num_packets()
                            self.fatal_gw_error = self.is_gw_respond_with_stat_param_zero(chosen_tag_packets)
                            if not self.tag_is_certain:
                                self.curr_test_pass = False
                                curr_test_fail_reasons += f"Tag is not certain, RSSI diff = {rssi_diff};"
                            elif self.tag_appeared_before:
                                self.curr_test_pass = False
                                curr_test_fail_reasons += f"Failed - duplication! " \
                                                          f"This tag already transmitted at different location;"
                            elif num_chosen_packets > 1 and self.fail_tags_with_same_packet_within_secs:
                                # filter tags that are not in battery flow (packets are close to each other
                                for i in range(1, len(chosen_tag_packets.raw_packet_map_list)):
                                    prev_packet = chosen_tag_packets[i - 1].packet_data['raw_packet']
                                    curr_packet = chosen_tag_packets[i].packet_data['raw_packet']
                                    if curr_packet != prev_packet:
                                        # for handling the case of 1 packet
                                        try:
                                            prev_time = float(chosen_tag_packets[i - 1].
                                                              gw_data['time_from_start'][-1])
                                        except Exception:
                                            prev_time = float(chosen_tag_packets[i - 1].gw_data['time_from_start'])
                                        try:
                                            curr_time = float(chosen_tag_packets[i].gw_data['time_from_start'][0])
                                        except Exception:
                                            curr_time = float(chosen_tag_packets[i].gw_data['time_from_start'])
                                        if (curr_time - prev_time) < \
                                                self.tests_suite['tests'][test_num][
                                                    'failTagsWithSamePacketWithinSecs']:
                                            self.curr_test_pass = False
                                            printing_func("tag {} will fail because it is not in "
                                                          "battery flow (time delta between two different packets is "
                                                          "too low)".format(self.chosen_tag_in_location),
                                                          'tagResult', lock_print, do_log=True, logger_type='info')
                            elif num_chosen_packets < test_params['minPackets']:
                                self.curr_test_pass = False
                                curr_test_fail_reasons += f"Below packet threshold, {num_chosen_packets}<" \
                                                          f"{test_params['minPackets']};"
                                printing_func(f"Test {test_num} failed. Number of packets "
                                              f"{chosen_tag_packets.get_num_packets()} is lower than required "
                                              f"{test_params['minPackets']}", 'tagResult', lock_print, do_log=True,
                                              logger_type='info')
                            else:
                                # Check performance\statistics:
                                if 'statistics_limits' in test_params.keys():
                                    for stat_name in test_params['statistics_limits']:
                                        limits = test_params['statistics_limits'][stat_name]
                                        try:
                                            val = chosen_tag_statistics[stat_name]
                                            if val < limits[0] or val > limits[1]:
                                                self.curr_test_pass = False
                                                curr_test_fail_reasons += f"Failed statistics check of param " \
                                                                          f"{stat_name}={val} not in range " \
                                                                          f"{limits[0]} - {limits[1]}"
                                        except Exception:
                                            self.curr_test_pass = False
                                            curr_test_fail_reasons += f"Failed statistics check, param <<{stat_name}" \
                                                                      f">> not found or had bad limits;"

                                # This test can't fail.. we check the threshold at the filter encrypted packets.
                                # Consider to remove one of them... [Tomer, 14.3.2022]
                                if chosen_tag_statistics['rssi_mean'] > self.tests_suite['rssiThreshold']:
                                    self.curr_test_pass = False
                                    curr_test_fail_reasons += f"Failed test_suite RSSI " \
                                                              f"{chosen_tag_statistics['rssi_mean']}" \
                                                              f" is above test_suite thr of {str(self.tests_suite['rssiThreshold'])}."
                                    printing_func(f"Failed to check RSSI - got {chosen_tag_statistics['rssi_mean']}"
                                                  f", threshold {str(self.tests_suite['rssiThreshold'])} ", 'tagResult', lock_print,
                                                  do_log=True, logger_type='info')

                        else:
                            if test_params['minPackets'] > 0:
                                self.curr_test_pass = False
                                curr_test_fail_reasons += "Could not find tagID candidate"

                        # End of Check current test results ################
                        if fail_this_tag:
                            self.curr_test_pass = False
                        test_suite_results[test_num] = self.curr_test_pass
                        # do not continue to next test..
                        if not test_suite_results[test_num]:
                            break

                    else:
                        # We should not get here!!! this is actually an exception...
                        msg = f'Failed anaylizing test results, test_done = {test_done}, remained_packets_collected = ' \
                              f'{remained_packets_collected}, chosen tag is  {self.chosen_tag_in_location}'
                        printing_func(msg, 'TagThread', lock_print, do_log=True, logger_type='warning')
                        raise ValueError("Code reached else at tagthread which is not valid!!!")

                        # end of packet loop ###############

                    # end of curr test events loop ###############
                    if "stopAfterPassInLastTest" in self.tests_suite.keys():
                        if self.tests_suite['stopAfterPassInLastTest'] == 'True':
                            if test_suite_results[-1] is True:
                                break
        # End of all tests - process data and update files ############################################################

        # Prepare for next tag PL delay:
        # self.GwObj.write("!cancel")
        self.GwObj.set_gw_max_output_power()

        packets_time_diff = None
        #
        # # to resolve what is the tag that was tested
        # if not current_tag_is_certain:
        #     self.adv_addr, self.tag_appeared_before, packets_time_diff = \
        #         self.tags_handling.get_estimated_tag_in_location()
        #     # for the case of no packet was received
        #     if self.adv_addr is None:
        #         chosen_tag_data_list = []
        #     else:
        #         # this will pass tags that transmitted enough packets even if it was received after the timer ended
        #         # this is a temporary fix so the post-process will not collapse
        #
        #

        if self.fatal_gw_error:
            failed_test = 0
            chosen_tag_status = 'Fatal GW error- error got reset during the run'
            #TODO: find a way to not fail this tag..
            msg = 'Fatal GW error - resting the GW and failing this tag'
            printing_func(msg, 'TagThread', lock_print, logger_type='warning')
            fail_this_tag = True
            self.reset_and_init_gw()
        elif not self.start_GW_happened:
            failed_test = 0
            fail_this_tag = True
            chosen_tag_status = 'GW did not send start indication'
        elif False in test_suite_results:
            failed_test = test_suite_results.index(False)
            chosen_tag_status = 'Failed test {}, reason:{}'.format(failed_test, curr_test_fail_reasons)
            fail_this_tag = True
        elif fail_this_tag:
            #Not sure how we can get here... but just to be on the safe side:
            failed_test = test_num #Assume the last test failed...
            chosen_tag_status = 'Decided to fail_this_tag, see log for more details'.format(failed_test, curr_test_fail_reasons)
        else:
            chosen_tag_status = 'Pass'
            fail_this_tag = False

        # logging ####################
        # TODO: move to packet list usage..
        if len(chosen_tag_data_list) > 0:
            df_chosen_tag_data_list = pd.DataFrame(chosen_tag_data_list)
            df_chosen_tag_data_list = df_chosen_tag_data_list.loc[df_chosen_tag_data_list['advAddress'] == self.chosen_tag_in_location]
            chosen_tag_data_list = df_chosen_tag_data_list.to_dict('records')

        if len(chosen_tag_data_list) > 0:
            # TODO: replace with packet_list get stattistics, this is duplicated calculation..
            packets_data = process_encrypted_tags_data(data=chosen_tag_data_list,
                                                       packet_threshold=int(self.value['packetThreshold']),
                                                       fail_this_tag=self.tag_appeared_before or fail_this_tag or chosen_tag_status != 'Pass',
                                                       adv_of_selected_tag=self.adv_addr)

        # adding the packets from this location to packets_data_log
        if packets_data_log is None:
            packets_data_log = CsvLog(header_type=HeaderType.PACKETS, path=packets_data_path,
                                      tester_type=TesterName.OFFLINE,
                                      temperature_sensor=temperature_sensor_enable)
            packets_data_log.open_csv()
            printing_func("packets_data log file has been created", 'TagThread',
                          lock_print, do_log=False, logger_type='debug')

        desired_keys = ['externalId', 'tagLocation', 'packetStatus', 'temperatureFromSensor', 'commonRunName',
                        'encryptedPacket', 'time', 'attenuation', 'gw_tx_power', 'advAddr', 'rssi', 'packet_data',
                        'gw_time', 'tbp', 'test_num', 'test_duration']

        for i in range(len(debug_chosen_tag_data_list)):
            tmp_packet_dict = {'chosenTagInLocation': self.chosen_tag_in_location,
                               'chosenTagStatus': chosen_tag_status}

            for key in debug_chosen_tag_data_list[i]:
                if key == 'packet_time':
                    tmp_packet_dict['time'] = debug_chosen_tag_data_list[i][key]
                if key == 'raw_data':
                    tmp_packet_dict['encryptedPacket'] = debug_chosen_tag_data_list[i][key]
                elif key in desired_keys:
                    tmp_packet_dict[key] = debug_chosen_tag_data_list[i][key]
            packets_data_log.append_list_as_row(packets_data_log.dict_to_list(tmp_packet_dict))

        # for the previous tag print - make sure the last tag was printed:
        # if self.to_print:
        #     logging.info('Making sure printer doesnt have failures')
        #     self.done_or_printer_event.wait(timeout=10)
        ##########################################################

        # run final new_tag checks before moving to the next location:
        # ------------------------------------------------
        # check if the stop button was pressed:
        if self.events.done_to_tag_thread.is_set():
            clear_timers()
            self.events.was_fail_to_printer.set()  # to avoid deadlock
            logging.info("The User pressed STOP")
            logging.debug('stop pressed after start GW happened. the last tag will be ignored')
            return 'Exit'
        # check if the pause button was pressed:
        elif self.events.pause_to_tag_thread.isSet():
            if self.events.done_to_tag_thread.isSet():
                clear_timers()
                return
            else:
                clear_timers()
                self.events.cont_to_tag_thread.wait()
                self.events.cont_to_tag_thread.clear()
                self.events.pause_to_tag_thread.clear()
                self.events.cont_to_main_thread.set()
        # check if the continue button was pressed:
        elif self.events.cont_to_tag_thread.isSet():
            self.events.cont_to_tag_thread.clear()
            self.events.pause_to_tag_thread.clear()
            self.events.cont_to_main_thread.set()
        # check if we received enough packets to pass the current tag:
        elif chosen_tag_status == 'Pass':

            data = packets_data
            if tags_data_log is None:
                tags_data_log = CsvLog(header_type=HeaderType.TAG, path=tags_data_path,
                                       tester_type=TesterName.OFFLINE,
                                       temperature_sensor=temperature_sensor_enable)
                tags_data_log.open_csv()
                printing_func("tags_data log file has been created", 'TagThread',
                              lock_print, do_log=False, logger_type='debug')
            tags_data_log.append_list_as_row(tags_data_log.dict_to_list(data))

            if is_debug_mode:
                debug_data = process_encrypted_tags_data(data=debug_chosen_tag_data_list,
                                                         packet_threshold=int(self.value['packetThreshold']),
                                                         fail_this_tag=self.tag_appeared_before or fail_this_tag,
                                                         # Can not arrive here...
                                                         is_debug_mode=True,
                                                         packets_time_diff=packets_time_diff,
                                                         adv_of_selected_tag=self.adv_addr)
                if debug_tags_data_log is None:
                    debug_tags_data_log = CsvLog(header_type=HeaderType.TAG, path=debug_tags_data_path,
                                                 tester_type=TesterName.OFFLINE,
                                                 temperature_sensor=temperature_sensor_enable,
                                                 is_debug_mode=is_debug_mode)
                    debug_tags_data_log.open_csv()
                    printing_func("debug_tags_data log file has been created", 'TagThread',
                                  lock_print, do_log=False, logger_type='debug')
                debug_tags_data_log.append_list_as_row(debug_tags_data_log.dict_to_list(debug_data))

            printing_func("The data to the classifier is: " + str(data), 'TagThread',
                          lock_print, do_log=False, logger_type='info')  # the tag is good
            self.printed_external_id, is_OK = get_printed_value(self.printing_value['stringBeforeCounter'],
                                                                self.printing_value['digitsInCounter'],
                                                                str(self.externalId), self.value['printingFormat'])
            if not is_OK:
                clear_timers()
                msg = 'printing counter reached a value that is bigger than the counter possible space.' \
                      ' the program will exit now'
                printing_func(msg, 'TagThread', lock_print, logger_type='warning')
                sys.exit(0)
            temperature_msg = 'NA'

            try:
                temperature_msg = data['temperatureFromSensor']
            except Exception:
                temperature_msg = 'NA'

            try:
                msg = "*****************Tag with advAddress " + str(raw_data['advAddress']) + \
                      " has passed, tag location is " + str(self.tag_location) + ' , ' + \
                      str({'advAddress': str(raw_data['advAddress']), 'externalId': self.printed_external_id,
                           'temperatureFromSensor': temperature_msg, 'test_time' : str(self.get_curr_timestamp_in_sec())})  + '*****************'
                printing_func(msg, 'TagThread', lock_print, logger_type='info')

            except Exception:
                clear_timers()
                msg = "*****************Tag with advAddress " + str(raw_data['advAddress']) + \
                      " has passed, tag location is " + str(self.tag_location) + ' , ' + \
                      str({'advAddress': str(raw_data['advAddress']), 'externalId': self.printed_external_id,
                           'temperatureFromSensor': temperature_msg}) + '*****************'
                printing_func(msg, 'TagThread', lock_print, logger_type='info')

            if not self.to_print:
                self.events.r2r_ready.clear()
            if self.qr_enable == 'Yes':
                if self.events.qr_read_success.is_set():
                    self.events.qr_read_success.clear()
                    qr_que_list.append({'externalID': self.printed_external_id, 'status': 'Pass'})
            self.events.pass_to_r2r_thread.set()
            global passed
            passed += 1
            global last_pass_string
            last_pass_string = f'advAddress: {str(self.chosen_tag_in_location)} , Tag Location:  ' \
                               f'{str(self.tag_location)} , External ID: {self.printed_external_id} , RSSI: ' \
                               f'{self.rssi}, TBP: {self.tbp}, TTFP: {self.ttfp}'
            if self.to_print:
                self.events.was_pass_to_printer.set()
                self.externalId += 1

                payload = raw_data['raw_data']
                if self.ports_and_guis.do_serialization:
                    if len(self.next_batch_to_serialization['upload_data']) == 0:
                        self.next_batch_to_serialization = {'response': '',
                                                            'upload_data': [{"payload": payload,
                                                                             "tagId": self.printed_external_id}],
                                                            'writing_lock': threading.Lock(), 'failed_already': False}
                    else:
                        self.next_batch_to_serialization['upload_data'].append({"payload": payload,
                                                                                "tagId": self.printed_external_id})
            else:
                self.externalId += 1
            if packets_data['Ttfgp'] is not None:
                self.ttfgp_list.append(float(packets_data['Ttfgp']))

        # # tag did not transmit for too long (self.value['maxTtfp']
        # elif self.test_times_up:
        #     if self.start_GW_happened:
        #         self.missing_labels_in_a_row = 0
        #     logging.warning(
        #       "Tag {} hasfailed! did not transmit for {} seconds".format(str(tested), str(self.value['maxTtfp'])))
        #
        #     if not self.to_print:
        #         self.events.r2r_ready.clear()
        #     self.events.fail_to_r2r_thread.set()
        #     if self.to_print:
        #         self.events.was_fail_to_printer.set()
        # time is up  - tag failed
        elif self.start_GW_happened:
            # TODO: combine with pass tags logging
            logging.debug("Tag failed")
            # write the data of the tag in case it failed with packets
            if len(chosen_tag_data_list) > 0:
                data = packets_data
                under_threshold += 1
                if tags_data_log is None:
                    tags_data_log = CsvLog(header_type=HeaderType.TAG, path=tags_data_path,
                                           tester_type=TesterName.OFFLINE,
                                           temperature_sensor=temperature_sensor_enable)
                    tags_data_log.open_csv()
                    printing_func("tags_data log file has been created", 'TagThread',
                                  lock_print, do_log=False, logger_type='debug')
                tags_data_log.append_list_as_row(tags_data_log.dict_to_list(data))
                printing_func("The data to the classifier is: " + str(data), 'TagThread',
                              lock_print, do_log=False, logger_type='info')

            if is_debug_mode and len(debug_chosen_tag_data_list) > 0:
                adv_of_selected_tag = None
                if len(chosen_tag_data_list) > 0:
                    df = pd.DataFrame(chosen_tag_data_list)
                    adv_of_selected_tag = df['advAddress'].iloc[0]

                debug_data = process_encrypted_tags_data(data=debug_chosen_tag_data_list,
                                                         packet_threshold=int(self.value['packetThreshold']),
                                                         fail_this_tag=True,
                                                         is_debug_mode=True,
                                                         packets_time_diff=packets_time_diff,
                                                         adv_of_selected_tag=adv_of_selected_tag)
                if debug_tags_data_log is None:
                    debug_tags_data_log = CsvLog(header_type=HeaderType.TAG, path=debug_tags_data_path,
                                                 tester_type=TesterName.OFFLINE,
                                                 temperature_sensor=temperature_sensor_enable,
                                                 is_debug_mode=is_debug_mode)
                    debug_tags_data_log.open_csv()
                    printing_func("debug_tags_data log file has been created", 'TagThread',
                                  lock_print, do_log=False, logger_type='debug')
                debug_tags_data_log.append_list_as_row(debug_tags_data_log.dict_to_list(debug_data))

            # write the log if there were any packets.
            if len(chosen_tag_data_list) > 0:
                if 'tag_id' in raw_data.keys():
                    logging.info("Tag {} has failed!".format(str(raw_data['tag_id'])))
                elif 'advAddress' in raw_data.keys():
                    logging.info("Tag with advAddress {} has failed!".format(str(raw_data['advAddress'])))
            if not self.to_print:
                self.events.r2r_ready.clear()
            if self.qr_enable == 'Yes':
                if self.events.qr_read_success.is_set():
                    self.events.qr_read_success.clear()
                    qr_que_list.append({'externalID': (self.printed_external_id), 'status': 'Fail'})
            self.events.fail_to_r2r_thread.set()
            if self.to_print:
                self.events.was_fail_to_printer.set()
            logging.warning('Location {} has failed, reason: {}'.format(str(int(self.tag_location)), chosen_tag_status))

        # missing label
        elif self.r2r_response_times_up:
            self.start_GW_happened = False

            msg = 'R2R has not move for ' + str(self.time_out_to_missing_label) + \
                  ' seconds , enforce a start_r2r & fail_r2r (the last spot will be fail)'
            printing_func(msg, 'TagThread', lock_print, logger_type='debug')
            missing_labels += 1

            # will take care of the missing labels in a row situation
            if self.missing_labels_in_a_row > 0:
                self.missing_labels_in_a_row += 1
            else:
                self.missing_labels_in_a_row = 1

            if self.events.done_to_tag_thread.isSet():
                clear_timers()
                return
            else:
                if not self.is_missing_label_mode:
                    msg = 'missing label has been detected. The R2R will stop now'
                    printing_func(msg, 'TagThread', lock_print, logger_type='warning')
                    printing_func('Please check the reel is OK and press Continue', 'TagThread', lock_print,
                                  do_log=False, logger_type='warning')
                    self.events.stop_to_r2r_thread.set()
                    self.GwObj.stop_continuous_listener()
                    self.events.cont_to_tag_thread.wait()
                    self.GwObj.start_continuous_listener()
                    self.missing_labels_in_a_row = 0
                    self.events.cont_to_tag_thread.clear()
                    self.events.cont_to_main_thread.set()
                elif self.missing_labels_in_a_row > int(self.value['maxMissingLabels']):
                    msg = str(self.missing_labels_in_a_row) \
                          + ' missing labels in a row has been detected. The R2R will stop now'
                    printing_func(msg, 'TagThread', lock_print, logger_type='warning')
                    printing_func('Please check the reel is OK and press Continue', 'TagThread', lock_print,
                                  do_log=False, logger_type='warning')
                    self.events.stop_to_r2r_thread.set()

                    if (len(self.next_batch_to_serialization[
                                'upload_data']) == self.num_of_tags_per_upload_batch or len(
                        self.next_batch_to_serialization[
                            'upload_data']) > 0) and self.to_print and self.ports_and_guis.do_serialization:
                        logging.info(
                            'Starting Serialization process since max number of missing labels detected - might be end of run')
                        self.serialization_data_for_all_run.append(self.next_batch_to_serialization)
                        self.next_batch_to_serialization = {'response': '', 'upload_data': [], 'failed_already': False}
                        self.serialize_status = check_serialization_exception_queues(self.serialization_threads_working,
                                                                                     printing_lock=lock_print)

                        self.serialization_threads_working.append(
                            SerializationAPI(batch_dictionary=self.serialization_data_for_all_run[-1], to_logging=True,
                                             security_client=self.management_client.auth_obj,
                                             try_serialize_again=self.events.try_serialize_again,
                                             printing_lock=lock_print,
                                             env=self.ports_and_guis.env))
                        self.serialization_threads_working[-1].start()

                    if not self.serialize_status:
                        msg = 'Serialization failed'
                        printing_func(msg, 'TagThread', lock_print, logger_type='warning')

                    self.GwObj.stop_continuous_listener()
                    self.events.cont_to_tag_thread.wait()
                    self.GwObj.start_continuous_listener()
                    self.missing_labels_in_a_row = 0
                    self.events.cont_to_tag_thread.clear()
                    self.events.cont_to_main_thread.set()
                else:
                    msg = str(self.missing_labels_in_a_row) + ' missing labels in a row has been detected'
                    printing_func(msg, 'TagThread', lock_print, logger_type='warning')
                    if not self.to_print:
                        self.events.r2r_ready.clear()
                    # global qr_que_list
                    if self.qr_enable == 'Yes':
                        if self.events.qr_read_success.is_set():
                            self.events.qr_read_success.clear()
                            qr_que_list.append({'externalID': self.printed_external_id, 'status': 'Fail'})
                    self.events.start_to_r2r_thread.set()
            logging.warning('Tag {} has failed due to Missing Label'.format(str(self.tag_location)))

        # check if printer error occurs:
        elif self.to_print:  # will use it only before self.start_GW_happened
            logging.info('Waiting for printer feedback')
            self.done_or_printer_event.wait(timeout=5)
            self.events.printer_success.clear()
            if self.events.done_to_tag_thread.isSet():
                clear_timers()
                return
            # to make sure that the tag thread will not proceed if an error occur
            if self.events.printer_error.isSet():
                if self.events.done_to_tag_thread.isSet():
                    clear_timers()
                    return
                else:
                    self.events.cont_to_tag_thread.wait()
                    self.events.cont_to_tag_thread.clear()
                    self.events.pause_to_tag_thread.clear()
                    self.events.cont_to_main_thread.set()
                    self.events.printer_error.clear()
            else:
                self.events.printer_success.clear()

        # doing it last for the case of printer crash in the middle of the new_tag()
        global external_id_for_printer
        external_id_for_printer = self.externalId
        clear_timers()

    def closure_fn(self):
        """
           turn off the GW (reset) and closes the GW Comport
           Logging:
               'User pressed Stop!'
           """
        global failed_tags, run_data_dict, problem_in_locations_hist
        # for the case that the Button was pressed after a long time (the token expires)
        try:
            success = get_new_token_api()
        except Exception as e:
            printing_func("Failed to get token", 'TagThread', lock_print, logger_type='warning')

        if not success:
            printing_func('get_new_token_api() failed', 'TagThread', lock_print, logger_type='warning')
        if self.ports_and_guis.do_serialization:
            failed_tags = close_all_serialization_processes_when_they_done(
                self.serialization_threads_working, to_logging=True, printing_lock=lock_print,
                try_serialize_again=self.events.try_serialize_again)
            # run_data_dict['TagsFaildSerialization'] = failed_tags
            # TODO add this lines to save tags that failed serialization
        problem_in_locations_hist = self.tags_handling.problem_in_locations_hist
        self.GwObj.stop_processes()
        self.GwObj.reset_buffer()
        self.GwObj.write('!reset')
        self.GwObj.close_port(is_reset=True)
        printing_func("TagThread is done", 'TagThread',
                      lock_print, logger_type='debug')


class R2RThread(threading.Thread):
    """
    Thread that controls R2R machine

    Parameters:
        @type events: class MainEvents (costume made class that has all of the Events of the program threads)
        @param events: has all of the Events of the program threads
        @type ports_and_guis: class PortsAndGuis (costume made class that has all of the ports and gui inputs for the
              program threads)
        @param ports_and_guis: has all of the ports and gui inputs for the program threads

    Exceptions:

    @except Exception: 'r2r_thread got an Exception, press Continue or Stop'
            exception details will be printed
            Exception might be either:
                1. Send GPIO pulse failed
                2. GPIO pulse was sent twice

    Events:
        listen/ waits on:
        events.done_or_stop => event that equals to (events.done_to_r2r_thread OR events.stop_to_r2r_thread)
        events.done_to_r2r_thread => kills R2R thread main loop if set
        events.pass_to_r2r_thread => notify if current tag passed. if set, send pulse on "Pass" GPIO line
        events.fail_to_r2r_thread => notify if current tag failed. if set, send pulse on "Fail" GPIO line
        events.start_to_r2r_thread => enable/disable R2R movement. Sends pulse on "Start/Stop machine" GPIO line
        events.enable_missing_label_to_r2r_thread => notify if missing label mode is enabled
            (skips current tag location in case of missing label up to maxMissingLabels set by user)


        sets:
        events.r2r_ready => notify if R2R in ready for movement
        events.stop_to_r2r_thread => stops the R2R from running in case of end of run or exception

    Logging:
        the logging from this thread will be to logging.debug()
        """

    def __init__(self, events, ports_and_guis):
        """
        Initialize Constants
        """
        super(R2RThread, self).__init__(daemon=True)
        self.exception_queue = Queue()
        self.events = events
        self.done_or_stop = or_event_set(self.events.done_to_r2r_thread, self.events.stop_to_r2r_thread)
        self.r2r_events_or = or_event_set(self.events.pass_to_r2r_thread, self.events.fail_to_r2r_thread,
                                          self.events.start_to_r2r_thread, self.done_or_stop,
                                          self.events.enable_missing_label_to_r2r_thread)
        self.en_missing_label = False
        self.ports_and_guis = ports_and_guis

        self.my_gpio = self.ports_and_guis.R2R_myGPIO

    @pyqtSlot()
    def run(self):
        """
        runs the thread
        """
        die = False
        while not die:
            try:
                self.r2r_events_or.wait()
                if self.done_or_stop.is_set():
                    self.my_gpio.gpio_state(3, "OFF")
                    msg = "PC send stop to R2R"
                    printing_func(msg, 'R2RThread', lock_print, logger_type='debug')
                    self.events.stop_to_r2r_thread.clear()
                    if self.events.done_to_r2r_thread.isSet():
                        logging.warning('Job is done')
                        die = True

                if self.events.start_to_r2r_thread.is_set():
                    if self.en_missing_label:
                        msg = "PC send stop + start + fail to R2R"
                        printing_func(msg, 'R2RThread', lock_print, logger_type='debug')
                        self.my_gpio.gpio_state(3, "OFF")
                        time.sleep(0.5)  # just to be on the safe side
                    else:
                        msg = "PC send start + fail to R2R"
                        printing_func(msg, 'R2RThread', lock_print, logger_type='debug')
                    self.my_gpio.gpio_state(3, "ON")
                    time.sleep(0.5)  # just to be on the safe side
                    self.my_gpio.pulse(2, 50)
                    self.events.r2r_ready.set()
                    self.events.start_to_r2r_thread.clear()

                if self.events.pass_to_r2r_thread.is_set():
                    msg = "^^^^^^^^^^^^^^^^^^ PC send pass to R2R ^^^^^^^^^^^^^^^^^^"
                    printing_func(msg, 'R2RThread', lock_print, logger_type='debug')
                    self.my_gpio.pulse(1, 50)
                    self.events.pass_to_r2r_thread.clear()
                    self.events.r2r_ready.set()

                if self.events.fail_to_r2r_thread.is_set():
                    msg = "PC send fail to R2R"
                    printing_func(msg, 'R2RThread', lock_print, logger_type='debug')
                    self.my_gpio.pulse(2, 50)
                    self.events.fail_to_r2r_thread.clear()
                    self.events.r2r_ready.set()

                if self.events.enable_missing_label_to_r2r_thread.is_set():
                    msg = "PC send 'enable missing label' to R2R"
                    printing_func(msg, 'R2RThread', lock_print, logger_type='debug')
                    self.my_gpio.gpio_state(4, "ON")
                    self.events.enable_missing_label_to_r2r_thread.clear()
                    self.en_missing_label = True
                if self.events.disable_missing_label_to_r2r_thread.is_set():
                    msg = "PC send 'disable missing label' to R2R"
                    printing_func(msg, 'R2RThread', lock_print, logger_type='debug')
                    self.my_gpio.gpio_state(4, "OFF")
                    self.events.disable_missing_label_to_r2r_thread.clear()
                    self.en_missing_label = False
            except Exception:
                exception_details = sys.exc_info()
                self.exception_queue.put(exception_details)
                self.events.stop_to_r2r_thread.set()  # to avoid from the run to continue printing in this case
                self.events.cont_to_tag_thread.wait()


class MainEvents:
    """
    Contains events that connect between all threads
    Events are set or cleared by threads
    Events are divided to four primary groups:
        1. TagThread events
        2. MainWindow events
        3. R2R (reel to reel machine) events
        4. Printer events

    Parameters: None
    Exceptions: None
    Events: None
    Logging: None
    """

    def __init__(self):
        """
        Initialize the events for the entire run
        """

        # set by tag_checker
        self.pass_to_r2r_thread = threading.Event()
        self.fail_to_r2r_thread = threading.Event()
        # set by main
        self.start_to_r2r_thread = threading.Event()
        self.stop_to_r2r_thread = threading.Event()
        self.cont_to_tag_thread = threading.Event()
        # only to be sure we initialize the counters to the printer counter
        self.cont_to_printer_thread = threading.Event()
        self.cont_to_main_thread = threading.Event()
        self.pause_to_tag_thread = threading.Event()
        self.enable_missing_label_to_r2r_thread = threading.Event()
        self.disable_missing_label_to_r2r_thread = threading.Event()
        self.done_to_tag_thread = threading.Event()
        self.done_to_printer_thread = threading.Event()
        self.done2r2r_ready = threading.Event()
        self.done_to_r2r_thread = threading.Event()
        self.tag_thread_is_ready_to_main = threading.Event()
        self.try_serialize_again = threading.Event()

        # set by r2r
        # both printer and tag thread will wait on it. only printer will .clear() it (in printing mode)
        self.r2r_ready = threading.Event()

        # printer events
        self.was_pass_to_printer = threading.Event()
        self.was_fail_to_printer = threading.Event()
        self.printer_success = threading.Event()
        self.printer_error = threading.Event()
        self.printer_event = or_event_set(self.printer_success, self.printer_error)

        # being used in printer thread too
        self.r2r_ready_or_done2tag = or_event_set(self.r2r_ready, self.done2r2r_ready)

        # start qr read_out
        self.start_qr_scan = threading.Event()
        self.qr_read_success = threading.Event()


class PortsAndGuis:
    """
    class which is responsible for initializing peripheral's ports and get data from run GUIs

    Parameters: None
    Exceptions: None
    Events: None
    Logging: None
    """

    def __init__(self):
        """
        Initialize the runs ports and gets data from the guis
        """
        self.dir_config = 'configs'
        self.tests_suites_configs_path = join(self.dir_config, 'tests_suites.json')
        # Get tests:
        with open(self.tests_suites_configs_path, 'r') as f:
            self.all_tests_suites = json.load(f)

        # run values (1st GUI)
        self.Tag_Value = open_session(inlay_type_list=list(self.all_tests_suites.keys()))
        # Getting the config values
        self.init_config_values()

        self.tests_suite = self.all_tests_suites[self.Tag_Value['inlayType']]
        self.serialize_status = True
        # for Tag thread ###########
        # check if production mode or test mode to set environment for cloud_api
        global env
        if self.Tag_Value['prodMode']:
            self.env = ''
        else:
            self.env = '/test'
        env = self.env
        print('Starting run in {} mode'.format(str(self.env)))
        # printing values (2nd GUI)
        self.do_serialization = False
        if self.Tag_Value['toPrint'] == 'Yes':
            self.to_print = True
            self.do_serialization = True
            if self.Tag_Value['printingFormat'] == 'Test':
                self.Tag_Printing_Value, self.Tag_is_OK = printing_test_window(self.env)
                if not self.Tag_is_OK:
                    msg = 'Impossible printing values entered by the user, the program will exit now'
                    printing_func(msg, 'PortsAndGuis', lock_print, logger_type='debug')
                    sys.exit(0)
                self.do_serialization = False
            elif self.Tag_Value['printingFormat'] == 'SGTIN':
                self.Tag_Printing_Value, self.Tag_is_OK = printing_sgtin_window(self.env)
                if not self.Tag_is_OK:
                    msg = 'user exited the program'
                    printing_func(msg, 'PortsAndGuis', lock_print, logger_type='debug')
                    sys.exit(0)
            else:
                msg = 'user chose unsupported printing format!!!'
                printing_func(msg, 'PortsAndGuis', lock_print, logger_type='debug')
        # path for log file

        self.env_dirs = WiliotDir()
        self.WILIOT_DIR = self.env_dirs.get_wiliot_root_app_dir()

        self.machine_dir = join(self.WILIOT_DIR, 'offline')
        self.logs_dir = join(self.machine_dir, 'logs')
        self.new_path = join(self.logs_dir, str(self.Tag_Value['batchName']))
        # new_path = 'logs/' + str(self.Tag_Value['batchName'])
        if not os.path.exists(self.new_path):
            os.makedirs(self.new_path)
        global log_path, R2R_code_version
        global run_start_time, common_run_name
        global reel_name
        reel_name = self.Tag_Value['batchName'].rstrip()
        common_run_name = reel_name + run_start_time
        self.Tag_pathForLog = join(self.new_path, common_run_name + '@ver=' + R2R_code_version + '.log')
        # self.Tag_pathForLog = self.Tag_pathForLog.replace(':', '-')
        log_path = self.Tag_pathForLog
        print(self.Tag_pathForLog)
        # save the reel & log name for upload to the cloud at the end
        logging.getLogger().setLevel(logging.DEBUG)
        write_handler = logging.FileHandler(self.Tag_pathForLog, mode='a')
        formatter = logging.Formatter('%(asctime)s,%(msecs)d  %(levelname)s %(message)s')
        write_handler.setFormatter(formatter)
        logging.getLogger().addHandler(write_handler)
        self.auto_attenuator_enable = False

        self.config_equipment(temperature_sensor=True, attenuator=False)

        # check if the system variable exist
        assert ('testerStationName' in os.environ), 'testerStationName is missing from PC environment variables, ' \
                                                    'please add it in the following convention:' \
                                                    ' <company name>_<tester number>'
        self.tag_tester_station_name = os.environ['testerStationName']
        # serial for GW
        self.GwObj = WiliotGateway(auto_connect=True, logger_name='root', lock_print=lock_print)
        ver, __ = self.GwObj.get_gw_version()
        assert (int(ver.split('.')[0], 16) >= 3 and int(ver.split('.')[1], 16) >= 5 and int(ver.split('.')[2][0],
                                                                                  16) >= 2), \
            'GW version should be at least 3.5.2 to support accurate timing measurement'
        # for Printer thread ###########
        self.Printer_socket = ''  # will only be opened by the thread
        if self.Tag_Value['printingFormat'] == 'Test':
            self.filename = 'gui_printer_inputs_4_Test_do_not_delete.json'
        elif self.Tag_Value['printingFormat'] == 'SGTIN':
            self.filename = 'gui_printer_inputs_4_SGTIN_do_not_delete.json'

        else:
            msg = 'The print Job Name inserted is not supported at the moment, You will need to press Stop'
            printing_func(msg, 'PortsAndGuis', lock_print, logger_type='debug')

        # check printing configs and save it locally
        self.folder_path = 'configs'
        self.data_for_printing = open_json(folder_path=self.folder_path,
                                           file_path=os.path.join(self.folder_path, self.filename),
                                           default_values=DefaultGUIValues(
                                               self.Tag_Value['printingFormat']).default_gui_values)

        # create log filenames join(new_path,
        global run_data_path, tags_data_path, packets_data_path, debug_tags_data_path
        # self.tags_data_path = new_path + '/' + common_run_name + '@offline_tester@tags_data' + \
        #                                                          '@ver=' + R2R_code_version + '.csv'

        self.tags_data_path = join(self.new_path, common_run_name + '@offline_tester@tags_data' +
                                   '@ver=' + R2R_code_version + '.csv')
        # self.tags_data_path = self.tags_data_path.replace(':', '-')
        self.debug_tags_data_path = join(self.new_path, common_run_name + '@offline_tester@debug_tags_data' +
                                         '@ver=' + R2R_code_version + '.csv')
        # self.debug_tags_data_path = self.debug_tags_data_path.replace(':', '-')
        self.run_data_path = join(self.new_path, common_run_name + '@offline_tester@run_data' +
                                  '@ver=' + R2R_code_version + '.csv')
        # self.run_data_path = self.run_data_path.replace(':', '-')
        self.packets_data_path = join(self.new_path, common_run_name + '@offline_tester@packets_data@ver=' +
                                      R2R_code_version + '.csv')
        # self.packets_data_path = self.packets_data_path.replace(':', '-')
        run_data_path = self.run_data_path
        tags_data_path = self.tags_data_path
        debug_tags_data_path = self.debug_tags_data_path
        packets_data_path = self.packets_data_path
        # create log files
        global tags_data_log, debug_tags_data_log, is_debug_mode, packets_data_log
        if tags_data_log is None:
            tags_data_log = CsvLog(header_type=HeaderType.TAG, path=tags_data_path, tester_type=TesterName.OFFLINE,
                                   temperature_sensor=temperature_sensor_enable)
            tags_data_log.open_csv()
            printing_func("tags_data log file has been created", 'TagThread',
                          lock_print, do_log=False, logger_type='debug')
        if is_debug_mode and debug_tags_data_log is None:
            debug_tags_data_log = CsvLog(header_type=HeaderType.TAG, path=debug_tags_data_path,
                                         tester_type=TesterName.OFFLINE,
                                         temperature_sensor=temperature_sensor_enable,
                                         is_debug_mode=is_debug_mode)
            debug_tags_data_log.open_csv()
            printing_func("debug_tags_data log file has been created", 'TagThread',
                          lock_print, do_log=False, logger_type='debug')
        if packets_data_log is None:
            packets_data_log = CsvLog(header_type=HeaderType.PACKETS, path=packets_data_path,
                                      tester_type=TesterName.OFFLINE, temperature_sensor=temperature_sensor_enable)
            packets_data_log.open_csv()
            printing_func("packets_data log file has been created", 'TagThread',
                          lock_print, do_log=False, logger_type='debug')
        # for R2R thread ###########
        self.R2R_myGPIO = R2rGpio()

    def open_printer_socket(self):
        """
        opens the printer socket
        """
        self.Printer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.Printer_socket.connect((self.configs_for_printer_values['TCP_IP'],
                                     int(self.configs_for_printer_values['TCP_PORT'])))

    def update_printer_gui_inputs(self):
        """
        save the last pass value for crash support.
        passed global variable will be updated at tag Thread and should be correct here
        """
        self.data_for_printing['firstPrintingValue'] = str(int(self.data_for_printing['firstPrintingValue']) + 1)
        file_path = os.path.join('configs', self.filename)
        json.dump(self.data_for_printing, open(file_path, "w"))

    def init_config_values(self):
        """
        initialize the config values for the run
        """

        config_defaults = ConfigDefaults()

        self.configs_for_printer_file_values_path = self.dir_config + '/configs_for_printer_values.json'
        self.configs_for_printer_values = open_json(self.dir_config, self.configs_for_printer_file_values_path,
                                                    config_defaults.get_printer_defaults())

    def config_attenuator(self):
        """
        configs attenuator for this run
        :Return: True if configuration found and attenuator was configured successfully, False otherwise
        """
        if not self.auto_attenuator_enable:
            msg = "according to configs.test_configs (AutoAttenuatorEnable) automatic attenuator is not connected, " \
                  "or should not be used."
            printing_func(str_to_print=msg, logging_entity='PortsAndGuis', lock_print=lock_print,
                          do_log=True, logger_type='debug')
            try:
                attn = set_calibration_attn(set_optimal_attn=False)
                if attn is None:
                    msg = "failed to set attenuation"
                else:
                    msg = 'Attenuation is set (' + str(attn) + "dB)"
            except EquipmentError:
                msg = 'was not able to open port to Attenuator, will continue this run without attenuator configuration'

            except Exception:
                msg = 'was not able to open json with attenuator config data, will continue this run without ' \
                      'attenuator configuration'
        else:
            try:
                tmp_path = os.path.join('..', 'configs/equipment_config.json')
                attn = set_calibration_attn(set_optimal_attn=True, config_path=tmp_path)
                if attn is None:
                    msg = "failed to set attenuation, you will need to press Stop"
                    printing_func(str_to_print=msg, logging_entity='PortsAndGuis', lock_print=lock_print,
                                  do_log=True, logger_type='debug')
                    raise Exception("AutoAttenuatorEnable=Yes but failed to set attenuation")
                else:
                    msg = 'Attenuation is set (' + str(attn) + "dB)"
            except EquipmentError:
                msg = 'was not able to open port to Attenuator, you will need to press Stop\n' \
                      'if you want to restart run without using auto attenuator please change the field ' \
                      '"AutoAttenuatorEnable" in configs.test_config.json to "No"'
                printing_func(str_to_print=msg, logging_entity='PortsAndGuis', lock_print=lock_print,
                              do_log=True, logger_type='debug')
                raise Exception("AutoAttenuatorEnable=Yes but could not open port to Attenuator")
            except Exception:
                msg = 'was not able to open json with attenuator config data, will continue this run without ' \
                      'attenuator configuration'

        printing_func(str_to_print=msg, logging_entity='PortsAndGuis', lock_print=lock_print,
                      do_log=True, logger_type='debug')

    def config_equipment(self, temperature_sensor=True, attenuator=True):
        """
        :type temperature_sensor: bool
        :param temperature_sensor: if True will config temperature sensor
        :type attenuator: bool
        :param attenuator: if True will config attenuator
        configs equipment that needed for the run
        """
        # temperature sensor and auto attenuator
        global temperature_sensor_enable
        temperature_sensor_enable = False
        wiliot_folder_path = user_data_dir('offline', 'wiliot')
        folder_path = join(wiliot_folder_path, 'configs')
        # folder_path = 'configs'
        cfg_file_name = 'test_configs.json'
        # if file or folder doesn't exist will create json file with temperatureSensorEnable = 'No' and raise exception
        if os.path.isdir(folder_path):
            file_path = os.path.join(folder_path, cfg_file_name)
            if os.path.exists(file_path):
                self.test_configs = open_json(folder_path=folder_path,
                                              file_path=os.path.join(folder_path, cfg_file_name))
            else:
                msg = "Config file doesn't exist\n Creating test_config.json"
                printing_func(msg, 'PortsAndGuis', lock_print, logger_type='debug')
                with open(file_path, 'w') as cfg:
                    json.dump({"temperatureSensorEnable": "No", "AutoAttenuatorEnable": "No"}, cfg)
                # raise Exception('test_config.json was created\n Temperature sensor is disabled\n'
                #                 'You will need to press Stop')
                msg = 'test_config.json was created\n Temperature sensor is disabled\nYou will need to press Stop'
                printing_func(msg, 'PortsAndGuis', lock_print, logger_type='info')

                self.test_configs = open_json(folder_path=folder_path,
                                              file_path=file_path)
        else:
            msg = "'configs' directory doesn't exist\n Creating directory and test_config.json"
            printing_func(msg, 'PortsAndGuis', lock_print, logger_type='debug')
            os.mkdir(folder_path)
            file_path = os.path.join(folder_path, cfg_file_name)
            with open(file_path, 'w') as cfg:
                json.dump({"temperatureSensorEnable": "No", "AutoAttenuatorEnable": "No"}, cfg)
            # raise Exception('test_config.json was created\n Temperature sensor and Auto Attenuator is disabled\n'
            #                 'You will need to press Stop')
            msg = 'test_config.json was created\n Temperature sensor and Auto Attenuator is disabled\n' \
                  'You will need to press Stop'
            printing_func(msg, 'PortsAndGuis', lock_print, logger_type='info')

            self.test_configs = open_json(folder_path=folder_path,
                                          file_path=file_path)

        if temperature_sensor:
            if 'temperatureSensorEnable' not in self.test_configs.keys() or \
                    'AutoAttenuatorEnable' not in self.test_configs.keys():
                with open(file_path, 'w') as cfg:
                    json.dump({"temperatureSensorEnable": "No", "AutoAttenuatorEnable": "No"}, cfg)
                raise Exception('test_config.json missing some values, will return it to default values\n'
                                'You will need to press Stop')
            if self.test_configs['temperatureSensorEnable'].upper() == 'NO':
                temperature_sensor_enable = False
            elif self.test_configs['temperatureSensorEnable'].upper() == 'YES':
                temperature_sensor_enable = True
            else:  # illegal inputs will be ignored
                raise Exception("Valid values for temperatureSensorEnable are 'Yes' or 'No'\n "
                                "You will need to press Stop")
            if temperature_sensor_enable:
                self.Tag_t = set_temperature()
            else:
                self.Tag_t = None
        if attenuator:
            if self.test_configs['AutoAttenuatorEnable'].upper() == 'NO':
                self.auto_attenuator_enable = False
            elif self.test_configs['AutoAttenuatorEnable'].upper() == 'YES':
                self.auto_attenuator_enable = True
            else:  # illegal inputs will be ignored
                raise Exception("Valid values for AutoAttenuatorEnable are 'Yes' or 'No'\n You will need to press Stop")
            self.config_attenuator()


class ConsolePanelHandler_GUI(logging.Handler):

    def __init__(self, sig):
        # super().__init__()
        logging.Handler.__init__(self)
        # logging.StreamHandler.__init__(self, stream)
        self.stream = sig

    def handle(self, record):
        rv = self.filter(record)
        if rv:
            self.acquire()
            try:
                self.emit(record)
            finally:
                self.release()
        return rv

    def emit(self, record):
        try:
            self.stream.emit(self.format(record))
        except RecursionError:
            raise
        except Exception:
            self.handleError(record)


class MainWindow(QMainWindow):
    """
    Thread that opens and controls the GUI, opens all threads, sets/clears timers for all threads and handles exceptions
    This class will call for upload to cloud

    Parameters:
        values set by user in Offline Tester GUI:
            @Allow multiple missing label in row: dropdown list "Yes"/"No"
                If set to "No" the run will pause when a missing label is detected
            @Max missing labels in a row: int
                In case this number of missing label in row is reached, the run will pause
            @To print?: dropdown list "Yes"/"No"
                Enable/Disable printer. If set to "Yes" printing GUI will be opened after user pressed "Submit"
            @What is the printing job format?: dropdown list "SGTIN"/"Test"
            @Reel_name: str
            @Tags Generation: dropdown list with tags generation (e.g. "D2")
            @Inlay type: dropdown list with inlay types (e.g. "Dual Band")
            @Inlay serial number (3 digits): serial number for given inlay type
            @Test time [sec] (reel2reel controller->delay between steps = 999): max time before R2R moves to next tag
            @Fail if no packet received until [sec]: Max time TagThread will wait for first packet from tag
            @PacketThreshold: minimum amount of valid received packets from tag to pass
            @Desired amount of tags (will stop the run after this amount of tags): int.
                The run will pause after the amount written is reached. The user can choose to stop the run or continue.
            @Desired amount of pass (will stop the run after this amount of passes): int
                The run will pause after the amount written is reached in tags that passed.
                The user can choose to stop the run or continue.
            @Surface: dropdown list with various testing surfaces with given dielectric constant (Er)
            @Is converted?: dropdown list "Yes"/"No"  => if tag is converted or not
            @comments: text box for user comments

    Exceptions:
        @except Exception: exception occurred in one of the threads => calls look_for_exceptions()
            look_for_exceptions() will call handle_r2r_exception() which prints and handles the exception if possible

    Events:
        listen/ waits on:
            events.tag_thread_is_ready_to_main => event from TagThread. if set, TagThread is ready
            events.printer_event => wait for response from printer (printer_success or printer_error)
            events.printer_success => the last print was successful
            events.cont_to_main_thread => continue response received from TagThread
            events.r2r_ready => notify if R2R in ready for movement

        sets:
            events.start_to_r2r_thread => enable/disable R2R movement. Sends pulse on "Start/Stop machine" GPIO line
            events.stop_to_r2r_thread => stops the R2R from running in case of end of run or exception
            events.pause_to_tag_thread => pauses TagThread if exception happened of user pressed Pause
            events.done_to_tag_thread => closes TagThread at the end of the run
            events.cont_to_tag_thread => send continue to paused TagThread after user pressed continue
            events.done2r2r_ready => closes R2RThread
            events.done_to_r2r_thread => kills R2R thread main loop if set
            events.done_to_printer_thread => user pressed Stop (end the program) - to avoid deadlock
            events.cont_to_printer_thread => send continue to PrinterThread after Continue pressed by user


    Logging:
        logging to logging.debug() and logging.info()
    """
    sig = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        """
        Initialize the runs threads and classes
        """
        try:
            super(MainWindow, self).__init__(*args, **kwargs)
            self.events = MainEvents()
            self.passed_every_50 = []
            self.last_tested_num = 0
            self.last_passed_num = 0
            self.yield_over_time = []
            self.calculate_interval = 10
            self.to_print = False
            global calculate_interval
            calculate_interval = self.calculate_interval
            self.calculate_on = 50
            global calculate_on
            calculate_on = self.calculate_on
            self.first_reached_to_desired_passes = False
            self.first_reached_to_desired_tags = False
            self.yield_drop_happened = False
            self.yield_was_high_lately = True
            self.prev_y_len = 0
            self.waiting_for_user_to_press_stop_because_printer = False
            logging.getLogger().setLevel(logging.DEBUG)
            stream_handler = logging.StreamHandler()
            logging.getLogger().addHandler(stream_handler)
            self.ports_and_guis = PortsAndGuis()
            self.to_scan = self.ports_and_guis.Tag_Value['QRRead']

            file_path, user_name, password, owner_id, is_successful = check_user_config_is_ok()
            self.management_client = ManagementClient(oauth_username=user_name, oauth_password=password,
                                                      owner_id=owner_id, env=self.ports_and_guis.env,
                                                      logger_=logging.getLogger().name,
                                                      log_file=self.ports_and_guis.Tag_pathForLog)
            self.refresh_token_thread = refreshTokenPeriodically(security_client=self.management_client.auth_obj,
                                                                 dt=14400)

            self.r2r_thread = R2RThread(self.events, self.ports_and_guis)
            self.tag_checker_thread = TagThread(self.events, self.ports_and_guis, self.management_client)

            if self.to_scan == 'Yes':
                self.tag_comparing_qr = QRThread(self.events, self.ports_and_guis)

            self.events.tag_thread_is_ready_to_main.wait()
            self.events.tag_thread_is_ready_to_main.clear()

            self.pass_job_name = self.tag_checker_thread.printing_value['passJobName']  # will be set inside config
            self.to_print = self.tag_checker_thread.to_print
            self.start_value = int(self.tag_checker_thread.printing_value['firstPrintingValue'])

            # printer set-up ####################################################################
            # happens here so we will wait less until the printer will start up (will happen in the background)
            if self.to_print:
                self.printer = Printer(self.start_value, self.pass_job_name, self.events, self.ports_and_guis)
                self.look_for_exceptions()

            self.open_ui()  # starts recurring_timer() that starts look_for_exceptions()

            # if serialization:
            self.refresh_token_thread.start()

            self.r2r_thread.start()
            self.tag_checker_thread.start()
            self.events.tag_thread_is_ready_to_main.wait()
            self.events.tag_thread_is_ready_to_main.clear()

            if self.to_scan == 'Yes':
                self.tag_comparing_qr.start()

            if self.to_print:
                self.printer.start()
                self.events.printer_event.wait()
                if self.events.printer_success.isSet():
                    self.events.printer_success.clear()
                    msg = 'Printer is ready to start'
                    printing_func(msg, 'MainWindow', lock_print, logger_type='debug')

            self.events.start_to_r2r_thread.set()
        except Exception:
            exception_details = sys.exc_info()
            msg = 'Exception detected during initialization:'
            printing_func(msg, 'MainWindow', lock_print, logger_type='debug')
            print_exception(exception_details, printing_lock=lock_print)
            self.look_for_exceptions()

        # done will be raised from stop_fn (user pressed done)

    def open_ui(self):
        """
        opens the run main GUI that will present the run data and gives to the user ability to Stop/Continue/Pause
        """
        self.stop_label = QLabel("If you want to stop this run, press stop")
        self.stop_label.setFont(QFont('SansSerif', 10))
        self.cont_label = QLabel("If you want to skip and fail at this location, press Continue")
        self.cont_label.setFont(QFont('SansSerif', 10))
        self.reel_label = QLabel("Reel Name: ")
        self.reel_label.setFont(QFont('SansSerif', 10))
        self.reel_label.setStyleSheet('.QLabel {padding-top: 10px; font-weight: bold; font-size: 25px; color:#ff5e5e;}')
        self.reel_label.setFont(QFont('SansSerif', 10))
        self.tested = QLabel("Tested = 0, Passed = 0, Yield = -1%")
        self.tested.setFont(QFont('SansSerif', 10))
        self.last_tag_str = QLabel("Last Tag Passed: ")
        self.last_tag_str.setFont(QFont('SansSerif', 10, weight=QFont.Bold))
        self.last_pass = QLabel("No tag has passed yet :(")
        self.last_pass.setFont(QFont('SansSerif', 10))
        layout = QVBoxLayout()

        self.continue_ = QPushButton("Continue")
        self.continue_.setStyleSheet("background-color: green")
        self.continue_.setFont(QFont('SansSerif', 10))
        self.continue_.setFixedSize(QSize(300, 22))
        self.continue_.pressed.connect(self.continue_fn)

        self.pause = QPushButton("Pause")
        self.pause.setStyleSheet("background-color: orange")
        self.pause.setFont(QFont('SansSerif', 10))
        self.pause.setFixedSize(QSize(300, 22))
        self.pause.pressed.connect(self.pause_fn)

        self.stop = QPushButton("Stop")
        self.stop.setStyleSheet("background-color: #FD4B4B")
        self.stop.setFont(QFont('SansSerif', 10))
        self.stop.setFixedSize(QSize(300, 22))
        self.stop.pressed.connect(self.close)

        self.c = ConsolePanelHandler_GUI(self.sig)
        self.c.setLevel(logging.WARNING)
        self.text_box = QPlainTextEdit()
        self.text_box.setPlaceholderText("Warnings will be printed here")
        self.text_box.setMaximumBlockCount(1000)
        # self.text_box.centerOnScroll()
        self.text_box.setReadOnly(True)
        # addConsoleHandler(self.appendDebug , logging.DEBUG)
        # console_log = logging.getLogger()
        # console_log.setLevel(logging.WARNING)
        logging.getLogger().addHandler(self.c)
        # logging.getLogger().setLevel(logging.INFO) #Change to the wanted level of log
        self.sig.connect(self.appendDebug)
        self.text_box.moveCursor(QTextCursor.End)

        self.graphWidget = pg.PlotWidget()
        self.x = []  # 0 time points
        self.y = []  # will contain the yield over time
        self.graphWidget.setBackground('w')
        # Add Title
        self.graphWidget.setTitle("Yield over time", color="56C2FF", size="20pt")
        styles = {"color": "#f00", "font-size": "14px"}
        self.graphWidget.setLabel("left", "Yield for the last 50 tags [%]", **styles)
        self.graphWidget.setLabel("bottom", "Last tag location [x*" + str(self.calculate_interval) + "+" +
                                  str(self.calculate_on) + "]", **styles)
        pen = pg.mkPen(color=(255, 0, 0))
        self.data_line = self.graphWidget.plot(self.x, self.y, pen=pen)

        layout.addWidget(self.reel_label)
        layout.addWidget(self.cont_label)
        layout.addWidget(self.continue_)
        layout.addWidget(self.pause)
        layout.addWidget(self.stop_label)
        layout.addWidget(self.stop)
        layout.addWidget(self.last_tag_str)
        layout.addWidget(self.last_pass)
        layout.addWidget(self.tested)
        # layout.addWidget(self.debug)
        layout.addWidget(self.text_box)
        layout.addWidget(self.graphWidget)

        w = QWidget()
        w.setLayout(layout)
        self.setCentralWidget(w)
        # self.w = Error_window()
        self.show()

        # updates the GUI and stops all if exception happened
        self.update_timer = QTimer()
        self.update_timer.setInterval(500)
        self.update_timer.timeout.connect(self.recurring_timer)
        self.update_timer.start()

    def closeEvent(self, event):
        close = QMessageBox()
        close.setText("Are you sure want to stop and exit?")
        close.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        close = close.exec()

        if close == QMessageBox.Yes:
            event.accept()
            self.stop_fn()
        else:
            logging.info('Run paused')
            event.ignore()
            self.pause_fn()

    @pyqtSlot(str)
    def appendDebug(self, string):
        self.text_box.appendPlainText(string)  # +'\n')

    # GUI functions ##########################################################
    def stop_fn(self):
        """
        will be triggered by the Stop button and will end the run.
        will upload run's data to cloud and close the threads.
        """
        global tested, passed, missing_labels
        global last_pass_string, under_threshold, problem_in_locations_hist
        if tested == 0:
            yield_ = -1.0
        else:
            if tested > 1:
                if tested > passed:
                    tested = tested - 1
                yield_ = passed / tested * 100
            else:
                if passed == 0:
                    yield_ = 0
                else:
                    yield_ = 100
        self.events.pause_to_tag_thread.set()
        self.update_timer.stop()
        # self.close()
        ttfgp_avg = None
        if len(self.tag_checker_thread.ttfgp_list) > 0:
            ttfgp_avg = mean(self.tag_checker_thread.ttfgp_list)
        self.events.done_to_tag_thread.set()
        self.events.done_to_printer_thread.set()
        self.events.done2r2r_ready.set()
        self.events.cont_to_tag_thread.set()  # to avoid deadlock
        self.events.done_to_r2r_thread.set()

        values = save_screen(tested=tested, passed=passed, yield_=yield_, missing_labels=missing_labels,
                             problem_in_locations_hist_val=problem_in_locations_hist, ttfgp_avg=ttfgp_avg)
        try:
            msg = "Stopped by the operator.\n" + 'Reels yield_over_time is: |' + str(self.yield_over_time) + \
                  '| interval: |' + str(self.calculate_interval) + '|, on: |' + str(self.calculate_on) + \
                  '\nLast words: ' + values['comments'] + '\nTested = ' + str(tested) + ', Passed = ' + str(passed) + \
                  ', Yield = ' + str(yield_) + '%' + ', Missing labels = ' + str(missing_labels)
            printing_func(msg, 'MainWindow', lock_print, logger_type='info')
        except Exception:
            print('User finished the run from GUI')
        if self.to_scan == 'Yes':
            if len(self.tag_comparing_qr.failed_qr_list) > 0:
                logging.warning('Please check next tags printing: {}'.format(self.tag_comparing_qr.failed_qr_list))

        self.r2r_thread.join()
        # save last printed value, also being done after every pass by the printer thread (for crash support):

        env_dirs = WiliotDir()
        WILIOT_DIR = env_dirs.get_wiliot_root_app_dir()
        machine_dir = join(WILIOT_DIR, 'offline')
        local_config_dir = join(machine_dir, 'configs')

        if self.to_print:
            if self.tag_checker_thread.value['printingFormat'] == 'SGTIN':
                filename = 'gui_printer_inputs_4_SGTIN_do_not_delete.json'
                printing_format = 'SGTIN'
            else:
                filename = 'gui_printer_inputs_4_Test_do_not_delete.json'
                printing_format = 'Test'

            self.folder_path = 'configs'
            data = open_json(folder_path=self.folder_path, file_path=os.path.join(self.folder_path, filename),
                             default_values=DefaultGUIValues(printing_format).default_gui_values)
            last_printing_value = last_pass_string.split()
            if passed >0:
                data['firstPrintingValue'] = str(int(last_printing_value[9][-4:]) + 1)
            f = open(os.path.join(self.folder_path, filename), "w")
            json.dump(data, f)
            f.close()

        global run_data_log, log_path, run_data_dict, run_data_path
        is_exist = True
        if run_data_log is None:
            run_data_log = CsvLog(header_type=HeaderType.RUN, path=run_data_path, tester_type=TesterName.OFFLINE)
            run_data_log.open_csv()
            is_exist = False
        run_data_dict['passed'] = passed
        run_data_dict['tested'] = tested
        run_data_dict['timeProfile'] = self.ports_and_guis.tests_suite['tests'][0]['timeProfile']
        run_data_dict['txPower'] = self.tag_checker_thread.GwObj.valid_output_power_vals[
            self.ports_and_guis.tests_suite['tests'][0]['absGwTxPowerIndex']]['abs_power']
        run_data_dict['energizingPattern'] = self.ports_and_guis.tests_suite['tests'][0]['energizingPattern']

        if tested > 0:  # avoid division by zero
            run_data_dict['yield'] = passed / tested
        if tested == 0:
            run_data_dict['yield'] = -1.0
        run_data_dict['yieldOverTime'] = self.yield_over_time
        run_data_dict['includingUnderThresholdPassed'] = under_threshold + passed
        if tested > 0:  # avoid division by zero
            run_data_dict['includingUnderThresholdYield'] = run_data_dict['includingUnderThresholdPassed'] / tested
        run_data_dict['errors'] = "NA"  # collect_errors(log_path)
        run_data_log.override_run_data(run_data_dict, run_data_path)

        global reel_name, tags_data_path
        res = None
        if values['upload'] == 'Yes':
            parts1 = [i for i in run_data_path.split('/')]
            parts2 = [i for i in tags_data_path.split('/')]
            if tested > 0:
                try:
                    res = upload_to_cloud_api(batch_name=reel_name, tester_type='offline', run_data_csv_name=parts1[-1],
                                              tags_data_csv_name=parts2[-1], to_logging=True, logger_=logging.getLogger().name,
                                              env=self.ports_and_guis.env)
                    #todo add log_file=self.ports_and_guis.Tag_pathForLog and check if it doesnt over rides the original log file
                    sleep(3)
                    res = True
                except Exception:
                    exception_details = sys.exc_info()
                    print_exception(exception_details=exception_details, printing_lock=lock_print)
                    res = False
            else:
                logging.warning('tested value is incorrent, please check run_data file')
                res = False

            if not res:
                msg = 'Upload to cloud failed!!!!!!!!!\ngot an error while uploading to cloud'
                printing_func(msg, 'MainWindow', lock_print, logger_type='warning')
            else:
                logging.info('Uploaded to cloud ' + str(res))
        else:
            logging.info('Uploaded to cloud? No')

        self.tag_checker_thread.join()
        if self.to_print and not self.waiting_for_user_to_press_stop_because_printer:
            self.printer.join()

        self.refresh_token_thread.stop()
        global failed_tags
        if res is not None:
            upload_conclusion(failed_tags=failed_tags, succeeded_csv_uploads=res)
        window.close()
        sys.exit(0)

    def continue_fn(self):
        """
        will be triggered by the Continue button and will resume the run after Pause/ run got stuck if possible.
        """
        if not self.events.cont_to_tag_thread.isSet() and not self.waiting_for_user_to_press_stop_because_printer \
                and not self.tag_checker_thread.fetal_error:
            msg = "User pressed continue, the R2R will advance now (the last spot will be fail)"
            printing_func(msg, 'MainWindow', lock_print, logger_type='warning')
            self.look_for_exceptions()
            self.events.cont_to_tag_thread.set()
            self.events.cont_to_printer_thread.set()
            self.events.cont_to_main_thread.wait()
            self.events.cont_to_main_thread.clear()
            self.events.start_to_r2r_thread.set()
            if self.to_scan == 'Yes':
                self.tag_comparing_qr.start()

    def pause_fn(self):
        """
        will be triggered by the Pause button and will pause the run if possible.
        """
        if not self.events.pause_to_tag_thread.isSet() and not self.waiting_for_user_to_press_stop_because_printer \
                and not self.tag_checker_thread.fetal_error:
            msg = "Run paused, the R2R will pause now (the current spot will be fail)"
            printing_func(msg, 'MainWindow', lock_print, logger_type='warning')
            self.events.stop_to_r2r_thread.set()
            self.events.pause_to_tag_thread.set()

    def recurring_timer(self):
        """
        update the runs main GUI, checks that the other threads are OK (no exceptions)
        """
        global tested, passed, missing_labels, black_list_size
        global last_pass_string, reel_name

        if tested == 0:
            yield_ = -1.0
            self.reel_label.setText("Reel Name: " + reel_name)
        else:
            yield_ = passed / tested * 100
        self.tested.setText('Tested = ' + str(tested) + ', Passed = ' + str(passed) + ', Yield = ' +
                            '{0:.4g}'.format(yield_) + '%' + '\nMissing labels = ' + str(missing_labels) +
                            ', black list size = ' + str(black_list_size))
        self.last_pass.setText(last_pass_string)
        # update the graph, if there was change in the tested amount
        # because passed and tested are been updated in different times
        # we will check the passed of the prev tag => tested -1
        if tested > self.last_tested_num:
            if self.calculate_on >= tested > self.last_tested_num:
                if passed - self.last_passed_num > 0:
                    self.passed_every_50.append(1)
                else:
                    self.passed_every_50.append(0)
            elif tested > 0:
                del self.passed_every_50[0]
                if passed - self.last_passed_num > 0:
                    self.passed_every_50.append(1)
                else:
                    self.passed_every_50.append(0)

            if len(self.passed_every_50) > self.calculate_on:
                msg = 'self.passed_every_50 length is too long (self.passed_every_50 = ' + \
                      str(self.passed_every_50) + ')'
                printing_func(msg, 'MainWindow', lock_print, logger_type='warning')

            if tested % self.calculate_interval == 1 and tested > self.calculate_on:
                self.y.append(sum(self.passed_every_50) / self.calculate_on * 100)
                self.x = range(len(self.y))
                self.data_line.setData(self.x, self.y)  # Update the data.
                self.yield_over_time.append(int(sum(self.passed_every_50) / self.calculate_on * 100))
            if 0 < len(self.y) != self.prev_y_len and self.yield_was_high_lately:
                self.prev_y_len = len(self.y)
                if self.y[-1] == 0:  # 50 fails in a row => Pause the run
                    msg = 'There are 50 fails in a row, please make sure everything is OK and press Continue'
                    printing_func(msg, 'MainWindow', lock_print, logger_type='debug')
                    self.yield_drop_happened = True
                    self.yield_was_high_lately = False
                    if not self.events.pause_to_tag_thread.isSet():
                        self.events.stop_to_r2r_thread.set()
                        self.events.pause_to_tag_thread.set()
                elif self.y[-1] < 40 and len(self.y) > 15:  # under 40% yield-over-time for 200 tags => Pause the run
                    self.yield_drop_happened = True
                    for ii in range(1, 15):
                        if self.y[-ii] < 40:
                            continue
                        else:
                            self.yield_drop_happened = False
                            break
                    if self.yield_drop_happened:
                        msg = str('*' * 100) + '\nThe yield-over-time of the last 200 tags is below 40%,' \
                                               ' waiting to operator to press Continue\n' + str('*' * 100)
                        printing_func(msg, 'MainWindow', lock_print, logger_type='warning')
                        self.yield_was_high_lately = False
                        if not self.events.pause_to_tag_thread.isSet():
                            self.events.stop_to_r2r_thread.set()
                            self.events.pause_to_tag_thread.set()
                elif self.y[-1] > 50 and len(self.y) > 15:
                    self.yield_was_high_lately = True
            global yield_over_time
            yield_over_time = self.yield_over_time
            # update the prev counters
            self.last_tested_num += 1
            if passed > self.last_passed_num:
                self.last_passed_num += 1

        if tested == desired_tags_num and not self.first_reached_to_desired_tags:
            msg = '---------------------------Desired tags have reached (' + str(tested) + \
                  ') , If you wish to proceed, press Continue---------------------------'
            printing_func(msg, 'MainWindow', lock_print, logger_type='debug')
            self.first_reached_to_desired_tags = True
            self.pause_fn()
        if passed == desired_pass_num and not self.first_reached_to_desired_passes:
            msg = '---------------------------Desired passes have reached (' + str(passed) + \
                  ') , If you wish to proceed, press Continue---------------------------'
            printing_func(msg, 'MainWindow', lock_print, logger_type='debug')
            self.first_reached_to_desired_passes = True
            self.pause_fn()
        if not self.waiting_for_user_to_press_stop_because_printer:
            self.look_for_exceptions()

    def look_for_exceptions(self):
        """
        search for exceptions in the threads Exceptions Queues.
        """
        if self.to_print:
            if not self.printer.exception_queue.empty() or not self.tag_checker_thread.exception_queue.empty() or \
                    not self.r2r_thread.exception_queue.empty():
                if not self.events.pause_to_tag_thread.isSet():
                    msg = "Paused because an exception happened, the R2R will pause now " \
                          "(the current spot will be fail)"
                    printing_func(msg, 'MainWindow', lock_print, logger_type='debug')
                    self.events.stop_to_r2r_thread.set()
                    self.events.pause_to_tag_thread.set()
                self.handle_r2r_exception()
        elif not self.tag_checker_thread.exception_queue.empty() or not self.r2r_thread.exception_queue.empty():
            if not self.events.pause_to_tag_thread.isSet():
                msg = "Paused because an exception happened, the R2R will pause now (the current spot will be fail)"
                printing_func(msg, 'MainWindow', lock_print, logger_type='debug')
                self.events.stop_to_r2r_thread.set()
                self.events.pause_to_tag_thread.set()
            self.handle_r2r_exception()

    def handle_r2r_exception(self):
        """
        handle the exception if possible. prints the exception to screen and log
        """
        if self.to_print:
            if not self.printer.exception_queue.empty():
                exception_details = self.printer.exception_queue.get()
                msg = 'Printer got an Exception:'
                printing_func(msg, 'MainWindow', lock_print, logger_type='warning', do_log=True)
                # using logging.warning that will be parsed to errors
                print_exception(exception_details, printing_lock=lock_print)
                exc_type, exc_obj, exc_trace = exception_details
                # ConnectionResetError => exc_obj = 'An existing connection was forcibly closed by the remote host'
                if isinstance(exc_obj, PrinterNeedsResetException):
                    msg = 'Please press Stop and start a new run - Printer need restart'
                    printing_func(msg, 'MainWindow', lock_print, logger_type='warning', do_log=True)
                    self.waiting_for_user_to_press_stop_because_printer = True
                    self.events.printer_error.set()  # to avoid deadlock when printer thread crashed before
                elif isinstance(exc_obj, ConnectionResetError):
                    self.events.done_to_printer_thread.set()
                    msg = 'Will close socket to Printer and restart it, please wait...'
                    printing_func(msg, 'MainWindow', lock_print, logger_type='debug')
                    self.events.printer_event.wait()
                else:
                    if self.events.r2r_ready.isSet():
                        self.events.r2r_ready.clear()
                    msg = 'Please check everything is OK and press Continue'
                    printing_func(msg, 'MainWindow', lock_print, logger_type='debug')

        if not self.tag_checker_thread.exception_queue.empty():
            exception_details = self.tag_checker_thread.exception_queue.get()
            msg = 'tag_checker_thread got an Exception, waiting for an operator to press Continue or Stop'
            exc_type, exc_obj, exc_trace = exception_details
            if 'R2R moved before timer ended' in str(exc_obj):
                msg = 'R2R moved before timer ended, please check in r2r controller\n' \
                      'Menu -> Motors setup -> DELAY BETWEEN STEPS\n' \
                      'is set to 999'
                printing_func(msg, 'MainWindow', lock_print, logger_type='debug')
                print_exception(exception_details, printing_lock=lock_print)
                pop_up_window(msg)
            else:
                printing_func(msg, 'MainWindow', lock_print, logger_type='debug')
                print_exception(exception_details, printing_lock=lock_print)

        if not self.r2r_thread.exception_queue.empty():
            exception_details = self.r2r_thread.exception_queue.get()
            msg = 'r2r_thread got an Exception, waiting for an operator to press Continue or Stop'
            printing_func(msg, 'MainWindow', lock_print, logger_type='debug')
            print_exception(exception_details, printing_lock=lock_print)


def set_attn_power_offline(attn_obj, attn_power, simulation=False):
    """
    configure Attenuator to a specific value
    gets:
        attn_obj:       Attenuator obj
        attn_power:     value to set attn

    return:
        status if Attenuator is set correctly

    """
    if simulation:
        status = True
    else:
        status = True
        print('Setting Attenuator to {attn_power}dB'.format(attn_power=attn_power))
        attn_obj.Setattn(attn_power)
        sleep(0.5)

        # attn_current_config = attn_obj.Getattn()
        # if (float(attn_current_config) - attn_power) != 0:
        #     print('Error setting ATTENUATOR')
        #     status = False
        # print(
        #     "Attenuator is set to: {attn_current_config} dB".format(
        #         attn_current_config=attn_current_config.split('.')[0]))
    return status


# --------  main code:  ---------- #
app = QApplication([])
window = MainWindow()
app.exec_()
