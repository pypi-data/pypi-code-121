# -*- coding: utf-8 -*-
from marshmallow import Schema, fields
from docparser.config.excel.custom_fields import CustomFields


class RuleConfigSchema(Schema):
    """
    提取规则配置
    """
    # 定位规则
    position_pattern = CustomFields.ActionKeyField(required=True)
    # 单元格查找方向
    find_mode = CustomFields.FindModeField(required=True, default=0)
    # 匹配模式
    separator_mode = CustomFields.SeparatorModeField(required=True, default=0)
