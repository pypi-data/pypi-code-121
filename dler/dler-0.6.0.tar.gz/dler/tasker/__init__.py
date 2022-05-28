#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy@gmail.com

from urllib.parse import urlparse
from .base import BaseTasker
from .m3u8_tasker import M3u8Tasker
from .file_tasker import FileTasker

def conver_tasker(url: str, **kwargs) -> BaseTasker:
    parse = urlparse(url)
    path = parse.path
    Tasker = None
    if path.endswith('.m3u8'):
        Tasker = M3u8Tasker
    else:
        Tasker = FileTasker

    return Tasker(url, **kwargs)
