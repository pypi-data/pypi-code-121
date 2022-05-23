# coding=utf-8
from __future__ import absolute_import, print_function

import os
import sys
import functools


def resourcepath(relativepath):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        basepath = sys._MEIPASS
    except Exception:
        basepath = os.path.abspath(".")

    return os.path.join(basepath, relativepath)


def instancemethod(func):
    @functools.wraps(func)
    def _dec(self, *args, **kwargs):  # pylint: disable=unused-argument
        return func(*args, **kwargs)

    return _dec


def bindmethod(instance, func, name=None):
    name = name or func.__name__
    func = func.__get__(instance, instance.__class__)
    setattr(instance, name, func)
    return instance


def bind(instance, func, name=None):
    return bindmethod(instance, instancemethod(func), name=name)


def onlyonce(func):
    setattr(func, "__onlyonce_called__", False)
    setattr(func, "__onlyonce_return__", None)

    @functools.wraps(func)
    def _dec(*args, **kwargs):
        if not getattr(func, "__onlyonce_called__", False):
            setattr(func, "__onlyonce_called__", True)
            setattr(func, "__onlyonce_return__", func(*args, **kwargs))
        return getattr(func, "__onlyonce_return__")

    return _dec


def lazyproperty(func):
    attrname = "_lazy_" + func.__name__

    @property
    def _lazyproperty(self):
        if not hasattr(self, attrname):
            setattr(self, attrname, func(self))
        return getattr(self, attrname)

    return _lazyproperty
