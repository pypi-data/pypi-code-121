#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import time
import logging
import sys
import tornado.gen
from tornado.ioloop import IOLoop
from apscheduler.schedulers.tornado import TornadoScheduler

from lycium.amqplib import RabbitMQFactory

def test_amqplib():
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    virtual_host = 'xhhk'
    example_exchange = ''
    example_queue = 'amq.gen-ITXEQ0xY676S0Wft4Ocj7w'

    @tornado.gen.coroutine
    def test_callback(unused_channel, basic_deliver, properties, body):
        yield tornado.gen.sleep(0.00001)
        print('== on message consumer_tag:%s delivery_tag:%s' % (basic_deliver.consumer_tag, basic_deliver.delivery_tag))
        return None

    example = RabbitMQFactory()
    example.initialize({
        'host':'10.246.247.238',
        'port':30672, 
        'username':'xhhk', 
        'password':'ilq53eXBo6dteQhW',
        'virtual_host': virtual_host
    })
    example.consume(virtual_host, example_exchange, 'topic', example_queue, example_queue, False, test_callback)
    
    # start rabbit mq connection
    example.run()

    # start the ioloop
    IOLoop.instance().start()

if __name__ == '__main__':
    test_amqplib()
