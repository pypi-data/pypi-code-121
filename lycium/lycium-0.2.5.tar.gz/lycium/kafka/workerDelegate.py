#!/usr/bin/env python
# encoding: utf-8
from lycium.kafka.publishesMessage import PublishesMessage
# from publishesResponse import PublishesResponse
from lycium.kafka.protocol.kafkapacket_pb2 import KafkaPacket
# from lycium.kafka.logger import logger
import json
import asyncio
import logging

logger = logging.getLogger('kafka')


class WorkerDelegate(object):
    """ 
    用于执行 回调函数以及对应的参数
    """

    def __init__(self, callback: callable, message:KafkaPacket , private_topic: str):
        self.callback = callback
        self.message = message
        self.private_topic = private_topic

    async def executor(self):
        """ 
        用于执行回调函数，返回PublishesMessage
        """
        headers = self.message.headers
        response_headers = dict()
        for item in headers:
            response_headers[item.name] = item.value
        publish_message = PublishesMessage(payload="",
                                           reply_to=self.private_topic,
                                           send_to=self.message.replyTo,
                                           correlation_id=self.message.correlationId,
                                           is_reply=True,
                                           content_type=self.message.contentType,
                                           content_encoding=self.message.contentEncoding,
                                           group_id=self.message.groupId,
                                           message_id=self.message.messageId,
                                           msg_type=self.message.type,
                                           user_id=self.message.userId,
                                           app_id=self.message.appId,
                                           headers=response_headers,
                                           callback=None
                                           )
        if callable(self.callback):
            result = ""
            try:

                if asyncio.iscoroutinefunction(self.callback):
                    result = await self.callback(self.message)
                else:
                    result = self.callback(self.message)
                if isinstance(result, (list, dict)):
                    try:
                        result = json.dumps(result)
                    except Exception as ee:
                        logger.exception(ee)
                        logger.error('json serialize %s failed with error:%s', str(result), str(ee))
                        result = ""
                        publish_message.status_code = 500
                        publish_message.error_message = str(ee)
                elif isinstance(result, (bytes, str)):
                    pass
                else:
                    result = ''
            except Exception as e:
                logger.exception(e)
                publish_message.status_code = 500
                publish_message.error_message = str(e)
            publish_message.payload = result
        return publish_message
