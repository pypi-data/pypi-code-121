#!/usr/local/bin/python
# -*- coding:utf-8 -*-

# 由于每个配置必须要有root 所以这里有个root，但我们不使用他，因为在logger对象中无法获取root的hander
# 来设置过滤器，这里我们使用all代表文件和控制台的输出，配置文件的使用模式是在[loggers]中申明有哪些logger
# 在 [logger_xxx]中对应每个logger的配置，下面的结构完全遵循这一结构

import logging
import logging.config
import os
import sys
import time
from functools import wraps
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler
from os import path

"""
这个是logger的过滤器  可以过滤掉多余的日志 让对应级别的日志写入对应级别的文件
通过日志的级别和传入的级别对比 返回true or false
"""


class BaseLogFilter(logging.Filter):
    def __init__(self, name='', logname="_1"):
        super(BaseLogFilter, self).__init__(name)
        self.logname = logname


class LogLevelFilter(BaseLogFilter):
    def __init__(self, name='', level=logging.DEBUG, levels=None):
        super(LogLevelFilter, self).__init__(name)
        self.level = level
        self.levels = levels

    def filter(self, record):
        if self.levels == None:
            return record.levelno == self.level
        else:
            for level in self.levels:
                if record.levelno == level:
                    return True
            return False


"""
单例模式的一种实现
"""


def singleton(cls):
    instances = {}

    @wraps(cls)
    def getinstance(*args, **kw):
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]

    return getinstance


"""
Logger的主体，主要靠这个实现
加入单例模式下遇到MLogger调用静态方法会出问题
"""


# @singleton
class MLogger(object):
    def __init__(self, logfiledir=None, filter=None):
        if logfiledir:
            # 获取logger实例，如果参数为空则返回root logger
            self.confFilePath(logfiledir)
        # 这是输出流
        self.streamoutlogger = self.streamOutLogger()
        # 这是错误流
        self.streamerrlogger = self.streamErrLogger()

        self.streamlogger = self.streamLogger()

        self._alllogger = None
        self._filelogger = None
        self._timerotatingfilelogger = None
        self._rotatingfilelogger = None
        self.fileter = filter

        self.maxBytes = 1024 * 1024 * 1024
        self.backupCount = 10

    def set_logfiledir(self, logfiledir):
        self.confFilePath(logfiledir)

    @property
    def alllogger(self):
        # logger 对象是alllogger 及所有日志对象
        if not self._alllogger:
            self._alllogger = self.allLogger(self.logfiledir)
        return self._alllogger

    @alllogger.setter
    def alllogger(self, value):
        self._alllogger = value

    @property
    def filelogger(self):
        if not self._filelogger:
            self._filelogger = self.fileLogger(self.logfiledir)
        return self._filelogger

    @filelogger.setter
    def filelogger(self, value):
        self._filelogger = value

    @property
    def timerotatingfilelogger(self):
        if not self._timerotatingfilelogger:
            self._timerotatingfilelogger = self.timeRotatingFileLogger(self.logfiledir, self.fileter)
        return self._timerotatingfilelogger

    @timerotatingfilelogger.setter
    def timerotatingfilelogger(self, value):
        self._timerotatingfilelogger = value

    @property
    def rotatingfilelogger(self):
        if not self._rotatingfilelogger:
            self._rotatingfilelogger = self.RotatingFileLogger(self.logfiledir, self.fileter, maxBytes=self.maxBytes,
                                                               backupCount=self.backupCount)
        return self._rotatingfilelogger

    @rotatingfilelogger.setter
    def rotatingfilelogger(self, value):
        self._rotatingfilelogger = value

    def confFilePath(self, path=None):
        """
        这里定义了log日志存放的目录
        :param path: log日志存放的路径 如果没有 就默认当前目录的logs文件夹 
        :return: 
        """
        if path is None or path == '':
            # 如果没有指定文件路径
            self.logfiledir = "./logs"
            if not os.path.exists(self.logfiledir):
                os.makedirs(self.logfiledir)
        else:
            try:
                if not os.path.exists(path):
                    os.makedirs(path)
                self.logfiledir = path
            except Exception as e:
                raise e

    @staticmethod
    def formatter():
        # fmt = "%(asctime)s %(levelname)s {%(message)s} %(pathname)s:%(funcName)s:%(lineno)s:%(module)s %(name)s %(processName)s:%(process)d %(threadName)s:%(thread)d"
        fmt = "[%(asctime)s %(levelname)s/%(processName)s:%(process)d/%(threadName)s:%(thread)d] %(message)s ==> %(pathname)s->%(module)s->%(funcName)s->%(lineno)s %(name)s"
        datefmt = "%a %d %b %Y %H:%M:%S"  # Thu 22 Feb 2018
        datefmt = "%Y-%m-%d %H:%M:%S"  # 2018-02-22
        formatter = logging.Formatter(fmt, datefmt)
        return formatter

    @staticmethod
    def BaseHandler(std, level, filter=None):
        # 错误流的handler warn及其以上
        streamerrhandler = logging.StreamHandler(std)
        if filter != None:
            # 添加过滤器
            streamerrhandler.addFilter(filter)
        # 获取输出格式
        streamerrhandler.setFormatter(MLogger.formatter())
        # 设置级别
        streamerrhandler.setLevel(level)
        return streamerrhandler

    @staticmethod
    def BaseFileHandler(level, filename, filter=None, encoding='utf-8'):
        fileHandler = logging.FileHandler(filename, encoding=encoding)
        if filter != None:
            fileHandler.addFilter(filter)
        fileHandler.setFormatter(MLogger.formatter())
        fileHandler.setLevel(level)
        return fileHandler

    # 错误流会输出WARN及以上的级别
    @staticmethod
    def streamErrHandlers():
        return MLogger.BaseHandler(sys.stderr, logging.WARN)

    @staticmethod
    def streamHandlers():
        return MLogger.BaseHandler(sys.stdout, logging.DEBUG)

    # 输出流只会输出INFO 和 DEBUG 两个级别的数据
    # https://yinzo.github.io/14610807170718.html 小坑
    @staticmethod
    def streamOutHandler():
        filter_stdout = LogLevelFilter(levels=[logging.INFO, logging.DEBUG])
        return MLogger.BaseHandler(sys.stdout, logging.DEBUG, filter_stdout)

    # 文件流会将所有级别的日志写入mylog.log这个文件
    @staticmethod
    def fileHandler(filepath):
        log_file_path = path.join(filepath, time.strftime('%Y%m%d', time.localtime(time.time())) + ".log")
        return MLogger.BaseFileHandler(logging.DEBUG, log_file_path)

    @staticmethod
    def timeRotatingFileHandler(filepath, filter=None):
        suffix = ""
        if filter != None:
            suffix = filter.logname
        log_file_path = path.join(filepath, time.strftime('%Y%m%d', time.localtime(time.time())) + suffix + ".log")
        hander = TimedRotatingFileHandler(log_file_path, when="D", interval=1, backupCount=30)
        if filter != None:
            # 添加过滤器
            hander.addFilter(filter)
        hander.setFormatter(MLogger.formatter())
        hander.setLevel(logging.DEBUG)
        return hander

    @staticmethod
    def RotatingFileHandler(filepath, filter=None, maxBytes=1024 * 1024 * 1024, backupCount=10):
        suffix = ""
        if filter != None:
            suffix = filter.logname
        log_file_path = path.join(filepath, time.strftime('%Y%m%d', time.localtime(time.time())) + suffix + ".log")
        hander = RotatingFileHandler(log_file_path, maxBytes=maxBytes, backupCount=backupCount)
        if filter != None:
            # 添加过滤器
            hander.addFilter(filter)
        hander.setFormatter(MLogger.formatter())
        hander.setLevel(logging.DEBUG)
        return hander

    """
    下面这些只会将对应级别的日志写入对应的文件
    """

    @staticmethod
    def fileDebugHandler(filepath):
        log_file_path = path.join(filepath,
                                  "mydebuglog_" + time.strftime('%Y%m%d', time.localtime(time.time())) + ".log")
        filter_debug = LogLevelFilter(level=logging.DEBUG)
        return MLogger.BaseFileHandler(logging.DEBUG, log_file_path, filter_debug)

    @staticmethod
    def fileInfoHandler(filepath):
        log_file_path = path.join(filepath,
                                  "myinfolog_" + time.strftime('%Y%m%d', time.localtime(time.time())) + ".log")
        filter_info = LogLevelFilter(level=logging.INFO)

        return MLogger.BaseFileHandler(logging.DEBUG, log_file_path, filter_info)

    @staticmethod
    def fileWarnHandler(filepath):
        log_file_path = path.join(filepath,
                                  "mywarnlog_" + time.strftime('%Y%m%d', time.localtime(time.time())) + ".log")
        filter_warn = LogLevelFilter(level=logging.WARN)

        return MLogger.BaseFileHandler(logging.DEBUG, log_file_path, filter_warn)

    @staticmethod
    def fileErrorHandler(filepath):
        log_file_path = path.join(filepath,
                                  "myerrorlog_" + time.strftime('%Y%m%d', time.localtime(time.time())) + ".log")
        filter_error = LogLevelFilter(level=logging.ERROR)

        return MLogger.BaseFileHandler(logging.DEBUG, log_file_path, filter_error)

    @staticmethod
    def fileExceptionHandler(filepath):
        log_file_path = path.join(filepath,
                                  "myexceptionlog_" + time.strftime('%Y%m%d', time.localtime(time.time())) + ".log")
        filter_exception = LogLevelFilter(level=logging.ERROR)  # 会返回错误堆栈

        return MLogger.BaseFileHandler(logging.DEBUG, log_file_path, filter_exception)

    @staticmethod
    def fileCriticalHandler(filepath):
        log_file_path = path.join(filepath,
                                  "mycriticallog_" + time.strftime('%Y%m%d', time.localtime(time.time())) + ".log")
        filter_critical = LogLevelFilter(level=logging.CRITICAL)
        return MLogger.BaseFileHandler(logging.DEBUG, log_file_path, filter_critical)

    """
    下面是各种各样的logger 用于不同的输出
    比如你用errlogger就会只打印错误的logger 而不会打印输出信息的logger且不会写入文件 
    我们可以自由组合我们的logger方便使用，只要定义出不同组合的logger就行了，我现在一般使用allloger
    记录下所有的信息
    """

    @staticmethod
    def streamErrLogger(level=logging.DEBUG):
        # 获取logger对象
        logger = logging.getLogger("streamErrLogger")
        # 设置logger获取的级别
        logger.setLevel(level)
        logger.handlers = []
        # 为logger添加handler
        logger.addHandler(MLogger.streamErrHandlers())
        return logger

    @staticmethod
    def streamOutLogger(level=logging.DEBUG):
        logger = logging.getLogger("streamOutLogger")
        logger.setLevel(level)
        logger.handlers = []
        logger.addHandler(MLogger.streamOutHandler())
        return logger

    @staticmethod
    def allLogger(filepath,level=logging.DEBUG):
        # 获取all代表不管输出和文件都会有流产生
        logger = logging.getLogger("all")
        logger.setLevel(level)
        logger.handlers = []
        # http://www.aiuxian.com/article/p-483639.html
        logger.addHandler(MLogger.streamOutHandler())  # 输出流
        logger.addHandler(MLogger.streamErrHandlers())  # 错误流
        # 这是所有的日志都会输出到这个文件
        logger.addHandler(MLogger.fileHandler(filepath))
        # 下面是各个级别的日志流都会输入到对应的文件中
        logger.addHandler(MLogger.fileDebugHandler(filepath))
        logger.addHandler(MLogger.fileInfoHandler(filepath))
        logger.addHandler(MLogger.fileWarnHandler(filepath))
        logger.addHandler(MLogger.fileErrorHandler(filepath))
        logger.addHandler(MLogger.fileExceptionHandler(filepath))
        logger.addHandler(MLogger.fileCriticalHandler(filepath))
        return logger

    @staticmethod
    def multifile_logger(filepath,level=logging.DEBUG):
        # 获取all代表不管输出和文件都会有流产生
        logger = logging.getLogger("multifile")
        logger.setLevel(level)
        logger.handlers = []
        # 下面是各个级别的日志流都会输入到对应的文件中
        logger.addHandler(MLogger.fileDebugHandler(filepath))
        logger.addHandler(MLogger.fileInfoHandler(filepath))
        logger.addHandler(MLogger.fileWarnHandler(filepath))
        logger.addHandler(MLogger.fileErrorHandler(filepath))
        logger.addHandler(MLogger.fileExceptionHandler(filepath))
        logger.addHandler(MLogger.fileCriticalHandler(filepath))
        return logger

    @staticmethod
    def fileLogger(filepath,level=logging.DEBUG):
        # 获取all代表不管输出和文件都会有流产生
        logger = logging.getLogger("file")
        logger.setLevel(level)
        # 防止多次写入
        logger.handlers = []
        # http://www.aiuxian.com/article/p-483639.html
        logger.addHandler(MLogger.streamOutHandler())  # 输出流
        logger.addHandler(MLogger.streamErrHandlers())  # 错误流
        # 这是所有的日志都会输出到这个文件
        logger.addHandler(MLogger.fileHandler(filepath))
        return logger

    @staticmethod
    def timeRotatingFileLogger(filepath, fileter,level=logging.DEBUG):
        # 获取all代表不管输出和文件都会有流产生
        logger = logging.getLogger("timerotatingfile")
        logger.setLevel(level)
        # 防止多次写入
        logger.handlers = []
        # http://www.aiuxian.com/article/p-483639.html
        logger.addHandler(MLogger.streamOutHandler())  # 输出流
        logger.addHandler(MLogger.streamErrHandlers())  # 错误流
        if fileter:
            logger.addHandler(MLogger.timeRotatingFileHandler(filepath, fileter))
        # 这是所有的日志都会输出到这个文件
        logger.addHandler(MLogger.timeRotatingFileHandler(filepath))
        return logger

    @staticmethod
    def RotatingFileLogger(filepath, fileter, maxBytes=1024 * 1024 * 1024, backupCount=10,level=logging.DEBUG):
        # 获取all代表不管输出和文件都会有流产生
        logger = logging.getLogger("rotatingfile")
        logger.setLevel(level)
        # 防止多次写入
        logger.handlers = []
        # http://www.aiuxian.com/article/p-483639.html
        logger.addHandler(MLogger.streamOutHandler())  # 输出流
        logger.addHandler(MLogger.streamErrHandlers())  # 错误流
        if fileter:
            logger.addHandler(
                MLogger.RotatingFileHandler(filepath, fileter, maxBytes=maxBytes, backupCount=backupCount))
        # 这是所有的日志都会输出到这个文件
        logger.addHandler(MLogger.RotatingFileHandler(filepath, maxBytes=maxBytes, backupCount=backupCount))
        return logger

    def streamLogger(self,level=logging.DEBUG):
        # 全局对象个数有getLogger的参数决定
        logger = logging.getLogger("streamLogger")
        logger.setLevel(level)
        # 防止多次打印
        logger.handlers = []
        logger.addHandler(MLogger.streamHandlers())
        return logger

# def main():
#
#     # 使用教程
#     log_file_path = path.join(path.dirname(path.abspath(__file__)), 'logs')
#     logger = MLogger(log_file_path).streamlogger
#     logger.debug('debug message')
#     logger.info('info message')
#     logger.warning('warn message')
#     logger.error('error message')
#     logger.exception('exception message')
#     logger.critical('critical message')
#
# main()
