# -*- coding: utf-8 -*-

from marshmallow import Schema, fields

from docparser.config.excel.custom_fields import CustomFields
from docparser.config.excel.rect_config import RectConfigSchema


class BlockConfigSchema(Schema):
    """
    区块配置架构
    """

    # 区块类型
    type = CustomFields.BlockTypeField()

    # 区块数据提取器(standard）
    parser = fields.Str(required=True, default='standard')

    # 区域
    rect = fields.Nested(RectConfigSchema())


