#!/usr/bin/env python
# encoding: utf-8
from lycium.kafka.protocol.kafkapacket_pb2 import KafkaPacket
from lycium.kafka.producerHelper import ProducerHelper
from lycium.kafka.consumerHelper import ConsumerHelper
from lycium.kafka.publishesMessage import PublishesMessage
# from publishesResponse import PublishesResponse
from lycium.kafka. workerDelegate import WorkerDelegate
from typing import Optional, Dict, List, Any
import asyncio
import traceback
# from lycium.kafka.logger import logger
import uuid
import time
import logging

logger = logging.getLogger('kafka')


class KafkaWorker(object):
    """ 
    """

    def __init__(self,
                 hosts: list,
                 partition: int = 0,
                 private_topic: str = "",
                 kerberos_service_name: str = None,
                 kerberos_keytab: str = None,
                 Kerberos_principal: str = None,
                 security_protocol: str = "sasl_plaintext",
                 sasl_mechanisms: str = "PLAIN",
                 sasl_username: str = None,
                 sasl_password: str = None,
                 reconnect_interval: int = 500,
                 group_id = 0,
                 max_poll_interval_ms = 60 * 1000,
                 messageType = "direct",
                 is_debug = False,
                 max_message_size =0
                 ):
        """

        :params hosts kafka 集群节点
        :params serialization 序列化使用方式,支持json,protobuf和string
        :params partition 分区
        :params private_topic 私人topic，用于发送信息后接收响应的信息
        :params kerberos_service_name kerberos 验证选项
        :params kerberos_keytab    kerberos 验证选项
        :params Kerberos_principal  kerberos 验证选项
        :params security_protocol 鉴权所使用的协议，使用默认sasl_plaintext 就可以
        :params sasl_mechanisms 使用plain 认证需要配置
        :params sasl_username 使用plain 认证需要配置
        :params sasl_password 使用plain 认证需要配置
        :params reconnect_interval 断线重连的时间间隔，单位是毫秒，默认是500
        :params group_id 订阅服务指定消费者组id
        :params messageType direct:组播,订阅同一个topic，消费者组会相同，一条消息只会被组内一个消费者接收.fanout:广播,订阅同一个topic，但是消费者组会使用uuid，所有组都会收到信息
        :params max_message_size:配置数据包的大小
        """
        logger.debug("KafkaWorker init.")
        self.messageType = messageType
        self.messageTopic = ""
        if messageType == "fanout":
            # 使用广播模式
            group_id= str(uuid.uuid4())
            private_topic =""
        if private_topic !="":
            private_topic = private_topic+"-"+str(uuid.uuid4())[:10]
        else:
            private_topic = str(uuid.uuid4())

        serialization = "protobuf"
        self._producer = ProducerHelper()
        self._producer.config_servers(hosts).config_value_serializer(serialization).config_partition(partition)
        self._producer.config_reconnect_interval(reconnect_interval)

        self._consumer = ConsumerHelper()
        self._consumer.config_servers(hosts).config_value_deserializer(serialization).config_partition(partition)
        self._consumer.config_max_poll_interval_ms(max_poll_interval_ms)
        self._consumer.config_reconnect_interval(reconnect_interval)
        self._consumer.config_group_id(group_id)
        if kerberos_service_name and kerberos_keytab and Kerberos_principal:
            self._producer.config_kerberos_service_name(kerberos_service_name)
            self._producer.config_kerberos_keytab(kerberos_keytab)
            self._producer.config_kerberos_principal(Kerberos_principal)
            self._producer.config_security_protocol(security_protocol)

            self._consumer.config_kerberos_service_name(kerberos_service_name)
            self._consumer.config_kerberos_keytab(kerberos_keytab)
            self._consumer.config_kerberos_principal(Kerberos_principal)
            self._consumer.config_security_protocol(security_protocol)

        if sasl_mechanisms and sasl_username and sasl_password:
            self._producer.config_sasl_mechanisms(sasl_mechanisms)
            self._producer.config_sasl_username(sasl_username)
            self._producer.config_sasl_password(sasl_password)
            self._producer.config_security_protocol(security_protocol)

            self._consumer.config_sasl_mechanisms(sasl_mechanisms)
            self._consumer.config_sasl_username(sasl_username)
            self._consumer.config_sasl_password(sasl_password)
            self._consumer.config_security_protocol(security_protocol)

        if isinstance(max_message_size,int)  and max_message_size>0:
            self._producer.config_message_size(max_message_size)
            self._consumer.config_message_size(max_message_size)

        # 发出信息后，等待响应的信息列表
        self._wait_response_message: Dict[str, PublishesMessage] = {}
        # 注册接收指定topic 的消费者
        self._consumer_registers: Dict[str, callable] = {}
        # 如果指定routingKey，就使用topic+routingKey实现分发方法。(在这里routingKey和method都是用于分发调用业务方法，可认为是等价)
        self._method_registers: Dict[str,callable] = {}
        # 因为可能会往一些没有存在是topic发送信息，所以需要正式发送前发送hello 信息
        self._register_topic: Dict[str, int] = {}

        self._private_topic = private_topic
        # self._private_topic = str(uuid.uuid4())

        self.event_loop = asyncio.get_event_loop()

        # self._register_private_topic()
        self._open_private_topic()
        if is_debug:
            self._consumer.open_debug()

    def get_valid_private_topic(self,private_topic:str):
        """ 
        当程序部署在k8s 上时,会遇到多副本的情况,private topic 需要不一样
        容器也有可能不断重启，这时候就需要 private topic 没有变化
        """

    async def _on_message(self, message: KafkaPacket):
        """ 
        当接收到kafka 信息的时候会触发调用这个方法
        分两种情况，1 发送的信息后收到的回复 2 接收到新信息
        """
        logger.debug("_on_message, _wait_response_message length:{}".format(self._wait_response_message))
        if message.correlationId in self._wait_response_message:
            # 发送信息后收到的回复
            publish_message = self._wait_response_message[message.correlationId]
            del self._wait_response_message[message.correlationId]
            logger.debug(
                "response msg.correlationId, msg.body: {0}, {1}".format(message.correlationId, message.body))
            # publish_message.callback(message)
            worker_delegate = WorkerDelegate(publish_message.callback, message, self._private_topic)
            await worker_delegate.executor()
        else:
            # 接收到新的信息后查询处理方法，如果没有注册，则丢弃
            if message.sendTo in self._consumer_registers:
                deal_function = self._consumer_registers[message.sendTo]
                if message.routingKey:
                    key = "{0}-{1}".format(message.sendTo,message.routingKey)
                    if key in self._method_registers:
                        deal_function = self._method_registers[key]
                # deal_result = deal_function(message.body)
                # # print("deal_result:{0}".format(deal_result))
                # response_publish_message = PublishesMessage(
                #     body=deal_result,
                #     reply=self._private_topic,
                #     send_to=message.reply,
                #     correlation_id=message.correlation_id,
                #     is_reply=True
                # )
                worker_delegate = WorkerDelegate(deal_function, message, self._private_topic)
                response_publish_message = await worker_delegate.executor()
                # 查询信息中包含的是否需要回复消息，没有replyTo即不需要，就不发送回复信息
                if message.replyTo:
                    self._send_message(response_publish_message.to_protobuf())

    def _send_message(self, message):
        """ 
        发送信息
        """
        self._register_private_topic()
        if isinstance(message, PublishesMessage):
            
            value = message.to_protobuf()
            is_reply = message.is_reply
            need_reply = True if message.reply_to else False
            if not message.send_to in self._register_topic:
                self._producer.send_async_without_callback(message.send_to, value={"_register_private": "open"})
                self._register_topic[message.send_to] = 1
            if value.body:
                self._producer.send_async_without_callback(message.send_to, value=value)
                logger.debug("_send_message: {}".format(message.to_dict()))
                if not is_reply and need_reply:
                    self._wait_response_message[message.correlation_id] = message
        else:
            
            if not message.sendTo in self._register_topic:
                self._open_topic(message.sendTo)
                self._register_topic[message.sendTo] = 1
            if message.body:
                
                self._producer.send_async_without_callback(message.sendTo, value=message)
                logger.debug("_send_message: {}".format(message))

    async def _bind_to_on_message(self, value):
        """ 
        绑定消费者收到信息后调用 _on_message
        """
        if value is None:
            return
        logger.debug("_bind_to_on_message: {}".format(value))
        try:
            await self._on_message(value)
        except Exception as e:
            logger.exception(traceback.format_exc())

    def subscribe(self, topic: str, work: callable,routingKey=""):
        """ 
        订阅主题
        """
        logger.debug("subscribe topic: {}".format(topic))
        if topic not in self._consumer_registers:
            self._consumer.receive_async([topic], self._bind_to_on_message)
            self._consumer._loop.call_later(0.01,self._consumer._loop.create_task,self._consumer._poll_task())

            self._consumer_registers[topic] = work
            if self.messageType == "fanout":
                self.messageTopic = topic
        key = "{0}-{1}".format(topic,routingKey)

        if key not in self._method_registers:
            self._method_registers[key] =work
    
    def _open_topic(self, topic):
        """ 
        多次发送保障打开通道
        """
        for _ in range(10):
            self._producer.send_async_without_callback(topic, value={"_register_private": "open"})

    def _open_private_topic(self):
        """ 
        多次发送保障打开通道
        """
        for _ in range(100):
            self._producer.send_async_without_callback(self._private_topic, value={"_register_private": "open"})
            time.sleep(0.01)
            #asyncio.sleep(0.01)        

    def _register_private_topic(self):
        """ 
        注册私密的topic,用于发送信息后接收到信息
        """
        if self._private_topic == "":
            return
        if self._private_topic not in self._consumer_registers:
            self._open_topic(self._private_topic)

        self.subscribe(self._private_topic, lambda no_use: no_use)

    async def send(self, topic: str,
                   message: bytes,
                   content_type: str = None,
                   content_encoding: str = 'utf-8',
                   group_id: str = '0',
                   message_id: str = None,
                   msg_type: str = None,
                   user_id: str = None,
                   app_id: str = None,
                   headers: dict = None,
                   need_reply: bool = True, 
                   routing_key: str = None
                   ):
        """ 
        发送信息
        """
        logger.info("send message: {}".format(message))
        waiter = self.event_loop.create_future()

        def for_callback(response):
            waiter.set_result(response)
            return waiter.result()
        
        reply_to = self._private_topic if need_reply else None

        if self.messageType == "fanout" and self.messageTopic !="":
            reply_to = self.messageTopic

        publish_message = PublishesMessage(
            payload=message,
            reply_to=reply_to,
            send_to=topic,
            correlation_id="",
            content_type=content_type,
            content_encoding=content_encoding,
            group_id=group_id,
            message_id=message_id,
            msg_type=msg_type,
            user_id=user_id,
            app_id=app_id,
            headers=headers,
            callback=for_callback,
            routing_key=routing_key
        )
        publish_message.new_correlation_id()
        self._send_message(publish_message)
        if not need_reply:
            return
        await self._consumer.poll_task()
        return await waiter

    def stop_consumer(self, topic: str):
        """ 
        停止接收数据
        """
        self._consumer.stop_consumer([topic])
        del self._consumer_registers[topic]
