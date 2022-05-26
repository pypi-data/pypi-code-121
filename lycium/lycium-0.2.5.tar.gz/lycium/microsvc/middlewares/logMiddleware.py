#!/usr/bin/env python
# encoding: utf-8
""" 
日志中间件
"""
import logging
from lycium.microsvc.context import Context


logger = logging.getLogger('microsvc')

async def LogMiddleware(context:Context):
    """ """
    logger.info(context.request)
    result = await context.next()
    logger.info(result)
    return result