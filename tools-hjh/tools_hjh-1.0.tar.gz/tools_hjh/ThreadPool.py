# coding:utf-8
import time
import _thread


class ThreadPool():
    """ 维护一个线程池 """
    
    def __init__(self, size):
        self.locks = []
        self.maxsize = size
        
    def clear(self):
        self.locks.clear()

    def run(self, func, args, kwargs={}):
        """ 主线程命令当前线程池从空闲线程中取一个线程执行给入的方法，如果池满，则主线程等待 """
        if len(self.locks) < self.maxsize:
            lock = _thread.allocate_lock()
            lock.acquire()
            self.locks.append(lock)
            args = (*args, lock)
            newfunc = self._getnewfunc(func)
            _thread.start_new_thread(newfunc, args, kwargs)
        else:
            while len(self.locks) >= self.maxsize:
                for lock in self.locks:
                    if not lock.locked():
                        self.locks.remove(lock)
                time.sleep(0.2)
            self.run(func, args, kwargs)

    def wait(self):
        """ 主线程等待，直到线程池不存在活动线程 """
        for lock in self.locks:
            while lock.locked():
                time.sleep(0.2)

    def _getnewfunc(self, func):

        def newfunc(*arg, **kwargs):
            try:
                func(*arg[0:-1], **kwargs)
            finally:
                arg[-1].release()

        return newfunc

