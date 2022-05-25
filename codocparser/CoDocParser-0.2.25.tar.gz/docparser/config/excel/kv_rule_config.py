# -*- coding: utf-8 -*-
from marshmallow import fields
from docparser.config.excel.action_config import ActionConfigSchema
from docparser.config.excel.rule_config import RuleConfigSchema


class KvRuleConfigSchema(RuleConfigSchema):
    """
    键值对提取规则配置
    """
    # 提取规则组
    value_pattern = fields.List(fields.Str(), required=True)
    # 重复匹配次数
    repeat_count = fields.Integer(default=1)
    # 是否拆分单元格
    is_split_cell = fields.Integer(default=0)
    # 拆分规则
    split_pattern = fields.List(fields.Str())
    # 行动组
    action = fields.List(fields.Nested(ActionConfigSchema, many=True))
