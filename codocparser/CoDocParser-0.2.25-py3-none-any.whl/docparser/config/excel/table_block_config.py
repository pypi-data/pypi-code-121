# -*- coding: utf-8 -*-
from marshmallow import Schema, fields

from docparser.config.excel.block_config import BlockConfigSchema


class TableColumnConfigSchema(Schema):
    """
    表格列配置架构
    """
    # 名称，未指定名称则不提取数据
    name = fields.Str()

    # 标题
    title = fields.Str(required=True)

    # 数据提取根据改正则模式提取
    title_h_align = fields.Str(required=True, default='center')

    title_v_align = fields.Str(required=True, default='middle')

    # 数据提取根据改正则模式提取
    content_pattern = fields.Str()

    # 数据提取根据改正则模式提取
    content_h_align = fields.Str(default='center')

    content_v_align = fields.Str(default='middle')

    # 子列
    childrens = fields.List(fields.Nested(lambda: TableColumnConfigSchema()))


class TableBlockConfigSchema(BlockConfigSchema):
    """
    表格区块配置架构
    """

    # 最大行数(有些单行情况直接把数据合并到主数据上，并提高采集精度)，
    # -1:不确定,动态多行模式，1:固定一行用于直接行转列
    max_rows = fields.Integer(default=-1)

    # 行分割参考列名
    row_split_ref_col_name = fields.Str()

    # 列分割字符
    col_split_chars = fields.Str()

    # 列定义集合
    columns = fields.List(fields.Nested(TableColumnConfigSchema))


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
    schema = TableBlockConfigSchema()
    result = schema.load(cma_config)
    print(result)
