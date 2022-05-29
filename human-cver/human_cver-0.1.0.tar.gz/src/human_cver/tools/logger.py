import logging
import os
import os.path as osp

import cv2
import logzero
from logzero import logger
import platform

# python3.8版本之后才支持 stacklevel
version = platform.python_version()
version = [int(a) for a in version.split(".")]
has_stacklevel = not (version[0] <= 3 and version[1] < 8)


class Logger(object):

    FOLDER = ""

    @staticmethod
    def debug(msg):
        if has_stacklevel:
            logger.debug(msg, stacklevel=2)
        else:
            logger.debug(msg)

    @staticmethod
    def info(msg, data=""):
        if has_stacklevel:
            logger.info(msg + str(data), stacklevel=2)
        else:
            logger.info(msg + str(data))

    @staticmethod
    def warn(msg, data=""):
        if has_stacklevel:
            logger.warning(msg + str(data), stacklevel=2)
        else:
            logger.warning(msg + str(data))

    @staticmethod
    def error(msg):
        if has_stacklevel:
            logger.error(msg, stacklevel=2)
        else:
            logger.error(msg)

    @staticmethod
    def logfile(filename, clear=False):
        """设置日志文件"""
        path = osp.dirname(filename)
        Logger.FOLDER = path
        if not osp.exists(path):
            os.makedirs(path, exist_ok=True)

        if has_stacklevel:
            logger.warning(f"logfile -> {filename}", stacklevel=2)
        else:
            logger.warning(f"logfile -> {filename}")
        if clear and osp.exists(filename):
            os.remove(filename)
        logzero.logfile(filename)

    @staticmethod
    def loglevel(level):
        """设置日志等级: debug, info, warn, error"""
        level = level.upper()
        logzero.loglevel(eval(f"logging.{level}"))

        if has_stacklevel:
            logger.warning(f"loglevel -> {level}", stacklevel=2)
        else:
            logger.warning(f"loglevel -> {level}")

    @staticmethod
    def logimg(filename, img):
        filename = osp.join(Logger.FOLDER, filename)
        cv2.imwrite(filename, img)
        Logger.warn(f"logimg: {filename}")


Logger.loglevel("debug")
