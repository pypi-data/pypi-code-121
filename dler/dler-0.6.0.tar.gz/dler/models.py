#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy <wxnacy@gmail.com>
# Description: 

from typing import Dict
from pydantic import BaseModel, Field

class HeaderModel(BaseModel):
    content_type: str = Field(None, alias='Content-Type')
    content_length: int = Field(None, alias='Content-Length')
    server: str = Field(None, alias='Server')
    date: str = Field(None, alias='Date')
    connection: str = Field(None, alias='Connection')
    accept_ranges: str = Field(None, alias='Accept-Ranges')
    etag: str = Field(None, alias='ETag')
    cache_control: str = Field(None, alias='Cache-Control')
    expires: str = Field(None, alias='Expires')
    last_modified: str = Field(None, alias='Last-Modified',)

    class Meta:
        origin_data: Dict[str, str] = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.Meta.origin_data = kwargs

    def __getitem__(self, key: str) -> str:
        return self.Meta.origin_data[key]

    def get(self, key: str) -> str:
        return self.Meta.origin_data.get(key)

    def __setattr__(self, key: str, value: str) -> AttributeError:
        raise AttributeError('\'Header\' object does not support attribute assignment')


