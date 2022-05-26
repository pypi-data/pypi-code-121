#!/usr/bin/env python
# coding:utf-8
""" 
上下文，用于实现中间件功能
"""
import asyncio
import json
# from router import Router
import numpy as np
import pandas as pd
from lycium.kafka.protocol.kafkapacket_pb2 import KafkaPacket
import logging

logger = logging.getLogger('microsvc')


class Context(object):

    def __init__(self,request:KafkaPacket,router,worker):
        self.request = request
        self.raw_request = request
        self.router = router
        self.worker = worker
        self._middlewares = []
        self._index = -1
        self._environment ={}

    def set_environment(self,environment):
        """ 
        设置全局传递的环境变量
        """
        self._environment = environment
    
    def get(self,key:str):
        """ 
        获取指定key的值
        """
        return self._environment.get(key)
    
    def set(self,key:str,value):
        """ 
        设置key的值
        """
        self._environment[key] = value

    def get_payload(self):
        """ 
        获取传递过来的参数
        """
        return self.get("payload")
    def add_middleware(self,middleware):
        self._middlewares.append(middleware)
    
    def init_middlewares(self,middlewares:list):
        self._middlewares = middlewares
    
    async def next(self):
        self._index += 1
        middleware_length = len(self._middlewares)
        if self._index < middleware_length:
            func = self._middlewares[self._index]
            return await func(self)            

    async def send(self,topic,message,raw_response=False): 
        result = await asyncio.wait_for(self.worker.send(topic=topic,message = json.dumps(message)),30)
        # result = await self.worker.send(topic=topic,message = json.dumps(message))
        if not raw_response:
            return json.loads(result.body)
        return result

    def left_join(self,data_left,data_right,on):
        """ 实现左连接"""
        df_right = pd.DataFrame(data_right)
        df_left = pd.DataFrame(data_left)
        df = pd.merge(df_left,df_right,left_on=on,right_on=on,how="left")
        df =df.replace(np.nan, '', regex=True)

        return df.to_dict('records')

    def inner_join(self,data_left,data_right,on):
        """ 实现内连接"""
        df_right = pd.DataFrame(data_right)
        df_left = pd.DataFrame(data_left)
        df = pd.merge(df_left,df_right,left_on=on,right_on=on,how="inner")
        df =df.replace(np.nan, '', regex=True)

        return df.to_dict('records')
