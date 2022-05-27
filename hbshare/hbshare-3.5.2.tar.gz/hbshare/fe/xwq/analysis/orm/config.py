# -*- coding: utf-8 -*-
from hbshare.fe.xwq.analysis.utils.file_reader import FileReader
from hbshare.fe.xwq.analysis.utils.singleton import singleton
import configparser
import traceback


# @singleton
class Config(object):
    def __init__(self):
        try:
            config_string = FileReader.get_json_cfg('env.properties')
            config = configparser.ConfigParser()
            config.read_string(config_string)
            self.obj_instance = dict(config.items('prd'))
        except ValueError as e:
            exstr = traceback.format_exc()
            print('[envConfig] read env.properties failed!')
            print(exstr)

    def get_db_properties(self):
        return self.obj_instance['db.properties']

    def get_env_properties(self):
        return self.obj_instance['env.properties']

    def get_logger_properties(self):
        return self.obj_instance['logger.properties']

    def get_sql(self):
        return self.obj_instance['sql']

    def get_data_path(self):
        return self.obj_instance['data.path']

    def get_daily_k_start_date(self):
        return self.obj_instance['daily.k.start.date']

    def get_send_email(self):
        return int(self.obj_instance['send.email'])