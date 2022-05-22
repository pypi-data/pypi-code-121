import logging as pylogging


class Logger(object):

    def __init__(self, class_name):
        self._class_name = class_name
        self._log_format = '%(asctime)s [%(name)s] %(funcName)s | %(message)s'

    def set_format(self):
        return self._log_format

    def get_format(self):
        return self._log_format

    @property
    def logger(self):
        return pylogging.getLogger(self._class_name)
