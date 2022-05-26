# -*- coding:utf-8 -*-
from __future__ import absolute_import

import base64


def smart_decoder(raw_content, default_encoding_list=("utf-8", "gb18030")):
    """
    将字符串解码成unicode
    :type default_encoding_list: list of str
    :rtype: str
    :type raw_content: bytes
    """
    import chardet
    encoding = chardet.detect(raw_content).get("encoding", "utf-8")

    try:
        return raw_content.decode(encoding)
    except UnicodeDecodeError as e:
        for encoding in default_encoding_list:
            try:
                return raw_content.decode(encoding)
            except UnicodeDecodeError as e:
                pass
        raise e


def byte_to_string(byte_input: bytes, encoding="utf-8") -> str:
    """ encoding """
    return byte_input.decode(encoding)


def base64_to_string(base64_str):
    return base64.standard_b64decode(base64_str)


def string_to_base64(string):
    return base64.standard_b64encode(string)


__all__ = ("byte_to_string", "base64_to_string", "string_to_base64", "smart_decoder")
