# -*- coding: utf-8 -*-
from marshmallow import Schema, fields
from docparser.config.excel.custom_fields import CustomFields


class ActionConfigSchema(Schema):
    """
    匹配行为对象
    """
    # 关键字
    keyword = fields.List(fields.Str(), required=True)

    # 匹配结果的索引
    key = CustomFields.ActionKeyField(required=True)

    # 赋值模式
    action_type = CustomFields.ActionTypeField(required=True)

    # 匹配正则
    pattern_list = fields.List(fields.Str(), default=[])

    # 默认值
    default_value = fields.Str(default=None)
