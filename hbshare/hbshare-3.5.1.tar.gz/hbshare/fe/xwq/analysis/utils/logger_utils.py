# -*- coding: utf-8 -*-

from hbshare.fe.xwq.analysis.orm.config import Config
from hbshare.fe.xwq.analysis.utils.singleton import singleton
from logging import config as configs
import logging


@singleton
class LoggerUtils:
    def __init__(self):
        self.logger = logging.getLogger()
        configs.fileConfig(Config().get_logger_properties())

    def get_logger(self):
        return self.logger