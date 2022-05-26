import datetime
import logging
from io import StringIO
import functools


def initlog(version=None):
    # enable logging
    starttime = "{:%Y-%b-%d %H:%M:%S}".format(datetime.datetime.now())
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logstream = StringIO()
    loghandler = logging.StreamHandler(logstream)
    loghandler.setLevel(logging.INFO)
    logger.addHandler(loghandler)
    logger.propagate = False
    # start log
    if version:
        logger.info("version " + f"{version}")
    logger.info(f"{starttime}\n")
    return logger, logstream

    ###


def log(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        res = func(self, *args, **kwargs)
        # store call to function in logstring
        methodname = func.__name__
        logstring = methodname + "("
        if any(args):
            argslist = [repr(a) for a in args]
        else:
            argslist = []
        if any(kwargs):
            kwargslist = [f"{k}={v!r}" for k, v in kwargs.items()]
        else:
            kwargslist = []
        logstring += ", ".join(argslist + kwargslist) + ")\n"
        self.logger.info(logstring)
        return res
    return wrapper
