# -*- coding: utf-8 -*-
from marshmallow import Schema, fields


class HtmlDocumentItemConfigSchema(Schema):
    """
    Html文档项配置基类
    """

    # XPath路径
    xpath = fields.Str()

