import os
import time
import logging
import traceback

logging.Formatter.converter = time.localtime

class Logger(logging.Logger):
    def __init__(self, name, home=os.path.expanduser('~/logs')):
        super(Logger, self).__init__(name)
        self.home = home
        if not os.path.exists(self.home):
            os.makedirs(self.home)
        self.time = time.localtime(time.time())
        self.day = self.time.tm_mday
        self.formatter = logging.Formatter('%(asctime)s : %(message)s', datefmt='%H:%M:%S')
        handler = logging.StreamHandler()
        handler.setFormatter(self.formatter)
        handler.setLevel(logging.WARNING)
        self.streamHandler = handler
        self.addHandler(handler)
        self.setLevel(logging.INFO)
        self.refresh()
        # print(f'self.level = {self.level}')

    def refresh(self):
        for h in self.handlers:
            if isinstance(h, logging.FileHandler):
                self.removeHandler(h)
        date = time.strftime(r'%Y%m%d', self.time)
        logfile = f'{self.home}/{self.name}-{date}.log'
        fileHandler = logging.FileHandler(logfile, 'a')
        fileHandler.setLevel(logging.DEBUG)
        fileHandler.setFormatter(self.formatter)
        self.addHandler(fileHandler)

    def showLogOnScreen(self):
        self.streamHandler.setLevel(self.level)

    def hideLogOnScreen(self):
        self.streamHandler.setLevel(logging.ERROR)

    def check(self):
        self.time = time.localtime(time.time())
        if self.day == self.time.tm_mday:
            return
        self.day = self.time.tm_mday
        self.refresh()

    def debug(self, message, *args, **kwargs):
        self.check()
        super(Logger, self).debug(message, *args, **kwargs)

    def info(self, message, *args, **kwargs):
        self.check()
        super(Logger, self).info(message, *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        self.check()
        super(Logger, self).warning(message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        self.check()
        super(Logger, self).error(message, *args, **kwargs)

    def critical(self, message, *args, **kwargs):
        self.check()
        super(Logger, self).critical(message, *args, **kwargs)

    def traceback(self, ex):
        for line in traceback.format_exception(ex.__class__, ex, ex.__traceback__):
            if '\n' in line:
                sublines = line.split('\n')
                for subline in sublines:
                    self.error(subline.rstrip('\n'))
            else:
                self.error(line)

##

if __name__ == '__main__':

    logger = Logger('dailylog')

    # logger.setLevel(logging.DEBUG)
    # logger.showLogOnScreen()

    logger.info('===')
    logger.debug('debug message')
    logger.info('info message')
    logger.warning('warning message')
    logger.error('error message')
    logger.critical('critical message')
