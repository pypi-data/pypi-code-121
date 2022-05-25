import datetime

from enum import Enum
from threading import Condition
from queue import Queue
from TDhelper.Event.Event import Event
from TDhelper.Spider.models.Cache_L2 import L2, RecordStatus

thread_condition = Condition()


class L1(Event):
    def __init__(self, size=10):
        super(L1, self).__init__()
        self._L1_Size = size
        self._L1 = Queue(size)
        self._L2= L2()

    def push(self, value, key, source_url=None):
        try:
            thread_condition.acquire()
            if not self._L1.full():
                self._L1.put([value, source_url, key])
                self.on(event.onPush, self)
            else:
                # L1缓存数据存满了，将数据缓存到L2
                self._L2.URL = value
                self._L2.Source = source_url
                self._L2.status = RecordStatus.WAIT.value
                self._L2.Key= key
                self._L2.updatetime= datetime.datetime.now()
                self._L2.toSave()
                self._L2.clear()
        finally:
            thread_condition.release()

    def pop(self):
        try:
            thread_condition.acquire()
            if self._L1.empty():
                # L1缓存数据读取完毕，从L2缓存读取数据
                if not self._getL2cache(size= self._L1_Size):
                    return None
            return self._L1.get()
        finally:
            thread_condition.release()

    def _getL2cache(self, size=1, type= 0):
         # L1缓存数据读取完毕，从L2缓存读取数据
        m_records = self._L2.find(**{'limit': size})
        if m_records.count() > 0:
            for item in m_records:
                if type==0:
                    self.push(item['url'], item['key'], item['source'])
                else:
                    self._L1.put([item['url'], item['source'], item['key']])
                self._L2.model = item
                self._L2.deleteById()
                self._L2.clear()
            return True
        else:
            return False

    def getCache(self):
        '''
            不会触发push事件，仅返回cache本身.取出后会从缓存删除
        '''
        try:
            thread_condition.acquire()
            if self._L1.empty():
                # L1缓存数据读取完毕，从L2缓存读取数据
                if not self._getL2cache(type= 1):
                    return None
            return self._L1.get()
        finally:
            thread_condition.release()


    def getSize(self):
        return self.L1.qsize()


class event(Enum):
    onPush = 'onPush'
    onPop = 'onPop'
