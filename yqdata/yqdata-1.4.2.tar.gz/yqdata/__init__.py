# -*- coding: UTF-8 -*-

import pkgutil

__version__ = '1.0.0'
__author__ = 'Hu Min'

def get_version():
    return __version__

def init():
    import importlib
    for loader, module_name, is_pkg in pkgutil.walk_packages(path=__path__, prefix='yqdata.'):
        try:
            importlib.import_module(module_name)
        except ImportError:
            print("can not find mod [{}], ignored".format(module_name))
            continue
init()