#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lycium.kafka.kafkaWorker import KafkaWorker
from lycium.microsvc.router import Router
from lycium.microsvc.middlewares.exceptionMiddleware import ExceptionMiddleware
from lycium.microsvc.middlewares.logMiddleware import LogMiddleware
from lycium.microsvc.middlewares.websocketPackageMiddleware import WebsocketPackageMiddleware
from tornado.ioloop import IOLoop



class ApplicationService(object):
    """ 
    提供使用kafka 接收请求，并进行分发
    """
    def __init__(self,topic:str,hosts:list,app_code:str,username:str="",password:str=""):
       """ 
       :params topic 订阅的topic
       :params hosts kafka 节点的地址列表,如["127.0.0.1:9092","127.0.01:9093"]
       :params app_code 应用程序代码，用于返回错误时候区分不同的微服务
       :params username kafka 集群的用户名
       :params password kafka 集群的密码
       """
       self._topic = topic
       self._app_code = app_code
       worker = KafkaWorker(hosts=hosts,
                            private_topic=topic+"-private",
                            group_id=topic + "-group",
                            sasl_username = username,
                            sasl_password = password)
        
       self._worker = worker
       self._router = Router(self._worker)
       self.set_environment("app_code", app_code)
    
    def set_environment(self,key,value):
        """
        设置全局可用的环境变量 
        """
        self._router.set_environment(key,value)

    def add_middleware(self,middleware):
        """ 
        新增中间件
        """
        self._router.add_middleware(middleware)

    def add_read(self,module_name):
        """ 
        新增读权限的业务方法
        """
        def decorate(func):
            self._router.add_read(func, module_name)
            return func
        return decorate

    def add_create(self,module_name):
        """ 
        新增读权限的业务方法
        """
        def decorate(func):
            self._router.add_create(func, module_name)
            return func
        return decorate

    def add_update(self,module_name):
        """ 
        新增读权限的业务方法
        """
        def decorate(func):
            self._router.add_update(func, module_name)
            return func
        return decorate

    def add_delete(self,module_name):
        """ 
        新增读权限的业务方法
        """
        def decorate(func):
            self._router.add_delete(func, module_name)
            return func
        return decorate

    def init_middlewares(self):
        """ 
        加载常用的中间件
        """
        self.add_middleware(WebsocketPackageMiddleware)
        self.add_middleware(ExceptionMiddleware)
        self.add_middleware(LogMiddleware)

    def run(self):
        """ 
        服务开始运行
        """
        self.init_middlewares()
        self._worker.subscribe(self._topic, self._router.service)
        IOLoop.instance().start()