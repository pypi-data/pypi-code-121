import logging

from izihawa_utils.tskv import TskvRecord


class BaseError(Exception):
    code = 'base_error'
    level = logging.ERROR
    info = dict()
    internal_info = dict()

    def __init__(self, **kwargs):
        self.info = dict(self.info)
        self.internal_info = dict(self.internal_info)

        if 'code' in kwargs:
            self.code = kwargs['code']

        if 'internal_info' in kwargs:
            self.internal_info.update(kwargs.pop('internal_info'))

        self.info['code'] = self.code
        self.info.update(kwargs)

    def as_dict(self):
        return dict(self.info)

    def as_tskv(self):
        return TskvRecord(self.info)

    def as_internal_dict(self):
        info = self.as_dict()
        info.update(self.internal_info)
        return info

    def as_internal_tskv(self):
        info = self.as_tskv()
        info.update(self.internal_info)
        return info

    def __repr__(self):
        r = self.as_internal_tskv()
        return str(r)

    def __str__(self):
        return repr(self)

    def add(self, key, value):
        self.info[key] = value


class MissingFileError(BaseError, FileNotFoundError):
    def __init__(self, file_path=''):
        self.info = {'path': file_path}


class NeedRetryError(BaseError):
    pass
