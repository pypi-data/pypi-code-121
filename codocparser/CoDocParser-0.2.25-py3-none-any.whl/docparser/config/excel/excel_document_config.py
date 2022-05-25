# -*- coding: utf-8 -*-
from marshmallow import fields

from docparser.config.excel.block_config import BlockConfigSchema


class ExcelDocumentConfigSchema:
    """
    Excel 文档配置
    """
    # 名称
    name = fields.Str()

    # 内容匹配正则
    content_pattern = fields.Str()

    # 文件名匹配正则
    name_pattern = fields.Str()

    """
    采集数据项配置集合
    """
    # 集合
    items = fields.Dict(keys=fields.Str(), values=fields.Nested(BlockConfigSchema))


if __name__ == '__main__':
    cma_config = {
        "type": "table",
        "parser": "mixed",
        "max_rows": 1,
        "row_split_ref_col_name": "container_no",
        "col_split_chars": "  ",
        "rect": {
            "top": {
                "keyword": "CONTAINER  # ",
                "include": True
            },
            "bottom": {
                "keyword": "PLEASE NOTE :",
            }
        },
        "columns": [
            {
                "name": "container_no",
                "title": "CONTAINER #",
                "title_h_align": "center",
                "title_v_align": "middle",
                "content_pattern": "\\w{0,20}",
            }, {
                "name": "seal_no",
                "title": "SEAL #",
                "title_h_align": "center",
                "title_v_align": "middle",
                "content_pattern": "\\w{0,20}",
            }, {
                "name": "container_size_type",
                "title": "SIZE/TYPE #",
                "title_h_align": "center",
                "title_v_align": "middle",
                "content_pattern": "\\d{1,10}\\s{1,2}\\[a-z|A-Z]{2,5}",
            }, {
                "name": "weight",
                "title": "WEIGHT",
                "title_h_align": "center",
                "title_v_align": "middle",
                "content_pattern": "\\d{0,10}",
            }, {
                "name": "measure",
                "title": "MEASURE",
                "title_h_align": "center",
                "title_v_align": "middle",
                "content_pattern": "\\w{0,5}",
            }, {
                "name": "free_business_last_free",
                "title": "FREE BUSINESS LAST FREE",
                "title_h_align": "center",
                "title_v_align": "middle",
                "childrens": [
                    {
                        "name": "day_at_port",
                        "title": "DAYS AT PORT",
                        "title_h_align": "center",
                        "title_v_align": "middle",
                        "content_pattern": "\\w{0,20}",
                    },
                    {
                        "name": "day_at_ramp",
                        "title": "DAY AT RAMP",
                        "title_h_align": "center",
                        "title_v_align": "middle",
                        "content_pattern": "\\d{1,2}/\\d{1,2}/\\d{1,2}",
                    }
                ]
            }, {
                "name": "pickup_no",
                "title": "PICKUP #",
                "title_h_align": "center",
                "title_v_align": "middle",
                "content_pattern": "\\w{0,20}",
            },
        ]
    }
    # schema = TableBlockConfigSchema()
    # result = schema.load(cma_config)
    # print(result)
