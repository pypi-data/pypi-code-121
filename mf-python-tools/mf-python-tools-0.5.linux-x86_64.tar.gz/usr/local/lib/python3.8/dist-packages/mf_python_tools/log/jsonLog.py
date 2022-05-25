
import traceback
import logging
import socket
import sys
from datetime import datetime
try:
    import simplejson as json
except ImportError:
    import json

from ..tool import ranstr

RECORD_ATTRS = {
    'args',
    'asctime',
    'created',
    'exc_info',
    'exc_text',
    'filename',
    'funcName',
    'levelname',
    'levelno',
    'lineno',
    'module',
    'msecs',
    'message',
    'msg',
    'name',
    'pathname',
    'process',
    'processName',
    'relativeCreated',
    'stack_info',
    'thread',
    'threadName',
}

BASE_ATTRS = {
    'event',
    'source_random',
    'source_id',
    'source',
    'host',
    'data',
}

class JSONLOGFormatter(logging.Formatter):

    @classmethod
    def format_timestamp(cls, time):
        return datetime.fromtimestamp(time).isoformat(timespec='milliseconds')

    def format(self, record):
        '''组装logging格式
            record:{
                "name": "cement:app:cementtest",
                "msg": "this is warning",
                "args": {},
                "levelname": "WARNING",
                "levelno": 30,
                "pathname": "/home/fsy/.local/lib/python3.8/site-packages/cement/ext/ext_logging.py",
                "filename": "ext_logging.py",
                "module": "ext_logging",
                "exc_info": {},
                "exc_text": {},
                "stack_info": {},
                "lineno": 292,
                "funcName": "warning",
                "created": 1638937437.8548973,
                "msecs": 854.8972606658936,
                "relativeCreated": 173.1417179107666,
                "thread": 139641027528512,
                "threadName": "MainThread",
                "processName": "MainProcess",
                "process": 48580,
                "namespace": "cementtest"
                ...
            }
        '''

        message = self.get_base_message(record)
        extra = self.get_extra(record)
        data = self.get_data(record)

        return self.to_json(self.package(record, message, data,extra))

    def package(self,record,message, data,extra):
        m_data = []
        is_add = False
        try:
            msg = record.getMessage()
        except:
            msg = record.msg
            if len(record.args) >0:
                is_add = True
                m_data.append(msg)
                m_data = m_data +  list(record.args)
        if len(extra) >0 :
            message.update(extra)
        if isinstance(msg, str):
            if record.exc_info or record.exc_text:
                message['msg'] = str(msg) + ' ' + self.get_debug_fields(record)
            else:
                message['msg'] =  msg
        else:
            if record.exc_info or record.exc_text:
                message['msg'] = self.get_debug_fields(record)
            if not is_add:
                m_data.append(msg)
        if isinstance(data, dict):
            if len(m_data) >0:
                data['msg_ext'] = m_data
        elif isinstance(data, list):
            if len(m_data) >0:
                data.append(m_data)
        else:
            pass
        message['data'] = data
        if 'file_no' in message:
            del message['file_no']
        return message

    def get_debug_fields(self, record):
        if record.exc_info:
            exc_info = self.format_exception(record.exc_info)
        else:
            exc_info = record.exc_text
        return exc_info

    def format_exception(self, exc_info):
        return ''.join(traceback.format_exception(*exc_info)) if exc_info else ''

    def get_base_message(self, record):
        """"""
        message = {
            'datetime': self.format_timestamp(record.created),
            'source_id': self.get_source_id(record),
            'source': self.get_source(record),
            'host': self.get_host(record),
            'level': record.levelname,
            'event': self.get_event(record),
            'file_line': self.get_file_no(record),
            'msg': '',
            # 'data':  None,
        }

        return message



    def to_json(self, message, indent=None):
        try:
            return json.dumps(message, indent=indent)
        except TypeError:
            return json.dumps({})



    def get_event(self, record):
        event = ""
        if hasattr(record, 'event'):
            event = record.event
        return event

    def get_file_no(self,record):
        file =  record.pathname +" " +str(record.funcName) +": " + str(record.lineno)
        if hasattr(record, 'file_no'):
            file = record.file_no
        return file

    def get_source_id(self, record):
        source_id = ""
        if hasattr(record, 'source_id'):
            source_id = record.source_id
        else:
            if hasattr(record, 'source_random') and record.source_random:
                source_id = ranstr()
        return source_id


    def get_source(self, record):
        source = ""
        if hasattr(record, 'source'):
            source = record.source
        return source


    def get_host(self, record):
        host = ""
        if hasattr(record, 'host'):
            host = record.host
        else:
            host = self.local_host()
        return host

    def local_host(self, fqdn=False):
        host = ""
        if fqdn:
            host = socket.getfqdn()
        else:
            host = socket.gethostname()
        return host

    def get_data(self, record):
        data = {}
        if hasattr(record, 'data'):
            data = record.data
        return data

    def get_extra(self, record):
        """Returns `extra` dict you passed to logger.
        The `extra` keyword argument is used to populate the `__dict__` of
        the `LogRecord`.
        """
        m = {}
        for attr_name,y in record.__dict__.items():
            if attr_name not in RECORD_ATTRS and attr_name not in BASE_ATTRS:
                m[attr_name] = y
        return m
