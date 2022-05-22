from multiprocessing import Process, Lock
from threading import Thread
from array import array
import queue
import copy
import time

def PoolsFunc(func):
    def wapper(*args:tuple, **kwargs):
        try:
            thread_pools= None
            thread_index= None
            if len(args) >= 2:
                thread_pools = args[0]
                thread_index = args[1]
            else:
                raise Exception('params error.')
            kwargs['handle']= thread_pools
            kwargs['thread-id']= thread_index
            if not isinstance(args[2],list):
                raise Exception("params args must is <list>. you given an <%s>." % type(args[2]).__name__)
            m_args=args[2]
            while thread_pools._processFlag:
                if not m_args:
                    break
                ret= func(*m_args, **kwargs)
                m_args= thread_pools.popArgs()
            thread_pools.threadComplete(thread_index)
            return ret
        except Exception as e:
            raise Exception(e)
    return wapper

class threadPools:
    def __init__(self, threadfunc, daemon=False, isJoin=False, maxSize=10):
        self.Daemon = daemon
        self.isJoin = isJoin 
        self._processFlag = True # 方法状态
        self.processLock= Lock() # 方法事务锁
        self._threadLockArgs = Lock() # 任务队列锁
        self._threadLockThreadFunc = Lock() # 线程队列锁
        self._activeThread = {} # 活跃线程
        self._list = queue.Queue(maxSize) # 线程队列
        self._args = [] # 任务队列
        for offset in range(0, maxSize):
            self._list.put((offset, threadfunc))

    def stop(self, waitProcessComplate= True):
        '''
            停止线程
            - params:
            -   waiProcessComplate: <boolen>, 是否等待线程任务结束, 默认值：True
        '''
        if not waitProcessComplate:
            self._processFlag = False
        else:
            while True:
                if self.getArgsLength()==0:
                    self._processFlag= False
                    break
                time.sleep(0.5)

    def restart(self):
        '''
            重启线程,未关闭的情况下
        '''
        self._processFlag = True

    def pushArgs(self, param: any):
        '''
            push线程任务队列.
            - params:
            -   param: <any>, 任务参数.
        '''
        self._threadLockArgs.acquire()
        self._args.append(param)
        self._threadLockArgs.release()
        self.popThread()

    def popArgs(self):
        '''
            弹出任务
        '''
        value = None
        self._threadLockArgs.acquire()
        if len(self._args) > 0:
            value = self._args[0]
            del self._args[0]
        self._threadLockArgs.release()
        return value

    def getArgsLength(self):
        '''
            获取任务队列长度
        '''
        value = 0
        self._threadLockArgs.acquire()
        value = len(self._args)
        self._threadLockArgs.release()
        return value

    def popThread(self):
        '''
            从线程队列里，弹出一个线程方法.
        '''
        try:
            if not self._list.empty():
                self._threadLockThreadFunc.acquire()
                m_thread = self._list.get()
                self._threadLockThreadFunc.release()
                if m_thread:
                    self._activeThread[m_thread[0]] = m_thread[1]
                    m_args = self.popArgs()
                    if m_args:
                        m_thread = Thread(target=self._activeThread[m_thread[0]], name='Thread%s' % str(
                            m_thread[0]), args=(self, m_thread[0], m_args,))
                        m_thread.setDaemon = self.Daemon
                        m_thread.start()
                        if self.isJoin:
                            m_thread.join()
                    else:
                        self.threadComplete(m_thread[0])
                else:
                    raise Exception('thread func is none.')
        except Exception as e:
            raise e

    def pushThread(self, m_thread: tuple):
        '''
            将一个方法装入线程队列.
        '''
        if not self._list.full():
            self._threadLockThreadFunc.acquire()
            self._list.put(m_thread)
            self._threadLockThreadFunc.release()
            if self.getArgsLength() > 0:
                self.popThread()
        else:
            raise Exception('thread pools is full.')

    def threadComplete(self, offset):
        '''
            线程任务执行完成,将方法重新放入队列
        '''
        m_thread = (offset, self._activeThread.pop(offset))
        self.pushThread(m_thread)



