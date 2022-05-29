#!/usr/bin/env python
# --*--coding=utf-8--*--

from pdb import set_trace as stop
from metathing.metathing import MetaThing as MT
from metathing.http import Entry
from metathing.device import Device
import threading
import time
import sys
import json

class Dev(Device):
    def __init__(self, srv, model) -> None:
        super().__init__(srv, model)
        self.mqtt = self.srv.mqtt
        self.resources = {}

class Bluetooth():
    def __init__(self):
        self.ecbs = {}
        self.srv = None
        self.devs = {}
        self.deviceModel = {}

    def AddDev(self, model):
        dev = Dev(self.srv, model)
        self.devs[model['id']] = dev
        print("Model added: {0}".format(model['id']))
        return dev
    
    def UpdateDev(self, model):
        self.AddDev(model)
    
    def DeleteDev(self, id):
        del self.devs[id]
        quit()
        # TODO: Release?
    
    def InitDev(self, model):
        return self.AddDev(model)

    # Run after binding srv
    def Initialize(self):
        return

    def Ping(self):
        return "OK"


if __name__ == "__main__":
    filepath = sys.path[0]

    config = {
        "ADDR": "0.0.0.0",
        "PORT": 16543,
        "WORKDIR": '.',
        "MQTT_ADDR": "localhost",
        "MQTT_PORT": 1883,
    }
    srv_name = "test"
    mt = MT(config, srv_name)
    app = Bluetooth()
    mt.Bind(app)
    mt.Run()