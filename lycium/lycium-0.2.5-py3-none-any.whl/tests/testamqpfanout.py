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
    virtual_host = '/'
    example_exchange = 'ex.fanout.example'
    example_queue = 'example.text'

    @tornado.gen.coroutine
    def test_callback(unused_channel, basic_deliver, properties, body):
        time.sleep(0.5)
        print('== on message consumer_tag:%s delivery_tag:%s' % (basic_deliver.consumer_tag, basic_deliver.delivery_tag), body)
        return 'Response: ' + str(body)

    def test_publishing(example, idx_obj):
        example.publish(virtual_host, example_exchange, example_queue, 'test-'+str(idx_obj['index']))
        idx_obj['index'] += 1
        example.publish(virtual_host, example_exchange, example_queue, 'test-'+str(idx_obj['index']))
        idx_obj['index'] += 1

    example = RabbitMQFactory()
    example.initialize({
        'host':'localhost',
        'port':5672, 
        'username':'guest', 
        'password':'guest',
        'virtual_host': virtual_host
    })
    example.consume(virtual_host, example_exchange, 'fanout', example_queue, example_queue, False, test_callback)
    example.publish(virtual_host, example_exchange, example_queue, 'test-rpc')
    
    # scheduler example
    scheduler = TornadoScheduler()
    idx_obj = { 'index': 0 }
    scheduler.add_job(test_publishing, 'interval', seconds=5, args=(example, idx_obj))
    scheduler.start()

    # start rabbit mq connection
    example.run()

    # start the ioloop
    IOLoop.instance().start()

if __name__ == '__main__':
    test_amqplib()
