import json
from .serial_device_base import SerialDeviceBase
from time import time
import logging
from qtstrap import *


fake_guid = 0


def get_fake_guid():
    global fake_guid
    guid = fake_guid
    fake_guid += 1
    return str(guid)


class MessageTree(dict):
    def merge(self, d):
        for key in d:
            if key in self:
                self[key].update(d[key])
            else:
                self[key] = d[key]


class DeviceContextLogFilter(logging.Filter):
    def __init__(self, device):
        self.device = device

    def filter(self, record):
        record.port = self.device.port
        record.guid = self.device.guid
        record.baud = self.device.baud
        record.profile_name = self.device.profile_name
        return True


class SerialDevice(SerialDeviceBase):
    profile_name = ""
    
    def __init__(self, port=None, baud=9600, device=None):
        self.port = port
        self.baud = baud
        self.name = ""
        self.guid = get_fake_guid()
        
        # a SerialDevice can be created based on an existing SerialDevice
        if device:
            self.port = device.port
            self.baud = device.baud
            self.name = device.name
            self.guid = device.guid
        
        self.callbacks = {}

        super().__init__(port=self.port, baud=self.baud)

        # self.log = logging.getLogger(f'{__name__}.{self.profile_name}.{self.guid}')
        self.log = logging.getLogger(f'{__name__}.{self.profile_name}')
        self.log.addFilter(DeviceContextLogFilter(self))
        self.log.info(f'Creating device')

        self.signals = None
        self.time_created = time()

        # message stuff
        self.msg_count = 0
        self.message_tree = MessageTree()
        self.msg_history = []       

    @property
    def title(self):
        return f"{self.profile_name} ({self.port}) <{self.guid}>"

    @property
    def description(self):
        return {
            "profile_name":self.profile_name,
            "guid":self.guid,
            "port":self.port,
            "title":self.title,
        }

    def process_message(self, msg, table):
        # TODO: catch KeyErrors
        if self.message_tree is not None:
            for k in msg.keys():
                # does the table list an action?
                if k in table.keys() and callable(table[k]):
                    table[k](msg[k])

                # can we go deeper?
                elif isinstance(msg[k], dict):
                    if k in table.keys():
                        self.process_message(msg[k], table[k])

    def route_message(self, msg):
        pass

    def send(self, message, callback=None):
        if isinstance(message, dict):
            message['message_id'] = self.msg_count
            message = json.dumps(message)

            if callback:
                self.callbacks[self.msg_count] = callback

        super().send(message)
        self.msg_count += 1

    def receive(self, string):
        super().receive(string)

        try:
            msg = json.loads(string)

            if 'message_id' in msg:
                if msg['message_id'] in self.callbacks:
                    self.callbacks[msg['message_id']](msg)

            self.process_message(msg, self.message_tree)
            self.route_message(msg)

        except json.decoder.JSONDecodeError as e:
            self.log.warn("JSONDecodeError" + str(e))