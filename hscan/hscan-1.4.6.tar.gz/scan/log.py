import os
import sys
import asyncio
import datetime

from aiologger import Logger
from aiologger.utils import bind_loop
from aiologger.levels import LogLevel
from aiologger.formatters.base import Formatter
from aiologger.handlers.files import AsyncFileHandler
from aiologger.handlers.streams import AsyncStreamHandler


class AioLogger(object):
    def __init__(self, name=None, loop=None):
        # day_date = datetime.datetime.now().strftime('%Y-%m-%d')
        # log_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'logs/')
        # if not os.path.exists(log_path):
        #     os.makedirs(log_path)

        if loop is None:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        self.loop = loop
        # formatter = Formatter('[%(asctime)s] %(filename)s -> line:%(lineno)d [%(levelname)s] %(message)s')
        formatter = Formatter('%(asctime)s %(levelname)s %(message)s')

        logger = Logger(name=name, level=LogLevel.DEBUG)
        ash = bind_loop(AsyncStreamHandler, {})(stream=sys.stderr, level=LogLevel.DEBUG, formatter=formatter)
        logger.add_handler(ash)

        # log_name = f'{log_path}{name + ".log"}'
        # afh = AsyncFileHandler(log_name, 'a', encoding='utf-8')
        # afh.formatter = formatter

        self.logger = logger
        # self.logger.add_handler(afh)


def logger(name):
    return AioLogger(name).logger
