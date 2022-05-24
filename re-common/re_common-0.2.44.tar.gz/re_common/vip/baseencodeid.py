import base64
import hashlib

"""
VIP编码lngid生成
"""

class BaseLngid(object):
    def __int__(self):
        pass

    def BaseEncodeID(self, strRaw):
        r""" 自定义base编码 """

        strEncode = base64.b32encode(strRaw.encode('utf8')).decode('utf8')

        if strEncode.endswith('======'):
            strEncode = '%s%s' % (strEncode[0:-6], '0')
        elif strEncode.endswith('===='):
            strEncode = '%s%s' % (strEncode[0:-4], '1')
        elif strEncode.endswith('==='):
            strEncode = '%s%s' % (strEncode[0:-3], '8')
        elif strEncode.endswith('='):
            strEncode = '%s%s' % (strEncode[0:-1], '9')

        table = str.maketrans('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'ZYXWVUTSRQPONMLKJIHGFEDCBA9876543210')
        strEncode = strEncode.translate(table)

        return strEncode

    def BaseDecodeID(self, strEncode):
        r""" 自定义base解码 """

        table = str.maketrans('ZYXWVUTSRQPONMLKJIHGFEDCBA9876543210', '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        strEncode = strEncode.translate(table)

        if strEncode.endswith('0'):
            strEncode = '%s%s' % (strEncode[0:-1], '======')
        elif strEncode.endswith('1'):
            strEncode = '%s%s' % (strEncode[0:-1], '====')
        elif strEncode.endswith('8'):
            strEncode = '%s%s' % (strEncode[0:-1], '===')
        elif strEncode.endswith('9'):
            strEncode = '%s%s' % (strEncode[0:-1], '=')

        strRaw = base64.b32decode(strEncode.encode('utf8')).decode('utf8')

        return strRaw

    def GetLngid(self, sub_db_id, rawid, case_insensitive=False):
        """
        :param sub_db_id:
        :param rawid:
        由 sub_db_id 和 rawid 得到 lngid。
        :param case_insensitive: 标识源网站的 rawid 是否区分大小写
        :return: lngid
        """
        uppercase_rawid = ''  # 大写版 rawid
        if case_insensitive:  # 源网站的 rawid 区分大小写
            for ch in rawid:
                if ch.upper() == ch:
                    uppercase_rawid += ch
                else:
                    uppercase_rawid += ch.upper() + '_'
        else:
            uppercase_rawid = rawid.upper()

        limited_id = uppercase_rawid  # 限长ID
        if len(uppercase_rawid) > 20:
            limited_id = hashlib.md5(uppercase_rawid.encode('utf8')).hexdigest().upper()
        else:
            limited_id = self.BaseEncodeID(uppercase_rawid)

        lngid = sub_db_id + limited_id

        return lngid

    def GetRawid(self, limited_id, case_insensitive=False):
        try:
            uppercase_rawid = self.BaseDecodeID(limited_id)
            if case_insensitive:
                str_ = "_"
                uppercase_rawid_list = list(uppercase_rawid)
                for num,li in enumerate(uppercase_rawid_list):
                    if li == str_:
                        old_str = "".join(uppercase_rawid_list[num-1:num+1])
                        uppercase_rawid = uppercase_rawid.replace(old_str,uppercase_rawid_list[num-1].lower())
        except Exception as e:
            raise Exception("长度超过20，不可逆")

        return uppercase_rawid