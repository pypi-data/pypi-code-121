# -*- coding:utf-8 -*-
from __future__ import unicode_literals

import functools
import threading


class SingletonMixin(object):
    """
    thread safe singleton base class
    refer: https://gist.github.com/werediver/4396488

    # Based on tornado.ioloop.IOLoop.instance() approach.
    # See https://github.com/facebook/tornado
    """
    __singleton_lock = threading.Lock()
    __singleton_instance = None

    @classmethod
    def instance(cls):
        """

        :rtype: SingletonMixin
        """
        if not cls.__singleton_instance:
            with cls.__singleton_lock:
                if not cls.__singleton_instance:
                    cls.__singleton_instance = cls()
        return cls.__singleton_instance


def singleton(func):
    """线程不安全的单例模式"""

    @functools.wraps(func)
    def wrapper(*args, **kw):
        if not hasattr(func, 'attr'):
            func.attr = func(*args, **kw)
        return func.attr

    return wrapper
