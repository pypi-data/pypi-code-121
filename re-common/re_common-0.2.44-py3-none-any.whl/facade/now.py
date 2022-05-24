# 这个库会加载所有的模块，也可以知道本基础库使用了哪些模块
from re_common.baselibrary.utils.baserequest import BaseRequest

from .loggerfacade import MLogger

__all__ = ['get_streamlogger', 'get_filelogger', 'get_timerotatingfilelogger', 'BaseRequest']

"""
提供logger的使用外观  外观模式
"""


def get_streamlogger():
    """
    提供一个输出流的logger
    :return:
    """
    return MLogger().streamlogger


def get_filelogger(filedir):
    """
    文件流的logger
    :param filedir:
    :return:
    """
    return MLogger(filedir).filelogger


def get_timerotatingfilelogger(filedir, fileter=None):
    return MLogger(filedir, fileter).timerotatingfilelogger
