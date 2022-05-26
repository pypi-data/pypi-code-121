#!/usr/bin/env python
# encoding: utf-8
import logging
from lycium.microsvc.utils import decode_websocket_package,encode_websocket_package
from lycium.microsvc.context import Context

logger = logging.getLogger('microsvc')


async def WebsocketPackageMiddleware(context:Context):
    """ 
    处理websocket 网关发送过来的请求
    """
    requestPacket= decode_websocket_package(context.request)
    result = await context.next()
    return encode_websocket_package(result,requestPacket)

    