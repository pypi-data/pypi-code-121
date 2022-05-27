import json
import time
from robertcommonio.system.io.mqtt import MQTTConfig, MQTTAccessor
from datetime import datetime

HOST = 'mqtt.smartbeop.com'
PORT = 1884
client_id = ''
TOPIC = 'clp' #'SUBSTATION/MASTER/200120-1/S_SNT_DA' #'SUBSTATION/MASTER/200120-1/S_SNT_DAT'
USER = 'clp'
PSW = '9T3QV7hdjcHNIHpt'

all_values = {}

def call_back(topic: str, payload: bytes):
    try:
        values = json.loads(payload.decode())
        print(values)
        if isinstance(values, list):
            for value in values:
                if 'ID' in value.keys() and 'TS' in value.keys() and 'ST' in value.keys() and  'VR' in value.keys():
                    time = datetime.utcfromtimestamp(int(value.get('TS'))).replace(second=0).strftime("%Y-%m-%d %H:%M:%S")
                    if time not in all_values.keys():
                        all_values[time] = {}
                    all_values[time][f"{value.get('ID')}_{value.get('ST')}"] = eval(value.get('VR'))[0]

            print(f"{all_values}")
    except Exception as e:
        print(e.__str__())

def test_pub():
    accessor = MQTTAccessor(MQTTConfig(HOST=HOST, PORT=PORT, USER=USER, PSW=PSW, TOPIC=TOPIC, CLIENT_ID=client_id, KEEP_ALIVE=60))
    while True:
        accessor.publish_topic(TOPIC, datetime.now().strftime('%H:%M:%S'), 0)
        time.sleep(2)

def test_sub():
    accessor = MQTTAccessor(MQTTConfig(HOST=HOST, PORT=PORT, USER=USER, PSW=PSW, TOPIC=TOPIC, CLIENT_ID=client_id, KEEP_ALIVE=60))
    accessor.subscribe_topics(['clp', 'clp/s1'], 0, 10, call_back)

test_sub()
