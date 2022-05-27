from functools import wraps
from threading import Thread, Lock, Timer
from typing import Callable

# 单例模式
class Singleton(type):
    _instance_lock = Lock()

    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            with Singleton._instance_lock:
                if not hasattr(cls, '_instance'):
                    cls._instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instance


'''
#元类
class SingClass(metaclass=Singleton):
    def __init__(self):
        pass
'''

class SingleInstance(object):
    _instance_lock = Lock()
    _instance = None

    @classmethod
    def instance(cls, *args, **kwargs):
        if not hasattr(SingleInstance, '_instance'):
            with SingleInstance._instance_lock:
                if not hasattr(SingleInstance, '_instance'):
                    SingleInstance._instance = SingleInstance(*args, **kwargs)
        return SingleInstance._instance


def daemon_thread(fn: Callable) -> Callable[..., Thread]:

    @wraps(fn)
    def _wrap(*args, **kwargs) -> Thread:
        return Thread(target=fn, args=args, kwargs=kwargs, daemon=True)

    return _wrap


def function_thread(fn: Callable, daemon: bool, *args, **kwargs):
    return Thread(target=fn, args=args, kwargs=kwargs, daemon=daemon)

'''
 @daemon_thread
    def thread_func():
        pass
'''

class RepeatingTimer(Timer):

    def run(self):
        self.finished.wait(self.interval)
        while not self.finished.is_set():
            self.function(*self.args, **self.kwargs)
            self.finished.wait(self.interval)

class SimpleTimer():

    def __init__(self):
        self.timer = None

    def is_running(self):
        return self.timer and self.timer.is_alive()

    def run(self, interval: int, function: Callable, args=None, kwargs=None):
        if self.is_running():
            if kwargs.get('force', False) is False:
                raise Exception(f"timer is running, please cancel")
            else:
                self.cancel()
        self._run_timer(interval, function, args, kwargs)

    def _run_timer(self, interval: int, function: Callable, args=None, kwargs=None):
        self.timer = Timer(interval, function, args, kwargs)
        self.timer.start()

    def cancel(self):
        if self.is_running():
            self.timer.cancel()
        self.timer = None
