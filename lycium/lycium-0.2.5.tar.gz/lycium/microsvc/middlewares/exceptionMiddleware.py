#!/usr/bin/env python
# config: utf-8
""" 
捕捉异常,因为请求有可能来自是websocket 网关，
直接返回一个字典对象会导致websocket 网关 无法解析
需要 WebsocketPackageMiddleware 中间件进行处理
"""
import logging
from lycium.microsvc.context import Context

logger = logging.getLogger('microsvc')


async def ExceptionMiddleware(context:Context):
    """ """
    try:
        return await context.next()
    except Exception as e:
        logger.exception(e)
        app_code = context.get("app_code")

        return {
                "code":int(app_code)+5,
                "msg":str(e)
            }