#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from paho.mqtt import client as mqtt_client
import random
import time
from pdb import set_trace as stop
import json

class Err:
    SRV_NO_EXIST = 900 # 无此服务
    SRV_NO_RESP = 901 # 无回应
    SRV_REQ_INVALID = 902 # 无效 Req
    SRV_RESP_INVALID = 903 # 无效 Res

    DEV_NO_CONN = 1000 # 无法连接设备
    DEV_NO_RESP = 1001 # 无法得到回应
    DEV_REQ_INVALID = 1002 # 无效的 Request
    DEV_RESP_INVALID = 1003 # 无效的 Response

    BLE_RESP_INVALID = 11003 # 无效蓝牙回应
    BLE_NO_CHAR = 11100 # 无效蓝牙特征

class Alarmer():
    def __init__(self, broker: str = 'broker.emqx.io', port: int = 1883) -> None:
        self.broker = broker
        self.port = port
        self.client = None

    def connect(self, srv_id, dev_id, label, srv_type):
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("[Alarmer] Connected to MQTT Broker: %s:%s!" % (self.broker, self.port))
            else:
                print("[Alarmer] Failed to connect, return code %d\n" % rc)

        self.client = mqtt_client.Client(f'python-alarmer-{random.randint(0, 99999999999)}')
        self.client.on_connect = on_connect
        self.client.connect(self.broker, self.port)
        self.client.loop_start()
        self.topic = 'alarm/{0}/{1}'.format(srv_id, dev_id)
        self.alarm_msg = {
            "srv_id": srv_id,
            "dev_id": dev_id,
            "label": label,
            "srv_type": srv_type,
            "code_err": -1,
            "code_severity": -1,
            "time": 0,
            "content": ""
        }

    def alarm(self, code_err: int, code_severity: int, content: str):
        self.alarm_msg['code_err'] = code_err
        self.alarm_msg['code_severity'] = code_severity
        self.alarm_msg['content'] = content
        self.alarm_msg['time'] = time.time_ns()
        msg = json.dumps(self.alarm_msg, ensure_ascii=False)
        print("[ALARM]: " + msg)
        self.client.publish(self.topic, msg, 1, False)