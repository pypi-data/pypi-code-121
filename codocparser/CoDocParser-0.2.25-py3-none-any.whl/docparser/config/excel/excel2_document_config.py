# -*- coding: utf-8 -*-
from marshmallow import Schema, fields
from docparser.config.excel.kv_rule_config import KvRuleConfigSchema
from docparser.config.excel.table_rule_config import TableRuleConfigSchema


class ExcelDocumentConfigSchema(Schema):
    """
    Excel 文档配置
    """
    # ID
    id = fields.Str(required=True)

    # 名称
    name = fields.Str(required=True)

    # 多页模式
    multi_page = fields.Integer(required=False, default=0)

    # 页头正则
    page_pattern = fields.List(fields.Str(), required=False)

    # 键值采集数据项配置集合
    kv = fields.Dict(Keys=fields.Str(), Values=fields.Nested(KvRuleConfigSchema))

    # 表格采集数据项配置集合
    table = fields.Dict(Keys=fields.Str(), Values=fields.Nested(TableRuleConfigSchema))


if __name__ == '__main__':

    config = {
        "id": "group_A",
        "name": "多页模板",
        "kv": {
            "Arrival Vessel": {
                "position_pattern": [r"^Arrival Vessel"],
                "value_pattern": [
                    r"Arrival Vessel\s*:\s*(\w*\s*\w*\s*\d+\s+\w+)\s{4,}[\w\W]*?\nB/L No\s*:\s*([\w]*?)\s{1,}"],
                "repeat_count": 1,
                "find_mode": "default",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [""],
                "action": [
                    {"keyword": "Arrival Vessel"},
                    {"keyword": "B/L No"}
                ]
            },
            "ETA": {
                "position_pattern": [r"^ETA/ETB"],
                "value_pattern": [
                    r"[\w\W]*?(\d{2,}\s*[a-zA-Z]{3,}\s*\d{2,}\s*\d{2,}\:\d{2,}\([a-zA-Z]{2}\))[\w\W]*?(\d{2,}\s*[a-zA-Z]{3,}\s*\d{2,}\s*\d{2,}\:\d{2,})[\w\W]*?([a-zA-Z]{3,}\s*\d+\s*[a-zA-Z]{3,})"],
                "repeat_count": 1,
                "find_mode": "h",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [""],
                "action": [
                    {"keyword": "ETA"},
                    {"keyword": "vailable Date"},
                    {"keyword": "Port Free Time"},
                ]
            }
        },
        "table": {
            "bill": {
                "position_pattern": [r"^CONTAINER#"],
                "separator": "\n",
                "find_mode": "h",
                "separator_mode": "regex",
                "column": ["CHG", "RATED AS", "RATE", "PE", "COLLECT"],
                "behaviors": [
                    {
                        "over_action": "row",
                        "loop": 1,
                        "value_pattern": [
                            r"(?P<col_1>[a-zA-Z]*\s{1,}[a-zA-Z]*)\s{1,}(?P<col_2>\d{1,}\.\d{1,})\s{1,}(?P<col_3>\d{1,}\.\d{1,})\s*(?P<col_4>\w{1,})\s{1,}(?P<col_5>\d{1,}\.\d{1,})(?:\n|$)"],
                        "action": []
                    },
                    {
                        "over_action": "end",
                        "value_pattern": ["^(DESTINATION)"]
                    }
                ]
            }
        }
    }

    schema = ExcelDocumentConfigSchema()
    result = schema.load(config)
    print(result)
