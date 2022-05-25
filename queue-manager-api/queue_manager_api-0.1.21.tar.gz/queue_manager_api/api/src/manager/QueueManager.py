import time

from python_helper import log, ReflectionHelper

try:
    import ThreadUtil
except:
    from queue_manager_api.api.src.util import ThreadUtil


DEFAULT_TIMEOUT = 20


def handleNotRunningThreadDictionary(threadDictionary, threadTimeout=DEFAULT_TIMEOUT):
    while not threadDictionary.isRunning() and not threadDictionary.shouldStopRunning():
        time.sleep(0.01)
    while threadDictionary.isRunning() and not threadDictionary.shouldStopRunning():
        for k in [*threadDictionary.keys()]:
            threadDictionary.get(k).runItIfItsNotRunningYet(threadTimeout=threadTimeout)
            if not threadDictionary.get(k).isAlive():
                threadDictionary.pop(k).kill()
                log.debug(handleNotRunningThreadDictionary, f'The {k}th tread is finished')
        time.sleep(0.01)
    for k in [*threadDictionary.keys()]:
        threadDictionary.pop(k).kill()
    log.debug(handleNotRunningThreadDictionary, f'Thread dictionary finished running')


class ThreadDictionary(dict):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.running = False
        self.shouldStop = False
        log.debug(self.__init__, f'{ReflectionHelper.getName(ThreadDictionary)} created')


    def run(self):
        self.running = True
        self.shouldStop = False


    def isRunning(self):
        return self.running and not self.shouldStop


    def shouldStopRunning(self):
        return True and self.shouldStop


    def kill(self):
        self.shouldStop = True
        self.running = False




class QueueManager:

    def __init__(self, threadTimeout=DEFAULT_TIMEOUT):
        self.threadDictionary = ThreadDictionary()
        self.timeout = threadTimeout
        self.threadDictionaryHandler = ThreadUtil.ApplicationThread(
            handleNotRunningThreadDictionary,
            self.threadDictionary,
            threadTimeout = self.timeout
        )
        log.debug(self.__init__, f'{ReflectionHelper.getName(QueueManager)} created')


    def new(self, target, *args, **kwargs):
        return ThreadUtil.ApplicationThread(target, *args, **kwargs)


    def runInAThread(self, target, *args, **kwargs):
        thread = self.new(target, *args, threadTimeout=self.timeout, **kwargs)
        self.threadDictionary[len(self.threadDictionary)] = thread


    def addResource(self, api, app):
        api.queueManager = self
        self.api = api


    def onHttpRequestCompletion(self, api, app):
        ...


    def onRun(self, api, app):
        ...


    def initialize(self, api, app):
        self.threadDictionaryHandler.run()
        self.threadDictionary.run()
        log.success(self.initialize, f'{ReflectionHelper.getClassName(self)} is running')


    def onShutdown(self, api, app):
        self.threadDictionary.kill()
        self.threadDictionaryHandler.kill()
        log.success(self.onShutdown, f'{ReflectionHelper.getClassName(self)} is successfuly closed')
