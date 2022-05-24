"""
提供logger的使用外观  外观模式
"""
from re_common.baselibrary import MLogger


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
