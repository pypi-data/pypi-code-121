#!/usr/bin/env python
# encoding: utf-8
import uuid
import time
from typing import Optional, Dict, List, Any
from lycium.kafka.protocol.kafkapacket_pb2 import KafkaPacket
import json


class PublishesMessage(object):

    def __init__(self,
                 payload: bytes,
                 reply_to: str,
                 send_to: str,
                 correlation_id: str,
                 content_type: str = None,
                 content_encoding: str = 'utf-8',
                 group_id: str = '0',
                 message_id: str = None,
                 msg_type: str = None,
                 user_id: str = None,
                 app_id: str = None,
                 headers: dict = None,
                 is_reply: bool = False,
                 callback: Optional[callable] = None,
                 routing_key: str =None):
        self.payload = payload
        self.callback = callback
        self.reply_to = reply_to
        self.send_to = send_to
        self.correlation_id = correlation_id
        self.content_type = content_type
        self.content_encoding = content_encoding
        self.group_id = group_id
        self.message_id = message_id
        self.msg_type = msg_type
        self.user_id = user_id
        self.app_id = app_id
        self.headers = headers if headers else dict()
        self.is_reply = is_reply
        self.create_time = time.time() * 1000
        self.standard_create_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.create_time/1000))
        self.status_code = 200
        self.error_message = ""
        self.routing_key = routing_key

    def new_correlation_id(self):
        self.correlation_id = str(uuid.uuid4())

    def to_dict(self):
        return {
            "payload": self.payload,
            "reply": self.reply_to,
            "correlation_id": self.correlation_id,
            "send_to": self.send_to,
            "create_time": self.create_time,
            "standard_create_time": self.standard_create_time,
            "status_code": self.status_code,
            "error_message": self.error_message
        }

    def to_protobuf(self):
        body = self.payload
        if isinstance(self.payload,str):
            body = self.payload.encode("utf-8")
        if isinstance(self.payload,(list,dict)):
            body = json.dumps(self.payload).encode("utf-8")
        kafka_packet = KafkaPacket(contentType=self.content_type,
                                   contentEncoding=self.content_encoding,
                                   sendTo=self.send_to,
                                   groupId=self.group_id,
                                   correlationId=self.correlation_id,
                                   replyTo=self.reply_to,
                                   messageId=self.message_id,
                                   timestamp=int(self.create_time),
                                   type=self.msg_type,
                                   userId=self.user_id,
                                   appId=self.app_id,
                                   body=body,
                                   routingKey=self.routing_key
                                   )
            
        for name, value in self.headers.items():
            headers = kafka_packet.headers.add()
            headers.name = name
            headers.value = value
        return kafka_packet

    def to_string(self):
        return "[message : %s , reply : %s , send_to : %s , correlation_id : %s , is_reply : %s , create_time : %s]" % (
            self.payload, self.reply_to, self.send_to, self.correlation_id, self.is_reply, self.standard_create_time)


if __name__ == "__main__":
    print(PublishesMessage("123", "123", "123", "123").to_string())
