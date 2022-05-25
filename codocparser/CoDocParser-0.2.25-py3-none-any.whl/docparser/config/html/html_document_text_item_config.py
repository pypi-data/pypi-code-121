# -*- coding: utf-8 -*-
from marshmallow import fields

from docparser.config.html.html_document_item_config import HtmlDocumentItemConfigSchema


class HtmlDocumentTextItemConfigSchema(HtmlDocumentItemConfigSchema):
    """
    Html文档文本项配置
    """

    # XPath路径
    xpath = fields.Str()

    # 正则
    pattern = fields.Str()


