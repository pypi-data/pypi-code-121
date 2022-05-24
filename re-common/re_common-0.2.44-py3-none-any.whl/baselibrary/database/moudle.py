#!/usr/bin/env python
# -*- coding:utf-8 -*-
from pymysql.cursors import Cursor


# pymysql的moudle
class SqlMoudle(object):
    def __init__(self):
        """
           host
          string, host to connect
          
        user
          string, user to connect as

        passwd
          string, password to use

        db
          string, database to use

        port
          integer, TCP/IP port to connect to

        这是一个标准连接的所有参数
        cursorclass pymysql.cursors.DictCursor 表示返回数据为dicts
        """
        self.host = None
        self.user = None
        self.password = ""
        self.database = None
        self.port = 3306
        self.unix_socket = None
        self.charset = ''
        self.sql_mode = None
        self.read_default_file = None
        self.conv = None
        self.use_unicode = True
        self.client_flag = 0
        self.cursorclass = Cursor
        self.init_command = None
        self.connect_timeout = 10
        self.ssl = None
        self.read_default_group = None
        self.compress = None
        self.named_pipe = None
        self.autocommit = False
        self.db = None
        self.passwd = None
        self.local_infile = False
        self.max_allowed_packet = 16 * 1024 * 1024
        self.defer_connect = False
        self.auth_plugin_map = None
        self.read_timeout = None
        self.write_timeout = None
        self.bind_address = None
        self.binary_prefix = False
        self.program_name = None
        self.server_public_key = None

    # @property
    # def get_serveraddress(self):
    #     return self._serveraddress
    #
    # @get_serveraddress.setter
    # def set_serveraddress(self,serveraddress):
    #     self._serveraddress = serveraddress
    #
    # @get_serveraddress.deleter
    # def del_serveraddress(self):
    #     del self._serveraddress

    def to_dict(self):
        return self.__dict__

    def __str__(self):
        return str(self.__dict__)


# sqlite3的 moudle
class Sqlite3Moudle(object):
    def __init__(self):
        self.database = ""
        self.timeout = None
        self.detect_types = None
        self.isolation_level = None
        self.check_same_thread = None
        self.factory = None
        self.cached_statements = None
        # self.uri = None

    def to_dict(self):
        return self.__dict__
