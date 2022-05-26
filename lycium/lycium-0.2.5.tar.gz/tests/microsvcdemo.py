#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" 
使用封装kafka的微服务框架的demo
"""
from loguru import logger
from lycium.microsvc.applicationServer import ApplicationService
from lycium.microsvc.context import Context
import datetime

kafka_hosts = ["172.16.28.190:9093","172.16.28.190:9094","172.16.28.190:9095"]
topic = "microsvc-demo"

app = ApplicationService(topic=topic, 
                        hosts=kafka_hosts,
                        app_code="1000",
                        username="",
                        password="",
                        )

@app.add_read("test")
async def now(context:Context):
    """
    测试用的业务方法
    """
    logger.info(context.get_payload())

    return {
        "code":0,
        "msg":"success",
        "data":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
if __name__ == "__main__":
    app.run()