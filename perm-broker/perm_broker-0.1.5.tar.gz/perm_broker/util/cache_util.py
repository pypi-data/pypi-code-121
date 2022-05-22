# coding:utf-8
class DummyLock(object):
    def __init__(self, key, timeout=5):
        pass

    def __enter__(self):
        pass

    def __exit__(self, *p):
        pass

cache_lock = DummyLock
