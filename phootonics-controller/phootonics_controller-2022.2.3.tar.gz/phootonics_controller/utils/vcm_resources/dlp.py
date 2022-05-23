# -*- coding: utf-8 -*-
"""
Created by gregory on 06.01.17

Copyright 2017 Alpes Lasers SA, Neuchatel, Switzerland
"""

import logging

from .base_controller import BaseController
import threading
import serial

logger = logging.getLogger(__name__)

__author__ = 'gregory'
__copyright__ = "Copyright 2016, Alpes Lasers SA"

ON = 'ON'
OFF = 'OFF'
READ = 'READ'
CHANNELS = {
    1: {ON: '1', OFF: 'Q', READ: 'A'},
    2: {ON: '2', OFF: 'W', READ: 'S'},
    3: {ON: '3', OFF: 'E', READ: 'D'},
    4: {ON: '4', OFF: 'R', READ: 'F'},
    5: {ON: '5', OFF: 'T', READ: 'G'},
    6: {ON: '6', OFF: 'Y', READ: 'H'},
    7: {ON: '7', OFF: 'U', READ: 'J'},
    8: {ON: '8', OFF: 'I', READ: 'K'},
}


class DLPController(BaseController):
    READY = 'READY'

    def __init__(self, port):
        super(DLPController, self).__init__()
        self._device = None
        self._port = port
        self._baudrate = 115200
        self._comm_lock = threading.Lock()

    def _connected_status(self):
        return DLPController.READY

    def read_channel(self, channel):
        with self._comm_lock:
            self._device.write(CHANNELS[channel][READ])
            ans = None
            while True:
                c = self._device.read()
                if not c:
                    raise Exception('DLP did not answer')
                if c not in '\r\n':
                    ans = bool(int(c))
                elif self._device.in_waiting == 0:
                    break
            return ans

    def set_channel(self, channel, value):
        with self._comm_lock:
            self._device.write(CHANNELS[channel][ON if value else OFF])

    def _connect(self):
        self._device = serial.Serial(self._port, baudrate=self._baudrate, timeout=2.0)

    def _disconnect(self):
        try:
            self._device.close()
        finally:
            self._device = None

    def _check_connection(self):
        with self._comm_lock:
            self._device.write("'")
            return self._device.read() == 'Q'
