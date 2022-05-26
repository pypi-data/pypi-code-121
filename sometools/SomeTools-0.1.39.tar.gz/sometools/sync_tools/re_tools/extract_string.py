# encoding='utf-8'
import re
from sometools.sync_tools.base import Base

# [^\u4e00-\u9fa5] //匹配非中文字符
# [\u4e00-\u9fa5] //匹配中文字符
# ^[1-9]\d*$ //匹配正整数
# ^[A-Za-z]+$ //匹配由26个英文字母组成的字符串
# ^[A-Z]+$ //匹配由26个英文字母的大写组成的字符串
# ^[a-z]+$ //匹配由26个英文字母的小写组成的字符串
# ^[A-Za-z0-9]+$ //匹配由数字和26个英文字母组成的字符串
# [\u4E00-\u9FA5\\s]+ 多个汉字，包括空格
# [\u4E00-\u9FA5]+ 多个汉字，不包括空格
# [\u4E00-\u9FA5] 一个汉字
# [\u4E00-\u9FA5\s\S]*?  # 多个汉字，包括空格

# 修饰符	描述
# re.I 	使匹配对大小写不敏感
# re.L 	做本地化识别（locale-aware）匹配
# re.M 	多行匹配，影响 ^ 和 $
# re.S 	使 . 匹配包括换行在内的所有字符
# re.U 	根据Unicode字符集解析字符。这个标志影响 \w, \W, \b, \B.
# re.X 	该标志通过给予你更灵活的格式以便你将正则表达式写得更易于理解。

class ExtractStringMixIn(Base):

    def __init__(self, *args, **kwargs):
        super(ExtractStringMixIn, self).__init__(*args, **kwargs)

    @staticmethod
    def extract_one_chinese(content_string: str) -> str:
        regex = r"([\u4E00-\u9FA5])"
        pattern = re.compile(regex, flags=re.S)
        match = pattern.search(content_string)
        if match and len(match.groups()) == 1:
            return match.groups()[0]
        return ''

    @staticmethod
    def extract_multi_chinese(content_string: str) -> str:
        regex = r"([\u4E00-\u9FA5]+)"
        pattern = re.compile(regex, flags=re.S)
        match = pattern.search(content_string)
        if match and len(match.groups()) == 1:
            return match.groups()[0]
        return ''

    @staticmethod
    def extract_multi_chinese_and_end_with_num(content_string: str) -> str:
        regex = r"([\u4E00-\u9FA5]+[1-9]\d*)"
        pattern = re.compile(regex, flags=re.S)
        match = pattern.search(content_string)
        if match and len(match.groups()) == 1:
            return match.groups()[0]
        return ''

    @staticmethod
    def extract_multi_chinese_and_num_and_multi_chinese(content_string: str) -> str:
        regex = r"([\u4E00-\u9FA5]+[1-9]\d*[\u4E00-\u9FA5]+)"
        pattern = re.compile(regex, flags=re.S)
        match = pattern.search(content_string)
        if match and len(match.groups()) == 1:
            return match.groups()[0]
        return ''