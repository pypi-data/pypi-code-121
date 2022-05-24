# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2020-05-02 15:17:41
:LastEditTime: 2020-05-02 15:32:51
:LastEditors: HuangJingCan
:Description: 自定义实体
"""


class InvokeResult():
    """
    :description: 接口返回实体
    :param {type} 
    :return: InvokeResult
    :last_editors: HuangJingCan
    """
    def __init__(self):
        self.ResultCode = "0"
        self.ResultMessage = "调用成功"
        self.Data = None


class FileUploadInfo():
    """
    :description: 文件上传信息实体
    :param {type} 
    :return: FileUploadInfo
    :last_editors: HuangJingCan
    """
    def __init__(self):
        # 检查值
        self.Md5Value = ""
        # 上传路经
        self.ResourcePath = ""
        # 原文件名
        self.OriginalName = ""
        # 文件路经
        self.FilePath = ""
        # 图片宽度
        self.ImageWidth = 0
        # 图片高度
        self.ImageHeight = 0


class PageInfo():
    """
    :description: 分页列表实体
    :param {type} 
    :return: 
    :last_editors: HuangJingCan
    """
    def __init__(self):
        # 当前索引号
        self.PageIndex = 0
        # 页大小
        self.PageSize = 0
        # 总记录数
        self.RecordCount = 0
        # 数据
        self.Data = None

    def get_entity_by_page_info(self, page_info):
        # 页数
        page_info.PageCount = page_info.RecordCount / page_info.PageSize + 1
        if page_info.PageSize == 0:
            page_info.PageCount = 0
        if page_info.RecordCount % page_info.PageSize == 0:
            page_info.PageCount = page_info.RecordCount / page_info.PageSize
        page_info.PageCount = int(page_info.PageCount)
        # 当前页号
        page_info.PageNo = page_info.PageIndex + 1
        # 上一页索引
        page_info.PreviousIndex = page_info.PageIndex - 1 if page_info.PageIndex > 0 else 0
        # 下一页索引
        page_info.NextIndex = page_info.PageIndex + 1
        if page_info.PageCount == 0:
            page_info.NextIndex = 0
        if page_info.PageNo >= page_info.PageCount:
            page_info.NextIndex = page_info.PageIndex
        # 是否下一页
        page_info.IsNext = True
        if page_info.PageCount == 0:
            page_info.IsNext = False
        if page_info.PageNo >= page_info.PageCount:
            page_info.IsNext = False
        # 是否上一页
        page_info.IsPrevious = True
        if page_info.PageIndex == 0:
            page_info.IsPrevious = False
        # 总记录数int
        page_info.RecordCountInt = page_info.RecordCount
        # 扩展数据
        page_info.ExtendData = None

        return page_info