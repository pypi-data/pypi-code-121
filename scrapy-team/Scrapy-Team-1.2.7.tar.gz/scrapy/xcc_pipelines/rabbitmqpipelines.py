# -*- coding: utf-8 -*-
from scrapy.utils.conf import get_config
import pika
import logging

     
from twisted.internet.threads import deferToThread
from scrapy.utils.serialize import ScrapyJSONEncoder
import time,os

EXCHANGE_NAME = ''

import logging
logger = logging.getLogger('pika').setLevel(logging.WARNING)
class RabbitMQPipeline(object):
    """Pushes serialized item into a RabbitMQ list/queue"""

    def __init__(self, item_key, connection_url):
        self.item_key = item_key
        self.exchange_name = EXCHANGE_NAME
        self.encoder = ScrapyJSONEncoder()
        self.connection_url= connection_url

    @classmethod
    def from_crawler(cls, crawler):
        section_select ="mq_cfg_prod" if os.environ.get('IF_PROD') == "True" or crawler.settings.get('IF_PROD')\
             == True or get_config().get("settings","IF_PROD",fallback="False")=="True" else "mq_cfg_dev"
        if hasattr(crawler.spider, 'items_key'):
            item_key = crawler.spider.items_key
        elif get_config().get(section=section_select,option="RABBITMQ_ITEMS_KEY",fallback=''):
            item_key = get_config().get(section=section_select,option="RABBITMQ_ITEMS_KEY",fallback='')
        elif hasattr(crawler.settings,"RABBITMQ_ITEMS_KEY"):
            item_key = crawler.settings.get("RABBITMQ_ITEMS_KEY")
        else:
            item_key = 'items_{spider_name}'.format(
                spider_name=crawler.spider.name)
        connection_url =  get_config().get(section=section_select,option="RABBITMQ_ITEMS_KEY",fallback='') or \
            crawler.settings.get('RABBITMQ_ITEMS_KEY')
        return cls(item_key,connection_url)

    def process_item(self, item, spider):
        return deferToThread(self._process_item, item, spider)

    def _process_item(self, item, spider):
        key = self.item_key
        data = self.encoder.encode(item)
        try_time = 1
        while try_time<10:
            try:
                self.server = self.connect_mq(self.connection_url)
                self.channel = self.get_channel(self.server, self.item_key)
                self.channel.basic_publish(exchange=self.exchange_name,
                                        routing_key=key,
                                        body=data)
                return item
            except Exception as e:
                logger.exception(e)
                logger.error('process item failed! try_time:{}'.format(try_time))
                try_time += 1
                time.sleep(1)
                self.channel = self.get_channel(self.server, self.item_key)
        return item

    def get_channel(self,connection, queue_name, durable=True, confirm_delivery=True, is_delay=False):
        """ Init method to return a prepared channel for consuming
        """
        channel = connection.channel()
        channel.queue_declare(queue=queue_name,durable=durable)#,arguments={'x-max-priority': 255,'vhost':'/'})
        if confirm_delivery:
            channel.confirm_delivery()

        if is_delay is True:
            exchange_name = "{}-delay".format(queue_name)
            channel.exchange_declare(exchange_name,
                                    exchange_type="x-delayed-message",
                                    arguments={"x-delayed-type": "direct"})
            channel.queue_bind(
                queue=queue_name, exchange=exchange_name, routing_key=queue_name)
        return channel
    
    def connect_mq(self,connection_url):
        """ Create and return a fresh connection
        """
        return pika.BlockingConnection(pika.URLParameters(connection_url))
