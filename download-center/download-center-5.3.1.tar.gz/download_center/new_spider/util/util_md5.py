# -*- coding: utf8 -*-
import hashlib
import sys


class UtilMD5(object):
    """
    MD5工具类
    """

    @staticmethod
    def md5(s):
        m = hashlib.md5()
        m.update(s.encode("utf-8"))
        return m.hexdigest()


def test():
    print(UtilMD5.md5('wangmspider'))

if __name__ == '__main__':
    test()