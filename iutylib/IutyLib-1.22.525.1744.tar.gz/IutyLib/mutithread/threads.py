from threading import Thread
import time

class LoopThread(Thread):
    '''
    construct a Thread 4 cycle task,handle must a void input method
    the proxy is a basic func,so it has no log
    args 4 func and finish
    kwargs 4 notice
    '''
    def __init__(self,targetfunc,interval = 0.01,notice = None,args = ()):
        Thread.__init__(self)
        self._interval = interval
        self._onTask = targetfunc
        self._notice = notice
        self._args = args
        self._running = False
        
        pass
    
    def threadfunc(self):
        if self._onTask != None:
            interval = self._onTask.__call__(*self._args)
            if type(interval) == float:
                self._interval = interval
        pass
    
    def stop(self):
        self._running = False
        
    def run(self):
        self._running = True
        while self._running:
            rst = self.threadfunc()
            if rst:
                self._running = False
            time.sleep(self._interval)
        self.onFin()
    
    def onFin(self):
        if not self._notice == None:
            self._notice.__call__(*self._args)
        pass
    
    def onNotice(self,**kwargs):
        if not self._notice == None:
            self._notice.__call__(**kwargs)
        pass
    
class SubThread(Thread):
    def __init__(self,targetfunc,notice = None,args = ()):
        Thread.__init__(self)
        self._notice = notice
        self._args = args
        self._onTask = targetfunc
        
        #self.start()
        pass
    
    def threadfunc(self):
        if self._onTask != None:
            self._onTask.__call__(*self._args)
            
        pass
    
        
    def run(self):
        self.threadfunc()
    
    def onFin(self):
        if not self._notice == None:
            self._notice.__call__(*self._args)
    
    def onNotice(self,**kwargs):
        if not self._notice == None:
            self._notice.__call__(**kwargs)
        pass