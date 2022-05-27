import logging
import inspect
import re
import sys
import time
import traceback
from typing import Any
from logging.handlers import TimedRotatingFileHandler

from ..os.path import create_dir_if_not_exist
from ..os.file import get_file_folder, get_file_name

LOG_FORMAT = '[%(asctime)s] level: [%(levelname)s] module: [%(filename)s] func: [%(funcName)s] lineno: [%(lineno)d] msg: [%(message)s]'
LOG_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

class MyLoggerHandler(logging.Handler):

    def __init__(self, *args, **kargs):
        logging.Handler.__init__(self, *args, **kargs)

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
        except Exception:
            self.handleError(record)

class MyLogLevel():
    CRITICAL = 50
    FATAL = CRITICAL
    ERROR = 40
    WARNING = 30
    WARN = WARNING
    INFO = 20
    DEBUG = 10
    NOTSET = 0

class MyLogRecord(object):
  
    def __init__(self, msg, log_level: int=MyLogLevel.INFO, fmt: str=LOG_FORMAT, log_time_fmt: str=LOG_TIME_FORMAT, **kwargs):

        self.fmt = fmt
        stack = inspect.stack()[1]
        self.record = {'level': log_level, 'levelname': '{0:<5s}'.format(logging.getLevelName(log_level))[:5], 'asctime': time.strftime(log_time_fmt, time.localtime(time.time())), 'message': msg, 'filename': get_file_name(stack[1]), 'funcName': stack[3], 'lineno': stack[2]}

    def format_msg(self):
        return f"{self.fmt % self.record}"

    def get_msg(self):
        return str(self.record.get('message'))


class MyStdout():

    def __init__(self):
        self.stdout_bak = sys.stdout
        self.stderr_bak = sys.stderr
        self.stdout = self
        self.stderr = self

    def write(self, info):
        if info.find('[INFO ]') >= 0:
            info = f"\033[0;34m{info}\033[0m"
        elif info.find('DEBUG') >= 0:
            info = f"\033[0;36m{info}\033[0m"
        elif info.find('[WARNI]') >= 0:
            info = f"\033[0;33m{info}\033[0m"
        elif info.find('[ERROR]') >= 0:
            info = f"\033[0;31m{info}\033[0m"
        self.stdout_bak.write(info)

    def flush(self):
        pass


def init_log(file_path: str, log_level: int, log_interval: int=1, log_backup: int=30, log_time_fmt: str=LOG_TIME_FORMAT, attach_handles: list=[]):
    file_folder = get_file_folder(file_path)
    if create_dir_if_not_exist(file_folder) is True:

        handler_file = TimedRotatingFileHandler(filename=file_path, when="D", interval=log_interval, backupCount=log_backup)
        handler_file.suffix = "%Y-%m-%d_%H-%M.log"
        handler_file.setLevel(log_level)
        attach_handles.append(handler_file)

        return logging.basicConfig(level=log_level, format=LOG_FORMAT, datefmt=log_time_fmt, handlers=attach_handles)

def convert_msg(log_content: str):
    if len(log_content) > 0:
        return re.search(r'\[(?P<asctime>.*?)] level: \[(?P<level>.*?)] module: \[(?P<module>.*?)] func: \[(?P<func>.*?)] lineno: \[(?P<lineno>.*?)] msg: \[(?P<msg>.*)]', log_content).groupdict()

def format_log(log_content: Any):
    func = inspect.stack()[1]
    return {'file': get_file_name(func[1]), 'func': func[3], 'lineno': func[2], 'msg': log_content}

def _get_normalized_locals_text(locals_dict) -> str:
    var_text_list = []
    for var_name, var_value in locals_dict.items():
        if var_name.startswith('__') or var_name == 'self':
            continue
        var_text_list.append(f"{var_name}={str(var_value)[:200]}")
    return ', '.join(var_text_list)


def log_unhandled_error(**kwargs):
    stacks = traceback.StackSummary.extract(traceback.walk_stack(None), limit=kwargs.get('limit', 2), capture_locals=kwargs.get('capture_locals', True))
    stack_len = len(stacks)
    if stack_len == 0:
        locals_text = "NO_STACK"
    elif stack_len == 1:
        locals_text = _get_normalized_locals_text(stacks[0].locals)
    else:
        locals_text = _get_normalized_locals_text(stacks[1].locals)
    logging.error(f"Unhandled exception! Locals: {locals_text}.", exc_info=kwargs.get('exc_info', False), stack_info=kwargs.get('stack_info', False))