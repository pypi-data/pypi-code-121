from functools import partial
import time

class semistaticmethod(object):
    def __init__(self, callable):
        self.f = callable
    def __get__(self, obj, type=None):
        if (obj is None) and (type is not None):
            return partial(self.f, type)
        if (obj is not None):
            return partial(self.f, obj)
        return self.f
    @property
    def __func__(self):
        return self.f
    
def cls_method_timer(func):
    def wrapper(self, *args, **kwargs):
        t1 = time.time()
        result = func(self, *args, **kwargs)
        t2 = time.time()
        method_name = f"{type(self).__name__}::{func.__name__}"
        self.stdout.info(f'INFO: Task {method_name!r} executed in {(t2-t1):.4f}s')
        return result
    return wrapper 

class Timer:    
    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.end = time.time()
        self.interval = self.end - self.start