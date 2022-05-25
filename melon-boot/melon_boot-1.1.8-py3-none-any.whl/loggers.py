# -*- encoding: utf-8 -*-
"""
@Author  : zh_o
"""
import sys
from loguru import logger


logger.remove()
default_format = '<cyan>{time:YYYY:MM:DD HH:mm:ss.SSS}</cyan> ' \
         '<black>[</black><magenta>TID:{thread.id}</magenta><black>]</black> ' \
         '<black>[</black><blue>{level}</blue><black>]</black> ' \
         '<black>{file}</black>' \
         '<black>[</black><blue>{line}</blue><black>]</black>' \
         '<black>:</black> ' \
         '{message}'

logger.add(
    sink=sys.stdout,
    format=default_format
)
