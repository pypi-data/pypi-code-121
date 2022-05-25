# -*- coding: utf-8 -*-

from marshmallow import Schema, fields


class PositionConfigSchema(Schema):
    """
    定位配置
    """
    # 关键字
    keyword = fields.Str()

    # 水平对齐方式
    h_align = fields.Str()

    # 垂直对齐方式
    v_align = fields.Str()

    # 第几次匹配才满足
    match_times = fields.Integer(default=1)

    # 关键字是否在区间内
    is_outer = fields.Boolean(default=True)


class RectConfigSchema(Schema):
    """
    区域信息
    """
    # 左边关键字位置信息
    left = fields.Nested(PositionConfigSchema())

    # 顶部关键字位置信息
    top = fields.Nested(PositionConfigSchema())

    # 右边关键字位置信息
    right = fields.Nested(PositionConfigSchema())

    # 底部关键字位置信息
    bottom = fields.Nested(PositionConfigSchema())


