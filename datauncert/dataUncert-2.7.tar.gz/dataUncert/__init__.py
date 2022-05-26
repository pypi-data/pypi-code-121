import logging
import traceback
import datetime

# Create a main logger and set the default level low
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# custom formatting of the stream in order to add the stack trace
class myStreamFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        if record.levelno in (logging.ERROR, logging.CRITICAL):
            stack = filter(
                lambda line: ("lib/logging/__init__.py" not in line)
                and ("lib\\logging\\__init__.py") not in line,
                traceback.format_stack()[:-1]
            )
            stack = ''.join(stack)
            stack = stack.split('\n')
            stack = stack[:len(stack) - 3]
            stack = '\n'.join(stack)
            return record.msg + "\nOrigin :\n" + "".join(stack)


# overload the streamhandler class in order to exit after emitting
class myStreamHandler(logging.StreamHandler):
    def emit(self, record):
        super().emit(record)
        if record.levelno in (logging.ERROR, logging.CRITICAL):
            raise SystemExit(-1)


# Create a stream formatter with a level of ERROR
streamFormatter = myStreamFormatter()
streamHandler = myStreamHandler()
streamHandler.setLevel(logging.ERROR)
streamHandler.setFormatter(streamFormatter)
logger.addHandler(streamHandler)


def setLogLevel(level):
    # custom formatter in order to add the stack trace
    class myFileFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            t = datetime.datetime.now()
            msg = f'{t}'
            msg += f' - {record.name}{" "*(21 - len(record.name))}'
            msg += f' - Line {record.lineno}{" "*(3-len(str(record.lineno)))}'
            msg += f' - {record.levelname}{" "*(8 - len(record.levelname))}'
            msg += f' - {record.msg}'
            if record.levelno in (logging.ERROR, logging.CRITICAL):
                stack = filter(
                    lambda line: ("lib/logging/__init__.py" not in line)
                    and ("lib\\logging\\__init__.py") not in line,
                    traceback.format_stack()[:-1]
                )
                stack = ''.join(stack)
                stack = stack.split('\n')
                stack = stack[:len(stack) - 1]
                stack = '\n'.join(stack)
                msg += "\nOrigin :\n" + "".join(stack)
            return msg

    # create a file formatter. This is written to 'log.log' with a level of INFO
    fileFormatter = myFileFormatter()
    fileHandler = logging.FileHandler('log.log', mode='w+')
    fileHandler.setFormatter(fileFormatter)

    # add the handlers
    fileHandler.setLevel(level)

    # change the order of the filehandler and the streamhandler
    # this is necessary in order to add the stack trace to both the log and the console before exiting
    logger = logging.getLogger(__name__)
    logger.removeHandler(streamHandler)
    logger.addHandler(fileHandler)
    logger.addHandler(streamHandler)


# import the necessary modules
from dataUncert.variable import *
from dataUncert.fit import *
from dataUncert.readData import *
