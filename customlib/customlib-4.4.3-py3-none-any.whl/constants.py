# -*- coding: UTF-8 -*-

from collections import namedtuple
from enum import IntFlag
from msvcrt import LK_UNLCK
from os.path import dirname, join
from sys import modules
from threading import RLock, Lock
from weakref import WeakValueDictionary

RECURSIVE_THREAD_LOCK = RLock()
THREAD_LOCK = Lock()
INSTANCES = WeakValueDictionary()

FRAME = namedtuple("FRAME", ["file", "line", "code"])
TRACEBACK = namedtuple("TRACEBACK", ["file", "line", "code", "message"])
ROW = namedtuple("ROW", ["time", "level", "file", "line", "code", "message"])

# root directory
DIRECTORY: str = dirname(modules["__main__"].__file__)

# default config file
CONFIG: str = join(DIRECTORY, "config", "config.ini")

# config default section
DEFAULTS: dict = {
    "directory": DIRECTORY,
}

# backup configuration
BACKUP: dict = {
    "FOLDERS": {
        "logger": r"${DEFAULT:directory}\logs"
    },
    "LOGGER": {
        "name": "customlib.log",
        "handler": "file",  # or "console"
        "debug": False,
    },
}


class LOCK(IntFlag):
    EX = 0x1       # exclusive lock
    SH = 0x2       # shared lock
    NB = 0x4       # non-blocking
    UN = LK_UNLCK  # unlock


class ES:
    CONTINUOUS = 0x80000000
    SYSTEM_REQUIRED = 0x00000001
    DISPLAY_REQUIRED = 0x00000002
