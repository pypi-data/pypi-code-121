# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

from hagworm.extend.base import Utils
from hagworm.extend.config import Configure, Field, HostType, StrListType


class _Static(Configure):

    MySqlMasterServer: HostType = Field(r'MySql')
    MySqlSlaveServer: HostType = Field(r'MySql')
    MySqlName: str = Field(r'MySql')
    MySqlUser: str = Field(r'MySql')
    MySqlPasswd: str = Field(r'MySql')
    MySqlMasterMinConn: int = Field(r'MySql')
    MySqlMasterMaxConn: int = Field(r'MySql')
    MySqlSlaveMinConn: int = Field(r'MySql')
    MySqlSlaveMaxConn: int = Field(r'MySql')

    MongoHost: StrListType = Field(r'Mongo')
    MongoAuth: str = Field(r'Mongo')
    MongoUser: str = Field(r'Mongo')
    MongoPasswd: str = Field(r'Mongo')
    MongoMinConn: int = Field(r'Mongo')
    MongoMaxConn: int = Field(r'Mongo')

    RedisHost: HostType = Field(r'Redis')
    RedisBase: int = Field(r'Redis')
    RedisPasswd: str = Field(r'Redis')
    RedisMinConn: int = Field(r'Redis')
    RedisMaxConn: int = Field(r'Redis')
    RedisExpire: int = Field(r'Redis')
    RedisKeyPrefix: str = Field(r'Redis')


class _Dynamic(Configure):

    Port: int = Field(r'Base')
    Debug: bool = Field(r'Base')
    GZip: bool = Field(r'Base')
    Secret: str = Field(r'Base')
    ProcessNum: int = Field(r'Base')
    ServerName: str = Field(r'Base')

    AllowOrigins: StrListType = Field(r'Cros')
    AllowMethods: StrListType = Field(r'Cros')
    AllowHeaders: StrListType = Field(r'Cros')
    AllowCredentials: bool = Field(r'Cros')

    LogLevel: str = Field(r'Log')
    LogFilePath: str = Field(r'Log')
    LogFileSplitSize: int = Field(r'Log')
    LogFileSplitTime: str = Field(r'Log')
    LogFileBackups: int = Field(r'Log')

    ThreadPoolMaxWorkers: int = Field(r'ThreadPool')


ConfigStatic = _Static()
ConfigDynamic = _Dynamic()

cluster = Utils.getenv(r'CLUSTER', None)

if cluster is None:
    ConfigStatic.read(r'./config/static.conf')
    ConfigDynamic.read(r'./config/dynamic.conf')
else:
    ConfigStatic.read(f'./config/static.{cluster.lower()}.conf')
    ConfigDynamic.read(f'./config/dynamic.{cluster.lower()}.conf')
