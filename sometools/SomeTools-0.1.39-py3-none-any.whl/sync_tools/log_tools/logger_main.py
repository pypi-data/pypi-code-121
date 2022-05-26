# https://loguru.readthedocs.io/en/stable/overview.html#ready-to-use-out-of-the-box-without-boilerplate

import sys
from sometools.sync_tools.base import Base
from loguru import logger as context_logger


class LogMixIn(Base):
    # __instance = None
    # def __new__(cls, *args, **kwargs):
    #     if not cls.__instance:
    #         cls.__instance = super(GeneralLog, cls).__new__(cls, *args, **kwargs)
    #     return cls.__instance

    # def __init__(self, *args, log_file_rec: bool = False, log_file_name: str = '', log_file_addr: str = '', **kwargs):
    def __init__(self, *args, **kwargs):
        super(LogMixIn, self).__init__(*args, **kwargs)
        log_file_rec = kwargs.get('log_file_rec')
        log_file_retention_days = kwargs.get('log_file_retention_days', 7)
        log_file_name = kwargs.get('log_file_name')
        log_file_addr = kwargs.get('log_file_addr')
        context_logger.remove()
        context_logger.add(sys.stdout, colorize=True, format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> <cyan>{extra[uuid1]}</cyan> <blue>{extra[uuid2]}</blue> <level>{message}</level>", enqueue=True)
        if log_file_rec:
            if log_file_name and log_file_addr:
                log_name = f'{log_file_addr}{log_file_name}.log'
                log_error_name = f'{log_file_addr}{log_file_name}_error.log'
            else:
                log_name = f'{log_file_name}.log'
                log_error_name = f'{log_file_name}_error.log'
            # https://loguru.readthedocs.io/en/stable/_modules/loguru/_logger.html?highlight=cyan#
            context_logger.add(log_name, format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> {level} <cyan>{extra[uuid1]}</cyan> <blue>{extra[uuid2]}</blue> {message}", rotation="23:00", retention=f"{log_file_retention_days} days", encoding='utf-8', enqueue=True)
            context_logger.add(log_error_name, format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> {level} <cyan>{extra[uuid1]}</cyan> <blue>{extra[uuid2]}</blue> {message}", rotation="23:00", retention=f"{log_file_retention_days} days", encoding='utf-8', enqueue=True, level='ERROR')

        self.context_logger = context_logger
        self.logger = self.get_logger

    def get_logger(self, **kwargs):
        uuid1 = kwargs.get('uuid1') or ''
        uuid2 = kwargs.get('uuid2') or ''
        self.context_logger = self.context_logger.patch(lambda record: record["extra"].update(uuid1=uuid1, uuid2=uuid2))
        return self.context_logger

# aa = GeneralLog()
# aa.logger.info('info')
# aa.logger.warning('warning')
# aa.logger.debug('debug')
# aa.logger.error('error')


# from loguru import logger
# import os
#
# logs_dir = f"{os.path.dirname(os.path.dirname(__file__))}/log"
# log_file_name = 'ApiTestLogs'
#
#
# class Loggings:
#     __instance = None
#     logger.add(f"{logs_dir}/{log_file_name}.log", rotation="500MB", encoding="utf-8", enqueue=True,
#                retention="10 days")
#
#     def __new__(cls, *args, **kwargs):
#         if not cls.__instance:
#             cls.__instance = super(Loggings, cls).__new__(cls, *args, **kwargs)
#
#         return cls.__instance
#     def __init__(self):
#         self.className = self.__class__.__name__
#
#     def info(self, msg):
#
#         return logger.info(msg)
#
#     def debug(self, msg):
#         return logger.debug(msg)
#
#     def warning(self, msg):
#         return logger.warning(msg)
#
#     def error(self, msg):
#         '''
#         打印错误信息
#         '''
#         return logger.error(msg)
#
#     def exception(self,msg):
#         '''
#         打印异常信息方法
#         '''
#         return logger.exception(msg)
