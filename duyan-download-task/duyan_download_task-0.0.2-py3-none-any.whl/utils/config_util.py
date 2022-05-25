import configparser
import os

import loguru

from duyan_download_task import constants

CONFIG_KEY_DOWNLOAD_TASK = 'download_task'
CONFIG_KEY_DB_HOST = 'dbHost'
CONFIG_KEY_DB_PORT = 'dbPort'
CONFIG_KEY_DB_USER = 'dbUser'
CONFIG_KEY_DB_PWD = 'dbPassword'
CONFIG_KEY_DB_NAME = 'dbName'
CONFIG_KEY_REDIS_HOST = 'redisHost'
CONFIG_KEY_REDIS_PORT = 'redisPort'
CONFIG_KEY_REDIS_PWD = 'redisPassword'
CONFIG_KEY_REDIS_DB = 'redisDb'


class ConfigException(Exception):
    def __init__(self, *arg, **kwargs):
        super().__init__(arg, kwargs)


class Config(object):

    def __init__(self, file_path):
        if not os.path.exists(file_path):
            raise Exception(f"配置文件[{file_path}]不存在")
        self.file_path = file_path
        self.config = configparser.ConfigParser()
        self.config.read(self.file_path, constants.UTF8)
        self.db_config = DbConfig(self)
        self.redis_config = RedisConfig(self)

    @loguru.logger.catch
    def get_value(self, key, field):
        if not self.config or not self.config.has_option(key, field):
            return None
        return self.config.get(key, field)


class DbConfig(object):

    def __init__(self, config: Config):
        self.host = config.get_value(CONFIG_KEY_DOWNLOAD_TASK, CONFIG_KEY_DB_HOST)
        if not self.host:
            raise ConfigException("db host can not be empty!")
        self.port = config.get_value(CONFIG_KEY_DOWNLOAD_TASK, CONFIG_KEY_DB_PORT)
        if not self.port:
            raise ConfigException("db port can not be empty!")
        self.port = int(self.port)
        self.user = config.get_value(CONFIG_KEY_DOWNLOAD_TASK, CONFIG_KEY_DB_USER)
        if not self.user:
            raise ConfigException("db user can not be empty!")
        self.password = config.get_value(CONFIG_KEY_DOWNLOAD_TASK, CONFIG_KEY_DB_PWD)
        if not self.password:
            raise ConfigException("db password can not be empty!")
        self.db_name = config.get_value(CONFIG_KEY_DOWNLOAD_TASK, CONFIG_KEY_DB_NAME)
        if not self.db_name:
            raise ConfigException("db db_name can not be empty!")


class RedisConfig(object):

    def __init__(self, config: Config):
        self.host = config.get_value(CONFIG_KEY_DOWNLOAD_TASK, CONFIG_KEY_REDIS_HOST)
        if not self.host:
            raise ConfigException("redis host can not be empty!")
        self.port = config.get_value(CONFIG_KEY_DOWNLOAD_TASK, CONFIG_KEY_REDIS_PORT)
        if not self.port:
            raise ConfigException("redis port can not be empty!")
        self.port = int(self.port)
        if not config.get_value(CONFIG_KEY_DOWNLOAD_TASK, CONFIG_KEY_REDIS_PWD):
            self.password = config.get_value(CONFIG_KEY_DOWNLOAD_TASK, CONFIG_KEY_REDIS_PWD)
        self.db = config.get_value(CONFIG_KEY_DOWNLOAD_TASK, CONFIG_KEY_REDIS_DB)
        if not self.db:
            raise ConfigException("redis db can not be empty!")
        self.db = int(self.db)
