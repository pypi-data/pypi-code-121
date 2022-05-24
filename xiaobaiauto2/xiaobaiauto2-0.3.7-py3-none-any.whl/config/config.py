#! /usr/bin/env python
__author__ = 'Tser'
__email__ = '807447312@qq.com'
__project__ = 'xiaobaiauto2'
__script__ = 'config.py'
__create_time__ = '2020/7/15 23:18'

from os import path
import logging
from xiaobaiauto2.__version__ import __version__
from xiaobaiauto2.data.GLO_VARS import PUBLIC_VARS

class LOGCONFIG:
    def __init__(self):
        log_name = 'xiaobaiauto2'
        log_level = logging.DEBUG
        log_fmt = '%(asctime)s %(levelname)s %(filename)s %(funcName)s %(lineno)d: %(message)s'
        log_file_name = 'xiaobaiauto2_debug.log'
        logger = logging.getLogger(log_name)
        logger.setLevel(log_level)
        fmt = logging.Formatter(log_fmt)
        '''
        'ERROR': logging.ERROR,
        'WARNING': logging.WARNING,
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG,
        'NOTSET': logging.NOTSET
        '''
        fileHandle = logging.FileHandler(log_file_name)
        fileHandle.setLevel(logging.DEBUG)
        fileHandle.setFormatter(fmt=fmt)
        logger.addHandler(fileHandle)

class DBCONFIG:
    def __init__(self):
        if 'dbpath' in PUBLIC_VARS.keys():
            self.dbapth = PUBLIC_VARS['dbpath']
        else:
            self.dbpath = path.dirname(path.abspath(__file__)) + '/../data/xiaobaiauto2.db'

class APICONFIG:
    def __init__(self):
        if 'base' in PUBLIC_VARS.keys():
            self.base = PUBLIC_VARS['base']
        else:
            self.base = 'https://test.xiaobai.com'

class TIMERCONFIG:
    def __init__(self):
        if 'geometry' in PUBLIC_VARS.keys():
            self.geometry = PUBLIC_VARS['geometry']
        else:
            self.geometry = '500x350'
        if 'timerpath' in PUBLIC_VARS.keys():
            self.timerpath = PUBLIC_VARS['timerpath']
        else:
            self.timerpath = path.dirname(path.abspath(__file__)) + '/../data/favicon.ico'
        if 'timerTitle' in PUBLIC_VARS.keys():
            self.timerTitle = PUBLIC_VARS['timerTitle']
        else:
            self.timerTitle = '小白定时器 v' + __version__ + '  '
        if 'timerRuningTitle' in PUBLIC_VARS.keys():
            self.timerRuningTitle = PUBLIC_VARS['timerRuningTitle']
        else:
            self.timerRuningTitle = '小白定时器 v%s [运行中] ' % __version__

class EMAILCONFIG:
    def __init__(self):
        if 'sender' in PUBLIC_VARS.keys():
            self.sender = PUBLIC_VARS['sender']
        else:
            self.sender = '807447312@qq.com'
        if 'receiver' in PUBLIC_VARS.keys():
            self.receiver = PUBLIC_VARS['receiver']
        else:
            self.receiver = '807447323@qq.com'
        if 'smtpserver' in PUBLIC_VARS.keys():
            self.smtpserver = PUBLIC_VARS['smtpserver']
        else:
            self.smtpserver = 'smtp.qq.com'
        if 'smtp_port' in PUBLIC_VARS.keys():
            self.smtp_port = PUBLIC_VARS['smtp_port']
        else:
            self.smtp_port = 25
        if 'username' in PUBLIC_VARS.keys():
            self.username = PUBLIC_VARS['username']
        else:
            self.username = 'username'
        if 'password' in PUBLIC_VARS.keys():
            self.password = PUBLIC_VARS['password']
        else:
            self.password = 'password'
        if 'subject' in PUBLIC_VARS.keys():
            self.subject = PUBLIC_VARS['subject']
        else:
            self.subject = '小白自动化测试报告'
        if 'report' in PUBLIC_VARS.keys():
            self.report = PUBLIC_VARS['report']
        else:
            self.report = 'report.html'

class CASE_TYPE:
    def __init__(self):
        # Separator
        if 'filepytes' in PUBLIC_VARS.keys():
            self.filepytes = PUBLIC_VARS['filepytes']
        else:
            self.filepytes = [('TEXT', '*.txt'), ('CSV', '*.csv'), ('JSON', '*.json'), ('YAML', '*.yaml')]
        if 'caseSeparator' in PUBLIC_VARS.keys():
            self.caseSeparator = PUBLIC_VARS['caseSeparator']
        else:
            self.caseSeparator = ';;'