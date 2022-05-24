# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2020-04-22 14:32:40
:LastEditTime: 2020-05-03 15:40:35
:LastEditors: HuangJingCan
:Description: 枚举类
"""

from enum import Enum, unique


class ButtonType(Enum):
    """
    :description: 按钮类型
    :param {type} 
    :return: 
    :last_editors: HuangJingCan
    """
    # 新增
    Add = 1
    # 修改
    Modify = 2
    # 删除
    Delete = 3
    # 保存
    Save = 4
    # 返回
    Back = 5
    # 查询
    Search = 6
    # 详细
    View = 7
    # 发布
    Release = 8
    # 取消发布
    UnRelease = 9


class ButtonPlace(Enum):
    """
    :description: 按钮位置
    :param {type} 
    :return: 
    :last_editors: HuangJingCan
    """
    Top = 1  # 顶部
    List = 2  # 列表


class QueryMethod(Enum):
    """
    :description: 查询方式
    :param {type} 
    :return: 
    :last_editors: HuangJingCan
    """
    # 等于
    Equal = "Equal"
    # 大于
    GreaterThan = "GreaterThan"
    # 大于等于
    GreaterThanOrEqual = "GreaterThanOrEqual"
    # 小于
    LessThan = "LessThan"
    # 小于等于
    LessThanOrEqual = "LessThanOrEqual"
    # 不等于
    NotEqual = "NotEqual"
    # LIKE '值%'
    StartsWith = "StartsWith"
    # LIKE '值%'
    EndsWith = "EndsWith"
    # LIKE '%值%'
    Contains = "Contains"
    # 多值查询
    ORLike = "ORLike"


class QueryDataType(Enum):
    """
    :description: 查询数据类型
    :param {type} 
    :return: 
    :last_editors: HuangJingCan
    """
    # 字符串型
    String = "String"
    # 数字型
    Int = "Int"
    # 时间
    Date = "Date"


class QuerySortType(Enum):
    """
    :description: 排序类型
    :param {type} 
    :return: 
    :last_editors: HuangJingCan
    """
    # 降序
    Desc = "Desc"
    # 升序
    Asc = "Asc"


class AccessModeCodeType(Enum):
    """
    :description: 访问方式代码
    :param {type} 
    :return: 
    :last_editors: HuangJingCan
    """
    # 虚拟访问方式
    VirtualAccess = 0
    # 虚拟原文件访问方式
    VirtualOriginalAccess = 1


class PathFormatCodeType(Enum):
    """
    :description: 路径格式代码
    :param {type} 
    :return: 
    :last_editors: HuangJingCan
    """
    # 按创建日期组织
    ByDate = 0
    # 按创建日期加小时组织
    ByDateAndHour = 1
    # 按唯一标识分组组织
    ByID = 2
    # 不分组
    ByNone = 3