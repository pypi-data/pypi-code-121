# -*- coding:utf-8 -*-
"""
@Author: Mas0n
@File: __init__.py.py
@Time: 2022/5/27 22:12
@Desc: It's all about getting better.
"""
from loguru import logger
import sys

logger.remove()
logger.add(sink=sys.stdout, format="<g>{time:YYYY-MM-DD HH:mm:ss.SSS}</g> <lr>|</lr> <level>{level.name:<8}</level> <lr>|</lr> <c><{file}:{line}></c> {level.icon:^10} <level>{message}</level>", colorize=True)

logger.level("TRACE", icon="🦉")
logger.level("SUCCESS", icon="🐉")
logger.level("DEBUG", icon="🔧")
logger.level("INFO", icon="😋")
logger.level("ERROR", icon="❌")
logger.level("WARNING", icon="⛔")
logger.level("CRITICAL", icon="🐛")


def set_icon(name, icon):
    """
    set level logger icon.
    :param name: level name
    :param icon: unicode string.
    :return: Level
    """
    return logger.level(name, icon=icon)
