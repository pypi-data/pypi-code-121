#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/26 11:25
# @Author  : Adyan
# @File    : rabbit_conn.py


import json
import logging
import time
import traceback

import pika
from pika.exceptions import ConnectionClosedByBroker, AMQPChannelError, AMQPConnectionError
logging.getLogger("pika").setLevel(logging.WARNING)

class RabbitClient:
    def __init__(self, queue_name, config):
        """
        :param queue_name:
        :param config: {
            "ip": "ip",
            "port": 30002,
            "virtual_host": "my_vhost",
            "username": "dev",
            "pwd": "zl123456",
            "prefix": ""
            }
        """
        self.queue_name = queue_name
        self.config = config

    def rabbit_conn(self):
        """
        创建连接
        :return:
        """
        user_pwd = pika.PlainCredentials(
            self.config.get("username"),
            self.config.get("pwd")
        )
        params = pika.ConnectionParameters(
            host=self.config.get("ip"),
            port=self.config.get('port'),
            virtual_host=self.config.get("virtual_host"),
            credentials=user_pwd
        )
        self.conn = pika.BlockingConnection(parameters=params)
        self.col = self.conn.channel()
        self.col.queue_declare(
            queue=self.queue_name,
            durable=True
        )

    def push_rabbit(self, item):
        self.rabbit_conn()
        self.col.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            body=json.dumps(item, ensure_ascii=False)
        )

    def get_rabbit(self, fun):
        self.rabbit_conn()
        self.col.queue_declare(self.queue_name, durable=True, passive=True)
        self.col.basic_consume(self.queue_name, fun)
        self.col.start_consuming()


class MonitorRabbit:
    def __init__(
            self, rabbit_conn, redis_coon,
            redis_key=None, callback=None
    ):
        """
        :param rabbit_conn: rabbit链接
        :param redis_coon: redis链接
        :param redis_key: redis储存的键
        :param callback: 方法
        """
        self.rabbit_conn = rabbit_conn
        self.redis_coon = redis_coon
        self.redis_key = redis_key
        self._callback = callback

    def start_run(self):
        """
        监听队列
        :return:
        """
        while True:
            try:
                self.rabbit_conn.get_rabbit(self.callback)
            except ConnectionClosedByBroker:
                logging.info(f'error  [{ConnectionClosedByBroker}]')
                time.sleep(10)
                continue
            except AMQPChannelError:
                logging.info(f'error  [{AMQPChannelError}]')
                time.sleep(10)
                continue
            except AMQPConnectionError:
                # traceback.print_exc()
                logging.info(f'error  [{AMQPConnectionError}]')
                time.sleep(10)
                continue
            except:
                traceback.print_exc()
                logging.info(f'error  [{"unknow error"}]')
                time.sleep(10)
                continue

    def callback(self, channel, method, properties, body):
        """
        回调函数
        """
        try:
            req_body = body.decode('utf-8')
            logging.info(req_body)
            mes = {'result': json.loads(req_body)}
            if self._callback:
                self._callback.shop_start(json.dumps(mes))
            else:
                self.redis_coon.lpush(f'{self.redis_key}:start_urls', json.dumps(mes, ensure_ascii=False))
        except Exception as e:
            print(e)
        finally:
            channel.basic_ack(delivery_tag=method.delivery_tag)
