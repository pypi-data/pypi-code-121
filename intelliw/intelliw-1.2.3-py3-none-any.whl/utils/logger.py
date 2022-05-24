#!/usr/bin/env python
# coding: utf-8
from intelliw.config import config
import threading
import logging.handlers
import os

framework_logger = None
user_logger = None

class Logger():
    _instance_lock = threading.Lock()

    def __new__(cls):
        """ 单例,防止调用生成更多 """
        if not hasattr(Logger, "_instance"):
            with Logger._instance_lock:
                if not hasattr(Logger, "_instance"):
                    Logger._instance = object.__new__(cls)
        return Logger._instance

    def __init__(self):
        self.framework_logger = self.__get_logger("Framework Log")
        self.user_logger = self.__get_logger("Algorithm Log")

    def __get_logger(self, logger_type):
        logger = logging.getLogger(logger_type)
        if not logger.handlers:
            level = logging.INFO if config.is_server_mode else logging.DEBUG
            FORMAT = '[%(name)s] %(asctime)s %(levelname)s %(filename)s:%(lineno)s: %(message)s'
            logging.basicConfig(level=level, format=FORMAT, datefmt='%Y-%m-%d %H:%M:%S')
            log_path = './logs/'
            file_name = 'iw-algo-fx.log' if logger_type == 'Framework Log' else 'iw-algo-fx-user.log'
            if not os.path.exists(log_path):
                os.makedirs(log_path)
            if os.access(log_path, os.W_OK):
                time_file_handler = logging.handlers.TimedRotatingFileHandler(
                    os.path.join(log_path, file_name),
                    when='D',
                    interval=2,
                    backupCount=180
                )
                log_format_console = logging.Formatter('[%(name)s] %(levelname)s %(asctime)s %(filename)s:%(lineno)s: %(message)s', datefmt='%H:%M:%S')
                time_file_handler.suffix = '%Y-%m-%d-%H.log' 
                time_file_handler.setLevel(level)
                time_file_handler.setFormatter(log_format_console)
                logger.addHandler(time_file_handler)
        return logger

    def get_logger(self, logger_type):
        if logger_type == "a":
            return self.user_logger
        return self.framework_logger


def get_logger():
    global framework_logger
    if framework_logger is None:
        framework_logger = Logger().get_logger("f")
    return framework_logger

def get_user_logger():
    global user_logger
    if user_logger is None:
        user_logger = Logger().get_logger("a")
    return user_logger
