import logging
import time
import os
from logging import handlers

class Logger(object):
    loggers = {}
    level_relations = {
        'debug':logging.DEBUG,
        'info':logging.INFO,
        'warning':logging.WARNING,
        'error':logging.ERROR,
        'crit':logging.CRITICAL
    }#日志级别关系映射

    def __init__(self,level='info', fmt='%(asctime)s - %(levelname)s: %(module)s %(lineno)d %(message)s'):
        self.logger = logging.getLogger()
        format_str = logging.Formatter(fmt)#设置日志格式
        self.logger.setLevel(self.level_relations.get(level))#设置日志级别

        sh = logging.StreamHandler()#往屏幕上输出
        sh.setFormatter(format_str) #设置屏幕上显示的格式
        self.logger.addHandler(sh) #把对象加到logger里

    def set_file_handler(self, filename, level='info',when="D", backCount=180, fmt='%(asctime)s - %(levelname)s: %(module)s %(lineno)d %(message)s'):
        th = handlers.TimedRotatingFileHandler(filename=filename,when=when,backupCount=backCount,encoding='utf-8')#往文件里写入#指定间隔时间自动生成文件的处理器
        #实例化TimedRotatingFileHandler
        #interval是时间间隔，backupCount是备份文件的个数，如果超过这个个数，就会自动删除，when是间隔的时间单位，单位有以下几种：
        # S 秒
        # M 分
        # H 小时、
        # D 天、
        # W 每星期（interval==0时代表星期一）
        # midnight 每天凌晨
        th.setFormatter(logging.Formatter(fmt))#设置文件里写入的格式
        th.setLevel(logging.INFO)
        self.logger.addHandler(th)

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    @classmethod
    def get_logger(cls, filename, level='info',when="D", backCount=180, fmt='%(asctime)s - %(levelname)s: %(module)s %(lineno)d %(message)s'):
        if filename not in cls.loggers:
            cls.loggers[filename] = Logger(level=level, fmt=fmt)
            cls.loggers[filename].set_file_handler(filename, level=level, when=when, backCount=backCount, fmt=fmt)

        return cls.loggers[filename]



class GzTimedRotatingFileHandler(handlers.TimedRotatingFileHandler):
    def __init__(self, filename, when='H', interval=1, backupCount=0, encoding=None):
        super(GzTimedRotatingFileHandler, self).__init__(filename, when, interval, backupCount, encoding)
 
    def doGzip(self, old_log):
        os.system("gzip {}".format(old_log))
 
    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None
        # get the time that this sequence started at and make it a TimeTuple
        currentTime = int(time.time())
        dstNow = time.localtime(currentTime)[-1]
        t = self.rolloverAt - self.interval
        if self.utc:
            timeTuple = time.gmtime(t)
        else:
            timeTuple = time.localtime(t)
            dstThen = timeTuple[-1]
            if dstNow != dstThen:
                if dstNow:
                    addend = 3600
                else:
                    addend = -3600
                timeTuple = time.localtime(t + addend)
        dfn = self.baseFilename + "." + time.strftime(self.suffix, timeTuple)
        if os.path.exists(dfn):
            os.remove(dfn)
        # Issue 18940: A file may not have been created if delay is True.
        if os.path.exists(self.baseFilename):
            os.rename(self.baseFilename, dfn)
            self.doGzip(dfn)
        if self.backupCount > 0:
            for s in self.getFilesToDelete():
                os.remove(s)
        if not self.delay:
            self.stream = self._open()
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval
        if (self.when == 'MIDNIGHT' or self.when.startswith('W')) and not self.utc:
            dstAtRollover = time.localtime(newRolloverAt)[-1]
            if dstNow != dstAtRollover:
                if not dstNow:  # DST kicks in before next rollover, so we need to deduct an hour
                    addend = -3600
                else:  # DST bows out before next rollover, so we need to add an hour
                    addend = 3600
                newRolloverAt += addend
        self.rolloverAt = newRolloverAt



