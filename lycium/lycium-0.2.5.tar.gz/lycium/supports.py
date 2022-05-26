#!/usr/bin/env python
# -*- coding: utf-8 -*-

# decorator of sigleton
def singleton(clsname):
    instances = {}
    def getinstance(*args,**kwargs):
        if clsname not in instances:
            instances[clsname] = clsname(*args,**kwargs)
        return instances[clsname]
    return getinstance

class Constant(object):
    class ConstError(TypeError) : pass
    
    def __setattr__(self, key, value):
        if hasattr(self, key):
            raise self.ConstError("Can't rebind const (%s)" % key)
        setattr(self, key, value)
