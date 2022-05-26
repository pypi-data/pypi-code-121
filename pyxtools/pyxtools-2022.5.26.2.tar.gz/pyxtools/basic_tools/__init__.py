# -*- coding:utf-8 -*-
from __future__ import absolute_import

import logging
import os
import shutil
import subprocess
import time
from decimal import getcontext, Decimal
from urllib.request import urlopen


def set_time_zone(tz: str = "Asia/Shanghai"):
    os.environ['TZ'] = tz
    time.tzset()


def set_proxy(http_proxy="http://127.0.0.1:8118"):
    """ 设置代理 """
    os.environ["https_proxy"] = http_proxy
    os.environ["HTTPS_PROXY"] = http_proxy
    os.environ["http_proxy"] = http_proxy
    os.environ["HTTP_PROXY"] = http_proxy


def clear_proxy_setting():
    """ 取消全局代理设置 """
    proxy_keys = {"HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY"}
    for key in proxy_keys:
        if key in os.environ:
            del os.environ[key]
        _key = key.lower()
        if _key in os.environ:
            del os.environ[_key]


def download_big_file(url, target_file_name):
    """
        使用python核心库下载大文件
        ref: https://stackoverflow.com/questions/1517616/stream-large-binary-files-with-urllib2-to-file
    """
    response = urlopen(url)
    chunk = 16 * 1024
    with open(target_file_name, 'wb') as f:
        while True:
            chunk = response.read(chunk)
            if not chunk:
                break
            f.write(chunk)


def download_big_file_with_wget(url, target_file_name):
    """
        使用wget下载大文件
        Note: 需要系统安装wget
    """

    download_process = subprocess.Popen(["wget", "-c", "-O", target_file_name, "'{}'".format(url)])

    download_process.wait()

    if not os.path.exists(target_file_name):
        raise Exception("fail to download file from {}".format(url))


def remove_path_or_file(path_or_file_name):
    """
        删除文件
    """
    if not os.path.exists(path_or_file_name):
        logging.warning("{} not exists!".format(path_or_file_name))
        return

    if os.path.isdir(path_or_file_name):
        # dir
        shutil.rmtree(path_or_file_name)
    else:
        # file
        os.remove(path_or_file_name)


def get_pretty_float(num: float, count: int = 2) -> str:
    """
        指定有效数字的科学计数法显示
    Args:
        num: float
        count: int
    """
    getcontext().prec = count
    return (Decimal(num) / Decimal(1)).to_eng_string()
