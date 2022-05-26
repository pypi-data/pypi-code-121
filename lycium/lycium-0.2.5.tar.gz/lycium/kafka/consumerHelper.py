#!/usr/bin/env python
# encoding: utf-8
from lycium.kafka.helper import Helper
from lycium.kafka.asyncWrapper import AsyncWrapper
# from lycium.kafka.logger import logger
from confluent_kafka import Producer,Consumer,KafkaError,KafkaException,TopicPartition
import json
import asyncio
import sys
from lycium.kafka.protocol.kafkapacket_pb2 import KafkaPacket
import logging

logger = logging.getLogger('kafka')


class ConsumerHelper(Helper):
    """
    消费者辅助
    """
    def __init__(self):
        super(ConsumerHelper, self).__init__()
        self._config["group.id"]= 0
        self._config['max.poll.interval.ms']= 60 * 1000
        self._config["session.timeout.ms"] = 6000
        self._config["heartbeat.interval.ms"] = 2000
        self._consumer = None
        self._partition = 0
        # 值的解码器
        self._value_deserializer = None

        # key 的解码器
        self._key_deserializer = None

        # protobuf 解码时需要
        self._objectParser = None
        # 发送消息的状态，True 是成功发送，False 是发送失败
        self._send_error = None
        self._send_msg = None
        # 最小同步消息数量
        self._minCommitCount = 100
        # 记录消息的偏移量,当kafka集群中某个节点(是使用topic的Leader节点)出现问题挂掉,此时还能接收到消息。
        # 有可能出现在节点恢复后，重发节点挂掉后发送的消息,所以通过记录偏移量避免重复处理消息
        self._offset = -1

        self._offsetDict={}
        self._loop  = asyncio.get_event_loop()
        self._is_debug = False

        # 是否停止消费标记z
        self._stop_consume_dict = {}

        self._poll_tasks = []
        # self._loop.call_later(0.0001,self._loop.create_task,self._poll_task())

    def open_debug(self):
        self._is_debug = True

    async def _poll_task(self):
        for task in self._poll_tasks:
            fn,params = task
            await fn(params)
        self._loop.call_later(0.0001,self._loop.create_task,self._poll_task())

    async def poll_task(self):
        for task in self._poll_tasks:
            fn,params = task
            await fn(params)

    def config_group_id(self,groupID):
        """
        配置groupID
        """
        self._config["group.id"] = groupID
        return self

    def config_max_poll_interval_ms(self,interval=60 * 1000):
        """ 
        配置 poll(拉取数据)的间隔，默认是设置60 秒
        """
        self._config['max.poll.interval.ms']=  interval
        

    def config_value_deserializer(self,method:str ="protobuf",object_parser=KafkaPacket):
        """
        配置对值的解码方式，可选有string、json和protobuf 三种方法
        当使用protobuf 时候需要指定objectParser 为需要转换成的对象,注意objectParser 是一个类
        """
        if method == "string":
            self._value_deserializer=bytes.decode
        if method == "json":
            self._value_deserializer = self._deserializer_json
        if method == "protobuf":
            self._value_deserializer = self._deserializer_protobuf
            self._object_parser = object_parser
        # self._config['value_deserializer']= self._value_deserializer
        return self


    def receive(self,topics:list,work):
        """
        订阅一系列主题，work 是处理接收到消息的方法
        此方法是阻塞的方式运行
        """
        if self._consumer is None:
            self._consumer = Consumer(self._config)
        try:
            
            partitions = [TopicPartition(t,self._partition) for t in topics]
            self._consumer.assign(partitions)
            self._consumer.subscribe(topics)
            msgCount = 0
            while 1:
                msg = self._consumer.poll(timeout=1.10)
                
                if msg is None:
                    continue
                if msg.error():
                    print("error here")
                    print(msg.error())
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        # 读取到分区的末尾了
                        sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                            (msg.topic(), msg.partition(), msg.offset()))
                    elif msg.error():
                        raise KafkaException(msg.error())
                else:
                    if msg.offset() > self._offset:
                        self._offset = msg.offset()
                        value =self._value_deserializer(msg.value())
                        work(value)
                    # msgCount += 1
                    # if msgCount % self._minCommitCount == 0:
                    #     pass
                        self._consumer.commit()
                    else:
                        print("skipping msg offset {0}".format(msg.offset()))
        finally:
            self._consumer.close()

    def receive_async(self,topics:list,work):
        """ 
        订阅一系列主题，work 是处理接收到消息的方法
        此方法是异步执行
        """
        async def receive_message(t):
            c_async,work,key = t
            if not self._stop_consume_dict[key]:
                msg = await c_async.poll(timeout=0.01)
                if msg is None:
                    return
                if msg.error():
                    print(msg.error())
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        # 读取到分区的末尾了
                        sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                            (msg.topic(), msg.partition(), msg.offset()))
                else:
                    if self._is_debug:
                        logger.debug("topic:{0},partition:{1},offset:{2},msg value:{3}".format(
                            msg.topic(), 
                            msg.partition(), 
                            msg.offset(),
                            msg.value()
                        ))
                    offset_key = "{0}-{1}".format(key,msg.partition())
                    if offset_key not in self._offsetDict:
                        self._offsetDict[offset_key] = -1
                    if msg.offset() > self._offsetDict[offset_key]:
                        self._offsetDict[offset_key] = msg.offset()
                        value = self._value_deserializer(msg.value())
                        if asyncio.iscoroutine(work) or asyncio.iscoroutinefunction(work):
                            await work(value)
                        else:
                            work(value)
                        # c_async.commit()
                
            else:
                # 停止消费(接收信息)，关闭连接
                try:
                    if self._consumer is not None:
                        self._consumer.close()
                except Exception as e:
                    logger.exception(e)

        key="_".join(topics)
        self._stop_consume_dict[key] = False
        c = Consumer(self._config)
        partitions = [TopicPartition(t,self._partition) for t in topics]
        c.assign(partitions)
        c.subscribe(topics)
        c_async = AsyncWrapper(c,methods=["poll"])
        # self._offsetDict[c_async] = -1
        self._poll_tasks.append((receive_message,(c_async,work,key)))
        self._loop.call_later(0.00001,self._loop.create_task,self._poll_task())


    def stop_consumer(self,topics:list):
        """ 
        停止接收信息
        """
        
        key="_".join(topics)
        logger.info("{0} 停止接收信息".format(key))
        self._stop_consume_dict[key] = True
            
    def _deserializer_json(self,v):
        """
        把bytes 转dict
        """
        d = json.loads(v.decode("utf-8"))
        self._json_bytes_recover(d)
        return d

    def _json_bytes_recover(self,d):
        """
        对字典里面的字节数组进行恢复
        """
        to_remove_keys = []
        for k in d:
            if k.startswith("_c_"):
                update_key=k[3:]
                d[update_key]=d[update_key].encode("utf8")
                to_remove_keys.append(k)
            if isinstance(d[k],dict):
                self._json_bytes_recover(d[k])
        for k in to_remove_keys:
            del d[k]

    def _deserializer_protobuf(self,v):
        """
        把bytes 转成protobuf
        """
        op = self._object_parser()
        if '_register_private' in str(v):
            op = None
        else:
            op.ParseFromString(v)
        return op

    def config_message_size(self,size):
        self._config['fetch.message.max.bytes'] = size
