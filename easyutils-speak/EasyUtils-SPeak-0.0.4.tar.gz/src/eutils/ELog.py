'''
Author: SPeak Shen
Date: 2022-02-25 21:32:14
LastEditTime: 2022-05-04 19:54:35
LastEditors: SPeak
Description: a base log system...
FilePath: /EasyUtils/src/eutils/ELog.py
trying to hard.....
'''
import _thread
import os
import time
from queue import Queue
import threading
import sys


class LogBase(object):
    _mOutputFile = None
    _mOutputConsole = None

    """ error < warning < debug < info"""
    _mLogLevelMap = None
    _mLogLevel = None

    __id = ""

    def __init__(self, id=""):

        self._mLogLevelMap = {"error": 0, "warn": 1, "debug": 2, "info": 3}
        self._mLogLevel = self._mLogLevelMap["warn"]
        self.__id = id

        self.config(console=True)

    def info(self, message):

        if self._mLogLevel >= self._mLogLevelMap["info"]:
            message = "[info]: " + str(message)

            self._print(message)

    def debug(self, message):

        if self._mLogLevel >= self._mLogLevelMap["debug"]:
            message = "[debug]: " + str(message)

            self._print(message)

    def warn(self, message):

        if self._mLogLevel >= self._mLogLevelMap["warn"]:
            message = "[warn]: " + str(message)

            self._print(message)

    def error(self, message):

        if self._mLogLevel >= self._mLogLevelMap["error"]:
            message = "[error]: " + str(message)

            self._print(message)

    def _print(self, message):

        raise Exception("method no implement...")

    def _formatLogMessage(self, message):
        timeInfo = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        parentPocessID = os.getppid()
        processID = os.getpid()
        threadID = threading.current_thread().ident

        return f"%s %d %d %d <%s> {message} " % (timeInfo, parentPocessID, processID, threadID, self.__id)

    def config(self, console=None, logFile=None, logLevel=None):

        if console != None:
            self._mOutputConsole = console

        if logFile != None:
            self.__configLogFile(logFile)

        if logLevel != None:
            self.__configLogLevel(logLevel)

    def __configLogFile(self, logFile):

        try:
            self._mOutputFile = open(logFile, 'a+')

        except Exception as e:

            raise Exception("open file %s failed [%s]" % (logFile, str(e)))


    def __configLogLevel(self, logLevel):

        self._mLogLevel = logLevel


class ELog(LogBase, threading.Thread):

    __mInputQueue = None
    __mOutputQueue = None

    qLock = threading.Lock()

    def __init__(self, id=""):
        threading.Thread.__init__(self)
        LogBase.__init__(self, id)

        self.__mInputQueue = Queue()
        self.__mOutputQueue = Queue()


    def run(self):
        while True:
            time.sleep(1)
            self.tryFlush()

    def _print(self, message):

        message = self._formatLogMessage(message)
        self.__put2MQ(message)

    def tryFlush(self):

        while not self.__mOutputQueue.empty():

            logInfo = self.__mOutputQueue.get()

            if self._mOutputConsole:
                print(logInfo)

            if self._mOutputFile is not None:

                try:

                    self._mOutputFile.write(logInfo + "\n")

                except Exception as e:

                    raise Exception("write log to file failed [%s]" % str(e))
                

        if self._mOutputFile is not None:
            self._mOutputFile.flush()

        self.__exchangeMQ()

    def __put2MQ(self, message):
        # todo thead lock? Queue is a data struct of thread safe
        # print("input <-- " + message)
        self.__mInputQueue.put(message)

    def __exchangeMQ(self):
        # self.qLock.acquire()
        # print(self.__mInputQueue, self.__mOutputQueue)
        self.__mInputQueue, self.__mOutputQueue = self.__mOutputQueue, self.__mInputQueue
        # print(self.__mInputQueue, self.__mOutputQueue)
        # self.qLock.release()


def getLogger(logID="", console=True, logLevel=1, autoCreateLogFile=False):

    log = ELog(logID)

    log.config(logLevel=logLevel)

    log.config(console)

    if autoCreateLogFile:
        timeInfo = time.strftime("%Y-%m-%d", time.localtime())
        defaultLogFile = os.getcwd() + "/eutils-" + timeInfo + "_" + ".elog.log"
        self.config(logFile=defaultLogFile)

    log.info("logger [%s] init done." % logID)

    log.start()

    return log

""" ----------------------------------------- Test Code ----------------------------------------- """

"""

sys._getframe().f_code.co_filename  #当前文件名
sys._getframe(0).f_code.co_name     #当前函数名
sys._getframe().f_lineno            #当前行号

"""

"""
def printLog(level, logger=None):

    if logger is None:
        logger = __ETMLogger

    info = "%s %s" % (sys._getframe().f_code.co_filename, sys._getframe(0).f_code.co_name)

    print(info)

    for i in range(0, 10):

        message = info + "hello world " + str(i)

        if level == 0:
            logger.info(message)
        elif level == 1:
            logger.debug(message)
        elif level == 2:
            logger.warn(message)
        else:
            logger.error(message)

        time.sleep(1)


if __name__ == "__main__":

    myLogger = getLogger()

    lFile= os.getcwd() + "/eu_test.log"

    print(lFile)

    myLogger.config(logFile=lFile)

    myLogger.info("test")

    _thread.start_new_thread(printLog, (0, myLogger))
    _thread.start_new_thread(printLog, (1, myLogger))
    _thread.start_new_thread(printLog, (2, myLogger))
    _thread.start_new_thread(printLog, (3, myLogger))

    time.sleep(10)
"""