import time

class FuncTime(object):
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        t1 = time.time()
        res = self.func(*args, **kwargs)
        t2 = time.time()
        print("函数执行时长:"+ str(t2 - t1))