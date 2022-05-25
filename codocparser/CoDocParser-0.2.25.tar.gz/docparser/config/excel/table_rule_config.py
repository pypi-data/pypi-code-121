# -*- coding: utf-8 -*-
from marshmallow import fields
from docparser.config.excel.table_behavior_config import TableBehaviorConfigSchema
from docparser.config.excel.rule_config import RuleConfigSchema


class TableRuleConfigSchema(RuleConfigSchema):
    """
    键值对提取规则配置
    """
    # 表头
    column = fields.List(fields.Str(), required=True)
    # 行动组
    action = fields.List(fields.Nested(TableBehaviorConfigSchema, many=True))
