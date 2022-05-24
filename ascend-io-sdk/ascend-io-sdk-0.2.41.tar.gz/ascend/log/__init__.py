import logging
import threading

_format_string = "%(asctime)s %(levelname)s %(logLabel)s %(filename)s:%(lineno)d %(message)s"

_thread_local = threading.local()

logger = logging.getLogger('ascend.log')
handler = logging.StreamHandler()

logger.propagate = False  # avoid double logging if there is also a root logger

debug = logger.debug
info = logger.info
warning = logger.warning
warn = logger.warning
error = logger.error
exception = logger.exception
fatal = logger.fatal
log = logger.log


def set_log_label(log_label):
  _thread_local.log_label = log_label


def clear_log_label():
  _thread_local.log_label = ''


def get_log_label():
  try:
    return _thread_local.log_label
  except AttributeError:
    return ''


class LabelFilter(logging.Filter):
  def filter(self, record):
    record.logLabel = get_log_label()
    return True


def setLevel(newlevel):
  logger.setLevel(newlevel)
  debug('Log level set to %s', newlevel)


def init(level=logging.INFO):
  logger.setLevel(level)


handler.addFilter(LabelFilter())
handler.setFormatter(logging.Formatter(fmt=_format_string, datefmt="%y/%m/%d %H:%M:%S"))
logger.addHandler(handler)
