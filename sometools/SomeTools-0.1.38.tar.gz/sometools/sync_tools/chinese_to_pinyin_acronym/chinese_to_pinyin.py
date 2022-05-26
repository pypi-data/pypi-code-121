from sometools.sync_tools.base import Base

class ChineseToPinyinMixIn(Base):

    def __init__(self, *args, **kwargs):
        super(ChineseToPinyinMixIn, self).__init__(*args, **kwargs)

    @staticmethod
    def get_pinyin(chinese_string: str) -> str:
        """
        输入中文字符串返回拼音的首字母字符串
        :param chinese_string: str
        :return: str
        """
        if chinese_string:
            lst = list(chinese_string)
            charLst = []
            for unicode1 in lst:
                str1 = unicode1.encode('gbk')
                try:
                    ord(str1)
                    charLst.append(str1.decode('gbk'))
                except:
                    asc = str1[0] * 256 + str1[1] - 65536
                    if asc >= -20319 and asc <= -20284:
                        charLst.append('a')
                    if asc >= -20283 and asc <= -19776:
                        charLst.append('b')
                    if asc >= -19775 and asc <= -19219:
                        charLst.append('c')
                    if asc >= -19218 and asc <= -18711:
                        charLst.append('d')
                    if asc >= -18710 and asc <= -18527:
                        charLst.append('e')
                    if asc >= -18526 and asc <= -18240:
                        charLst.append('f')
                    if asc >= -18239 and asc <= -17923:
                        charLst.append('g')
                    if asc >= -17922 and asc <= -17418:
                        charLst.append('h')
                    if asc >= -17417 and asc <= -16475:
                        charLst.append('j')
                    if asc >= -16474 and asc <= -16213:
                        charLst.append('k')
                    if asc >= -16212 and asc <= -15641:
                        charLst.append('l')
                    if asc >= -15640 and asc <= -15166:
                        charLst.append('m')
                    if asc >= -15165 and asc <= -14923:
                        charLst.append('n')
                    if asc >= -14922 and asc <= -14915:
                        charLst.append('o')
                    if asc >= -14914 and asc <= -14631:
                        charLst.append('p')
                    if asc >= -14630 and asc <= -14150:
                        charLst.append('q')
                    if asc >= -14149 and asc <= -14091:
                        charLst.append('r')
                    if asc >= -14090 and asc <= -13119:
                        charLst.append('s')
                    if asc >= -13118 and asc <= -12839:
                        charLst.append('t')
                    if asc >= -12838 and asc <= -12557:
                        charLst.append('w')
                    if asc >= -12556 and asc <= -11848:
                        charLst.append('x')
                    if asc >= -11847 and asc <= -11056:
                        charLst.append('y')
                    if asc >= -11055 and asc <= -10247:
                        charLst.append('z')
                    charLst.append('')
            return ''.join(charLst)
        return ''

    def __str__(self):
        return '中文汉字转拼音 obj name:ChineseToPinyinMixIn'
    __repr__ = __str__


if __name__ == '__main__':
    print(ChineseToPinyinMixIn().get_pinyin('中国外汇交易中心'))
