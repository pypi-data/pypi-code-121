# -*- coding: utf-8 -*-
from marshmallow import Schema, fields
from docparser.config.excel.custom_fields import CustomFields
from docparser.config.excel.action_config import ActionConfigSchema


class TableBehaviorConfigSchema(Schema):
    """
    匹配行为组
    """
    # 匹配行为结束后之后的操作
    over_action = CustomFields.OverActionField(required=True)

    # 行匹配的正则
    row_pattern = fields.List(fields.Str(), required=True)

    # 格式化匹配后的值， 纵列模式在分列前格式化字符串，其余条件下则是在赋值之前格式化
    value_format = fields.Str(required=False)

    # 分隔符置换符
    repl_separator = fields.Str(required=False, default=0)

    # 循环模式
    loop = fields.Integer(required=False)

    # 行动组
    action = fields.List(fields.Nested(ActionConfigSchema, many=True))
