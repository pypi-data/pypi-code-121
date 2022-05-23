# -*- coding: utf-8 -*-
import logging
import os

LOG_FILE = "pcs-get.log"

__logger = None


def d(msg):
    __logger.debug(msg)


def i(msg):
    __logger.info(msg)


def w(msg):
    __logger.warning(msg)


def e(msg):
    __logger.error(msg)


def init(debug):
    global __logger
    # 创建实例
    __logger = logging.getLogger(__file__)
    __logger.setLevel(logging.DEBUG)
    # 文件日志
    log_fp = os.path.join(os.path.expanduser("~"), LOG_FILE)
    fh = logging.FileHandler(log_fp)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    # CMD窗口日志
    ch = logging.StreamHandler()
    if debug:
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    else:
        ch.setLevel(logging.INFO)
        ch.setFormatter(logging.Formatter("%(message)s"))
    # 注册handler到logger
    __logger.addHandler(ch)
    __logger.addHandler(fh)
