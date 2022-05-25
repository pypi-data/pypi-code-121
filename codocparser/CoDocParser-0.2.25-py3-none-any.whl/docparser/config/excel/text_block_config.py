# -*- coding: utf-8 -*-
from marshmallow import fields

from docparser.config.excel.block_config import BlockConfigSchema


class TextBlockConfigSchema(BlockConfigSchema):
    """
    文本区块配置架构
    """

    # 正则模式
    pattern = fields.Str()




