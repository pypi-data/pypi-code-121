# -*- coding: utf-8 -*-
from docparser.config.excel.table_block_config import TableBlockConfigSchema


class ConfigManager:
    """
    配置管理器
    """

    @staticmethod
    def load(config):
        schema = TableBlockConfigSchema()
        result = schema.load(config)
        return result





