# -*- coding: utf-8 -*-

from enum import Enum


class BlockType(Enum):
    """
    Excel块类型
    """
    # 文本块
    text = 0

    # 表格块
    table = 1


class TableMode(Enum):
    """
    Excel块表格模式
    """
    # 标准
    standard = 0

    # 混杂模式
    mixed = 1,

    # 自定义
    custom = 2


class HorizontalAlignMode(Enum):
    """
    水平对齐方式
    """
    # 左
    left = 0

    # 中
    center = 1

    # 右
    right = 2


class VerticalAlignMode(Enum):
    """
    垂直对齐方式
    """
    # 上
    top = 0

    # 中
    middle = 1

    # 下
    bottom = 2

class AnalyticalMode(Enum):
    """
    analyticalMode
    解析模式
    1. 键值模式,默认值; 2. 表格模式;
    """
    # 键值模式
    key_value = 1
    # 表格模式
    table = 2


class FindMode(Enum):
    """
    findMode
    查找模式
    1. 纵列模式; 2. 横列模式; 0: 默认模式,为横列模式,且值在本行/本列不向下查找;
    """
    # 默认模式
    default = 0
    # 纵列模式
    v = 1
    # 横列模式
    h = 2


class SeparatorMode(Enum):
    """
    分割模式
    1. 分割字符串成列表，默认值; 2.正则表达式捕获组;
    """
    # 分割字符串成列表
    split = 1
    # 正则表达式捕获组
    regex = 2


class OverAction(Enum):
    """
    匹配成功后的行为
    1: 跳过; 2: 结束; 0:不跳过,默认值;
    """
    # 不跳过,默认值
    row = 0
    # 匹配成功后跳过
    skip = 1
    # 匹配成功后结束
    end = 2


class ActionType(Enum):
    """
    赋值模式
    1. 追加; 0: 覆盖添加,默认值; 2：裁剪模式;  3.分割模式；
    """
    #  覆盖添加,默认值
    add = 0
    # 追加
    append = 1

    # 裁剪模式,仅表格模式下生效,非表格模式下为执行覆盖添加行为
    cut = 2
    # 分割模式,仅表格模式下生效,非表格模式下为执行覆盖添加行为
    split = 3

