"""
Created on 13 janv. 2019

@author: aurele durand
"""

import math, xmltodict, re
from dicttoxml import dicttoxml

from . import number_lib


def to_int(value, default=None):
    if value is None:
        return default
    try:
        return int(value), True
    except ValueError:
        return value, False


def to_num(s, default=None):
    if s is None:
        return default
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return default


def is_num(s):
    if s is None:
        return False
    try:
        a = int(s)
        return True
    except ValueError:
        try:
            a = float(s)
            return not math.isnan(a)
        except ValueError:
            return False


def is_int(val):
    try:
        num = int(val)
    except ValueError:
        return False
    return True


def format_as_string_if_not_num(s):
    s = "'%s'" % s if not is_num(s) else s
    return s


def xml_content_to_orderdict(content):
    content = re.sub("<\?.*\?>", "", content).replace("\\r\\n", "")
    content_dict = xmltodict.parse(content)
    return content_dict


def get_percentage(percentage):
    return number_lib.myround(int(percentage * 100) / 100, 1)


def encrypt(s):
    s = bytes(s, "utf-8")
    return ascii_compress(s)[0]


def decrypt(b):
    c = ascii_decompress(b)[0]
    c = c.decode("utf-8")
    return c


def ascii_compress(data, level=9):
    """ compress data to printable ascii-code """

    code = zlib.compress(data, level)
    csum = zlib.crc32(code)
    code = base64.encodestring(code)
    return code, csum


def ascii_decompress(code):
    """ decompress result of asciiCompress """

    code = base64.decodestring(code)
    csum = zlib.crc32(code)
    data = zlib.decompress(code)
    return data, csum


from functools import singledispatch


@singledispatch
def keys_to_strings(ob):
    return ob


@keys_to_strings.register
def _handle_dict(ob: dict):
    return {str(k): keys_to_strings(v) for k, v in ob.items()}


@keys_to_strings.register
def _handle_list(ob: list):
    return [keys_to_strings(v) for v in ob]


def dict_to_xml(D, attr_type=True):
    # dicttoxml fail is keys are number - need to convert them to string
    D = keys_to_strings(D)
    xml = dicttoxml(D, attr_type=attr_type)
    return xml
