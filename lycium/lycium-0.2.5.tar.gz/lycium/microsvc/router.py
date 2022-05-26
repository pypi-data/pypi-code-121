#!/usr/bin/env python
# encoding: utf-8
from lycium.kafka.protocol.kafkapacket_pb2 import KafkaPacket
from lycium.kafka.kafkaWorker import KafkaWorker
from .context import Context
import json
import asyncio
import logging

logger = logging.getLogger('microsvc')


class Router(object):
    """ 
    路由类，辅助解决一下重现性工作
    """
    def __init__(self,worker:KafkaWorker):
        self.worker = worker
        self.middlewares = []
        self._method_mapping = {}
        self._environment = {}

    def set_environment(self,key, value):
        """ 设置全局可用的环境变量"""
        self._environment[key] = value

    def add_middleware(self,middleware):
        self.middlewares.append(middleware)

    def _add_method(self,callback: callable,module_name:str,permission:str,method_name:str=""):
        """ 
        添加一个方法
        """
        if method_name == "":
            method_name = callback.__name__
        if method_name not in self._method_mapping:
            self._method_mapping[method_name] ={"callback":callback,"module_name":module_name,"permission":permission}
        else:
            logger.error("重复添加 {0}".format(method_name))
    
    def add_read(self,callback: callable,module_name:str,method_name:str=""):
        self._add_method(callback,module_name,"read_permission",method_name)

    def add_create(self,callback: callable,module_name:str,method_name:str=""):
        self._add_method(callback,module_name,"create_permission",method_name)

    def add_update(self,callback: callable,module_name:str,method_name:str=""):
        self._add_method(callback,module_name,"create_permission",method_name)

    def add_delete(self,callback: callable,module_name:str,method_name:str=""):
        self._add_method(callback,module_name,"update_permission",method_name)

    async def service(self,message:KafkaPacket):
        """ 
        提供服务的入口
        """
        try:
            c = Context(message,self,self.worker)
            c.init_middlewares(self.middlewares)
            c.set_environment(self._environment)
            c.add_middleware(self.route)
            return await c.next()

        except Exception as e:
            logger.exception(e)
            return {
                "code":1000,
                "msg":str(e)
            }

    async def route(self,context:Context):
        """ 
        路由功能
        """
        payload = json.loads(context.request.body)
        callback = None
        if context.request.routingKey:
            routingKey = context.request.routingKey
            callback = self._method_mapping[routingKey]["callback"]
        if not callback and "method" in payload and payload["method"] in self._method_mapping:
            callback = self._method_mapping[payload["method"]]["callback"]
        if not callback:
            return {
                "code":int(self._environment["app_code"])+1,
                "msg":"cant not find callback"
            }
        context.set("payload",payload)

        if asyncio.iscoroutinefunction(callback) or asyncio.iscoroutine(callback):
            return await callback(context)
        return callback(context)
