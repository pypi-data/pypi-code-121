import functools
import time

#类函数装饰器
def class_method_decorator(func):

    @functools.wraps(func)
    def wrapper(me_instance, *args, **kwargs):
        start = time.time()
        rv = func(me_instance, *args, **kwargs)
        print(f"{time.time() - start}")
        return rv

    return wrapper

#类装饰器
class class_decorator(object):

    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        print(f"{self.func.__name__} start")
        rv = self.func()
        print(f"{self.func.__name__} end")
        return rv

def cost_time(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        rv = func(*args, **kwargs)
        print(f"{time.time() - start}")
        return rv

    return wrapper

'''
#缓存

from functools import lru_cache
@lru_cache
def readFile(filename:str):
	return open(filename)

'''

'''
重载
from functools import singledispatch

@singledispatch
def show(obj):
    print (obj, type(obj), "obj")

@show.register(str)
def show_str(text):
    print (text, type(text), "str")

@show.register(int)
def show_int(n):
    print (n, type(n), "int")

'''
