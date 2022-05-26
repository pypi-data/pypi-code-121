import opencc
from sometools.sync_tools.base import Base

class TraditionalSimplifiedChineseMixIn(Base):
    """
    hk2s: Traditional Chinese (Hong Kong standard) to Simplified Chinese

    s2hk: Simplified Chinese to Traditional Chinese (Hong Kong standard)

    s2t: Simplified Chinese to Traditional Chinese

    s2tw: Simplified Chinese to Traditional Chinese (Taiwan standard)

    s2twp: Simplified Chinese to Traditional Chinese (Taiwan standard, with phrases)

    t2hk: Traditional Chinese to Traditional Chinese (Hong Kong standard)

    t2s: Traditional Chinese to Simplified Chinese

    t2tw: Traditional Chinese to Traditional Chinese (Taiwan standard)

    tw2s: Traditional Chinese (Taiwan standard) to Simplified Chinese

    tw2sp: Traditional Chinese (Taiwan standard) to Simplified Chinese (with phrases)
    """

    def __init__(self, *args, **kwargs):
        super(TraditionalSimplifiedChineseMixIn, self).__init__(*args, **kwargs)

    @staticmethod
    def traditional_chinese_to_simplified(chinese_string: str) -> str:
        """
        t2s - 繁体转简体（Traditional Chinese to Simplified Chinese）
        :param chinese_string: str
        :return: str
        """
        cc = opencc.OpenCC('t2s')
        s = cc.convert(chinese_string)
        return s

    @staticmethod
    def simplified_chinese_to_traditional_chinese(chinese_string: str) -> str:
        """
        s2t - 简体转繁体（Simplified Chinese to Traditional Chinese）
        :param chinese_string: str
        :return: str
        """
        cc = opencc.OpenCC('s2t')
        s = cc.convert(chinese_string)
        return s


if __name__ == '__main__':
    print(TraditionalSimplifiedChineseMixIn().traditional_chinese_to_simplified('眾議長與李克強會談'))
    print(TraditionalSimplifiedChineseMixIn().simplified_chinese_to_traditional_chinese('众议长与李克强会谈'))
