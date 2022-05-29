import queue
import copy
from multiprocessing import Process,Lock
from TDhelper.Event.Event import Event
class pools(Event):
    def __init__(self, maxSize=100):
        '''
            初始化

            - 参数:
                obj: 装入队列的对象, 一个定义好的对象.初始化程序会自动拷贝对象填满队列.
                maxSize: 队列长度
        '''
        super(pools, self).__init__()
        # 可用资源
        self.available_resources= 0
        self.size= maxSize
        self._list= queue.Queue(maxSize)
        self._lock=Lock()

    def push(self,value):
        try:
            self._lock.acquire()
            if not self._list.full():
                self.available_resources+= 1
                self._list.put(value)
        finally:
            self._lock.release()

    def pop(self):
        try:
            self._lock.acquire()
            if not self._list.empty():
                self.available_resources-= 1
                return self._list.get()
        finally:
            self._lock.release()

    def getQSize(self):
        return self._list.qsize()
        