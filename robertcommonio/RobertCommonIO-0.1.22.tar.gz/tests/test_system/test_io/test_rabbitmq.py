import time
from robertcommonio.system.io.rabitmq import RabbitMQConfig, RabbitMQAccessor
from datetime import datetime

HOST = '47.103.96.35'
PORT = 5672
USER = 'admin'
PSW = '!Abc@123'
exchange = 'robert'
exchange_type = 'topic'
routing_key = 'robert_queue'
vir_host = '/'
short_connect = True



def call_back(data):
    print(data)

def test_pub():
    accessor = RabbitMQAccessor(RabbitMQConfig(HOST=HOST, PORT=PORT, USER=USER, PSW=PSW, VIR_HOST=vir_host, SHORT_CONNECT=short_connect))
    while True:
        accessor.publish_exchange(exchange, routing_key, datetime.now().strftime('%H:%M:%S'), exchange_type)
        time.sleep(2)

def test_sub():
    pass

test_pub()
