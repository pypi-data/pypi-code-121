#!/usr/bin/env python3
# coding = utf8
"""
@ Author : ZeroSeeker
@ e-mail : zeroseeker@foxmail.com
@ GitHub : https://github.com/ZeroSeeker
@ Gitee : https://gitee.com/ZeroSeeker
"""
import base64


def lazy_b64decode(s):
    """
    base64加密后的字符串位数一定是4的整数倍，这里在解码时判断，缺多少补多少
    :param s: 需要解密的字串
    """
    add_count = len(s) % 4
    if add_count > 0:
        for _ in range(4-add_count):
            s += '='
    s_decode = base64.b64decode(s=s).decode()
    return s_decode
