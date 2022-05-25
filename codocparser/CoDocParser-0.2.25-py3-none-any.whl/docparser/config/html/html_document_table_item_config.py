# -*- coding: utf-8 -*-
from marshmallow import fields

from docparser.config.html.html_document_item_config import HtmlDocumentItemConfigSchema


class HtmlDocumentTableColumnConfigSchema(HtmlDocumentItemConfigSchema):
    """
    Html文档文本项配置
    """

    # XPath路径
    xpath = fields.Str()

    # 正则
    pattern = fields.Str()


class HtmlDocumentTableItemConfigSchema(HtmlDocumentItemConfigSchema):
    """
    Html文档表格配置
    """

    # 列
    columns = fields.Dict(keys=fields.Str(), values=fields.Nested(HtmlDocumentTableColumnConfigSchema))

