#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
"""

"""

import os

__all__ = ['Constants']

class Constants():
    SERVER_PORT = 60609
    SERVER_HOST = 'localhost'
    MAX_TASK_PROCESS = 2
    MAX_SUB_TASK_PROCESS = 8


ENV_DOWNLOAD_DIR: str = os.path.expanduser(os.getenv("DLER_DOWNLOAD_DIR", ''))

DOWNLOAD_DIR: str = os.path.expanduser('~/Downloads')
CACHE_DIR: str = os.path.join(DOWNLOAD_DIR, '.dler')
DB_PATH: str = os.path.expanduser('~/dler.db?check_same_thread=false')
SEGMENT_SIZE: int = 1024 * 1024 * 16
