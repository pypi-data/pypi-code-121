# -*- coding: UTF-8 -*-
import os

import loguru
from loguru._defaults import env

TRACE = "TRACE"
INFO = "INFO"
DEBUG = "DEBUG"
ERROR = "ERROR"
WARNING = "WARNING"
fmt = "[%(thread)d]-[%(levelname)s]-[%(asctime)s}]-[%(process)d]-[%(name)s]-[%(funcName)s]%(lineno)s :%(message)s"

LOGURU_FORMAT = env(
    "LOGURU_FORMAT",
    str,
    "[{process}]-"
    "[<level>{level: <8}</level>]-"
    "[<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>]-"
    "[<cyan>{thread}</cyan>]-"
    "[<cyan>{file}</cyan>]-"
    "[<cyan>{function}</cyan>]<cyan>{line}</cyan> :"
    "<level>{message}</level>",
)
LOGURU_ERROR_FORMAT = env(
    "LOGURU_FORMAT",
    str,
    "[<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{process} | {thread}</cyan> | "
    "<cyan>{file}</cyan>-><cyan>{function}</cyan>:<cyan>{line}</cyan> ]"
    "<level>{message}</level>",
)
_py_info = '''
    * 日志工具
    * 创建 王建国
    * 对象 LOG 入参: file_name 文件名称 不需要带路径和后缀 使用看main方法 ，文件默认路径是当前路径下 ./log/{log_file_name}.log 系统会默认创建log目录
                    format ：日志输出格式 ,{time} 时间 ，{time:YYYY-MM-DD HH:mm:ss.SSS}可以格式化时间 
                                        {exception} 栈 
                                        {extra}
                                        {file} 文件名称
                                        {function} 方法
                                        {level} 日志级别
                                        {line} 行数
                                        {message} 信息
                                        {module} 模块
                                        {name}
                                        {process} 进程id
                                        {thread} 线程id
                    level 日志等级
                    rotation 文件切割方法 时间点 ，例如 '00:00' 表示 0点切割 
                                        文件大小， 例如 '500MB' 表示日志大于500M切割日志文件 
                                        时间间隔 ， 例如 '10s' 表示每10秒切割一次
                    retention 日志保留时间 例如 '3 days' 表示 保留3天的日志
                    compression 日志打包方式 ，一般 zip , gz , tar , tar.gz 压缩
                    enqueue 是否异步打印
'''


class LOG(object):

    # 静态方法 获取日志对象
    @classmethod
    def get_logger(cls, file_name, enqueue=False):
        self = object.__new__(cls)
        self.__init__(file_name, enqueue=enqueue)
        return self.logger

    @classmethod
    def get_logger_init(cls, file_name, format=LOGURU_FORMAT, level=INFO, rotation="00:00", retention="3 days",
                        compression="zip",
                        enqueue=False):
        self = object.__new__(cls)
        self.__init__(file_name, format=format, level=level, rotation=rotation, retention=retention,
                      compression=compression,
                      enqueue=enqueue)
        return self.logger

    def __init__(self, file_name, is_multiprocess_handler=False, format=LOGURU_FORMAT, level=INFO,
                 rotation="00:00", retention="3 days", compression="zip",
                 enqueue=False):
        self.logger = loguru.logger
        # 日志地址配置
        self.file_path = f'log/{file_name}.log'
        # 错误日志地址配置
        self.file_error_path = f'log/{file_name}-error.log'
        if not os.path.exists("./log"):
            os.makedirs("./log/")
        self.logger.add(self.file_path, format=format, level=level, enqueue=enqueue, rotation=rotation,
                        retention=retention,
                        compression=compression)
        # 错误日志默认保存三十天 错误日志格式和保存时间是无法配置的
        self.logger.add(self.file_error_path, format=LOGURU_FORMAT, level=ERROR, enqueue=enqueue,
                        rotation=rotation,
                        retention="30 days",
                        compression=compression)
