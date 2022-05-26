#!/usr/bin/env python
# encoding: utf-8
from lycium.kafka.helper import Helper
from confluent_kafka import Producer,Consumer,KafkaError,KafkaException,TopicPartition
from lycium.kafka.asyncWrapper import AsyncWrapper
import json
import asyncio
import datetime
from threading import Thread
import time
import uuid

class ProducerHelper(Helper):
    """
    生产者辅助
    """
    def __init__(self,flush_interval_time=0.001):
        super(ProducerHelper, self).__init__()
        self._config['message.send.max.retries']= 5

        self._producer = None
        self._partition = 0
        # 值的编码器
        self._value_serializer = None
        # key 的编码器
        self._key_serializer = None
        self._flush_interval_time = flush_interval_time
        self._event_loop = asyncio.get_event_loop()
        self._poll_thread = Thread(target=self._poll)
        self._poll_thread.start()
        
    def _poll(self):
        while True:
            if self._producer is not None:
                try:
                    self._producer.poll(0.1)
                except Exception as e:
                    print(e)
                time.sleep(0.1)
            else:
                time.sleep(0.5)
              
 
    def config_value_serializer(self,method :str ="protobuf"):
        """
        配置对值的编码方式，可选有string、json和protobuf 三种方法
        """
        if method == "string":
            self._value_serializer=self._serializer_string
        if method == "json":
            self._value_serializer=self._serializer_json
        if method == "protobuf":
            self._value_serializer=self._serializer_protobuf
        # self._config['value.serializer'] = self._value_serializer
        return self

    def send(self,topic:str,key=None,value=None):
        """
        发送消息,返回错误信息和发送的记录,如果成功发送，错误信息是None
        同步的方式
        """
        if key is None:
            key = str(uuid.uuid4())
        self._send_error=None
        self._send_msg=None
        if self._producer is None:
            self._producer= Producer(self._config)
        try:
            value = self._value_serializer(value)
            self._producer.produce(topic,key=key,value=value,partition=self._partition,callback=self._sendReport)
            self._producer.poll(5)
            #self._producer.flush(5)
            if False:
                print("send result:")
                print(self._send_error)
            return self._send_error,self._send_msg
        except Exception as ee:
            return ee,None

    def send_async(self,topic:str,key=None,value=None,callback=lambda error,value: print(value)):
        if key is None:
            key = str(uuid.uuid4())
        if self._producer is None:
            self._producer= Producer(self._config)

        dealCount = self._producer.poll(0)
        value = self._value_serializer(value)
        self._producer.produce(topic,key=key,value=value,partition=self._partition,callback=callback)

    def send_async_without_callback(self,topic:str,key=None,value=None):
        """ 
        :params topic: 主题
        :params key: 默认为None
        :params value: 要发送的信息
        confluent_kafka 发送本身就是异步操作，所以可以直接调用，但是需要做的是要调用
        """
        if key is None:
            key = str(uuid.uuid4())
        if self._producer is None:
            p = Producer(self._config)
            self._producer = AsyncWrapper(p,methods=["flush"])
            # self._event_loop.call_later(self._flush_interval_time,self._event_loop.create_task,self._async_flush())
        if isinstance(value, dict) and '_register_private' in value.keys():
            value = self._serializer_json(value)
        else:
            value = self._value_serializer(value)
        self._producer.produce(topic,key=key,value=value,partition=self._partition)

    def flush(self):
        if self._producer is not None:
            self._producer.flush(3)
    
    async def _async_flush(self):
        """ 

        """
        #if self._producer is not None and asyncio.iscoroutine(self._producer.flush()):
            # print("{0} async flushing".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")))
            #await self._producer.flush(3)
        await self._producer.flush(3)
        self._event_loop.call_later(self._flush_interval_time,self._event_loop.create_task,self._async_flush())

    def _serializer_json(self,v):
        """
        把 dict 转 bytes
        """
        self._json_bytes_convent(v)
        return json.dumps(v).encode("utf-8")
    def _serializer_string(self,v):
        """
        把 dict 转 bytes
        """
        
        return v.encode("utf-8")

    def _serializer_protobuf(self,v):
        """
        把protobuf 转成 bytes
        """
        v2 = v.SerializeToString()
        return v2

    def _json_bytes_convent(self,d):
        """
        对字典 数据里面包含的字节数组转换成字符串
        """
        tempDict = {}
        
        for k in d:
            v = d[k]
            if isinstance(v,dict):
                self._json_bytes_convent(v)
            if isinstance(v,bytes):
                d[k] = v.decode("utf8")
                addKey = "_c_{0}".format(k)
                tempDict[addKey]=1
        d.update(tempDict)

    def _send_report(self,err,msg):
        """
        用于检测异步发送消息的状态
        """
        self._send_error=err
        self._send_msg = msg
        # if err is not None:
        #     print("Delivery failed for User record {}: {}".format(msg.key(), err))
        #     return
        # print('User record {} successfully produced to {} [{}] at offset {}'.format(
        # msg.key(), msg.topic(), msg.partition(), msg.offset()))

    def config_message_size(self,size):
        self._config['message.max.bytes'] = size
