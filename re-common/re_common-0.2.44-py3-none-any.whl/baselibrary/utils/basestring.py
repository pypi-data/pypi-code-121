import re
import string
# 7-bit C1 ANSI escape sequences
# https://www.cnblogs.com/longdouhzt/archive/2012/09/25/2703173.html
ANSI_ESCAPE = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')


class BaseString():

    @classmethod
    def r_strip_one_char(cls, string):
        """
        去除右边的一个字符
        :param string: 
        :return: 
        """
        string = string[:-1]
        return string

    @classmethod
    def r_strip_substring(cls, string, substring):
        """
        移除子字符串
        :param string:
        :param substring:
        :return:
        """
        return string.rstrip(substring)

    @classmethod
    def r_strip_char(cls, string, number):
        """
        删除右边指定个数的字符串
        :param string: 需要处理的字符串
        :param number: 右边需要删除的字符个数
        :return: 
        """
        if number > 0:
            number = 0 - number
        elif number == 0:
            return string

        string = string[:number]
        return string

    @classmethod
    def get_strings_line_num(cls, strings, substrings, start=None, end=None):
        """
        方法用于统计字符串里某个字符出现的次数
        sub -- 搜索的子字符串
        start -- 字符串开始搜索的位置。默认为第一个字符,第一个字符索引值为0。
        end -- 字符串中结束搜索的位置。字符中第一个字符的索引为 0。默认为字符串的最后一个位置。
        :param filePath:
        :return:
        """
        if start is None:
            start = 0
        if end is None:
            end = len(strings)
        return strings.count(substrings, start=start, end=end)

    def filter_string_blank_space(self, filterobj):
        """
        过滤字符串空格
        例如  list = [' n 1 2', ' c 4s r   ']
        :return ['n12', 'c4sr']

        """
        if isinstance(filterobj, str):
            return "".join(filterobj.split())
        if isinstance(filterobj, list):
            listobj = ["".join(x.split()) for x in filterobj]
            return listobj
        else:
            assert "not have this Type，please check parameter Type" + __file__

    def string_to_list(self, string):
        """
        string 转换成list
        :param string:
        :return:  一个list每个元素一个char
        """
        mlist = [string[x] for x in range(len(string))]
        return mlist

    def parallelIterations(self, lista, listb):
        """
        并行迭代 会迭代出最少的那个  如下面的f被丢弃
            if (lista is None and listb is None):
            lista = ['1', '2', '3', '4', '5']
            listb = ['a', 'b', 'c', 'd', 'e', 'f']
        :param lista:
        :param listb:
        :return:
        """
        for aa, bb in zip(lista, listb):
            yield aa, bb

    def list_to_string(self, mlist):
        """
         b = ['a', 'b', 'c', 'd', 'e', 'f']
        :param mlist:
        :return:  string abcdef
        """
        return "".join(mlist)

    def find_sub(self, strings, substr):
        """
        strings是否存在sunstr
        :param strings:
        :param substr:
        :return:
        """
        num = strings.find(substr)
        if num == -1:
            return False
        else:
            return num

    @classmethod
    def cleanSemicolon(cls, text):
        """
        中文分号到英文分号的替换
        字符串前后分号的去除
        连续分号的合并
        分号前后空格的去除
        :param text:
        :return:
        """
        text = text.replace('；', ';')
        text = re.sub("\s+;", ";", text)
        text = re.sub(";\s+", ";", text)
        text = re.sub(";+", ";", text)
        text = re.sub("^;", "", text)
        text = re.sub(";$", "", text)
        return text.strip()

    def intercept_strings(self, str):
        """
        str = ‘0123456789’
        print str[0:3] #截取第一位到第三位的字符
        print str[:] #截取字符串的全部字符
        print str[6:] #截取第七个字符到结尾
        print str[:-3] #截取从头开始到倒数第三个字符之前
        print str[2] #截取第三个字符
        print str[-1] #截取倒数第一个字符
        print str[::-1] #创造一个与原字符串顺序相反的字符串
        print str[-3:-1] #截取倒数第三位与倒数第一位之前的字符
        print str[-3:] #截取倒数第三位到结尾
        print str[:-5:-3] #逆序截取，具体啥意思没搞明白？
        截取字符串
        :param str: 仅供参考使用
        :return:
        """

    def eval(self, strs):
        """
        将str当有效表达式
        :return:
        """
        return eval(strs)

    def lower(self, strs):
        """
        小写
        :param strs:
        :return:
        """
        return strs.lower()

    def upper(self, strs):
        """
        大写
        :param strs:
        :return:
        """
        return strs.upper()

    def swapcase(self, strs):
        """
        将字符串中的大写字母转为小写，小写字母转为大写
        :param strs:
        :return:
        """
        return strs.swapcase()

    def capitalize(self, strs):
        """
        字符串中的第一个字母大写，其他小写
        :param strs:
        :return:
        """
        return strs.capitalize()

    def title(self, strs):
        """
        将字符串中的每隔单词的首字母大写
        :param strs:
        :return:
        """
        return strs.title()

    def fillchar(self):
        """
        返回一个指定长度width的字符串str这个字符串在中间，其他位置用fillchar补全，默认是空格
        str3 = "1234"

        print(str3.center(15, "*"))
        print(str3.ljust(15, "*"))
        print(str3.rjust(15, "*"))
        print(str3.zfill(15)) #0补充

        ******1234*****
        1234***********
        ***********1234
        000000000001234


        s为字符串
        s.isalnum() 所有字符都是数字或者字母
        s.isalpha() 所有字符都是字母
        s.isdigit() 所有字符都是数字
        s.islower() 所有字符都是小写
        s.isupper() 所有字符都是大写
        s.istitle() 所有单词都是首字母大写，像标题
        s.isspace() 所有字符都是空白字符、\t、\n、\r
        参考
        :return:
        """
        pass

    @classmethod
    def hasnum(self, strings):
        """
        判断字符串是否有数字
        :param strings:
        :return:
        """
        return any(char.isdigit() for char in strings)

    @classmethod
    def chinese2digits(cls, uchars_chinese):

        common_used_numerals_tmp = {'零': 0, '一': 1, '二': 2, '两': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8,
                                    '九': 9,
                                    '十': 10, '百': 100, '千': 1000, '万': 10000, '亿': 100000000}
        total = 0
        r = 1  # 表示单位：个十百千...
        for i in range(len(uchars_chinese) - 1, -1, -1):
            # print(uchars_chinese[i])
            val = common_used_numerals_tmp.get(uchars_chinese[i])
            if val >= 10 and i == 0:  # 应对 十三 十四 十*之类
                if val > r:
                    r = val
                    total = total + val
                else:
                    r = r * val
                    # total =total + r * x
            elif val >= 10:
                if val > r:
                    r = val
                else:
                    r = r * val
            else:
                total = total + r * val
        return total

    @classmethod
    def is_space(cls, strings):
        """
        判断字符串是否全是空格
        :param strings:
        :return:
        """
        return strings.isspace()

    def str_full_to_half(self, ustring):
        """
        把字符串全角转半角
        全角字符unicode编码从65281~65374 （十六进制 0xFF01 ~ 0xFF5E）
        半角字符unicode编码从33~126 （十六进制 0x21~ 0x7E）
        空格比较特殊,全角为 12288（0x3000）,半角为 32 （0x20）
        而且除空格外,全角/半角按unicode编码排序在顺序上是对应的
        所以可以直接通过用+-法来处理非空格数据,对空格单独处理
        """
        rstring = ""
        for uchar in ustring:
            # 返回值是对应的十进制整数。
            # ord() 函数是 chr() 函数（对于8位的ASCII字符串）或 unichr() 函数（对于Unicode对象）的配对函数，它以一个字符（长度为1的字符串）作为参数，返回对应的 ASCII 数值，或者 Unicode 数值，如果所给的 Unicode 字符超出了你的 Python 定义范围，则会引发一个 TypeError 的异常。
            inside_code = ord(uchar)
            if inside_code == 0x3000:
                inside_code = 0x0020
            else:
                inside_code -= 0xfee0
            if not (0x0020 < inside_code and inside_code <= 0x7e):  # 转完之后不是半角字符返回原来的字符
                rstring += uchar
                continue
            rstring += chr(inside_code)
        return rstring

    def str_half_to_full(self, ustring):
        """把字符串半角转全角"""
        rstring = ""
        for uchar in ustring:
            inside_code = ord(uchar)
            if inside_code == 0x0020:  # 除了空格其他的全角半角的公式为:半角=全角-0xfee0
                inside_code = 0x3000
            else:
                if not (0x0020 < inside_code and inside_code <= 0x7e):
                    rstring += uchar
                    continue
                inside_code += 0xfee0
                rstring += chr(inside_code)
        return rstring

    def is_chinese(self, strings):
        """
        检查整个字符串是否包含中文
        :param string: 需要检查的字符串
        :return: bool
        """
        for ch in strings:
            if u'\u4e00' <= ch <= u'\u9fff':
                return True
        return False

    def delete_char(self, strings):
        """
        去除特殊字符，只保留汉子，字母、数字
        :return:
        """
        sub_str = re.sub("([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", "", strings)
        return sub_str

    def is_sub_str(self, strs, substrs):
        """
        判断substrs 是否存在strs中
        strs.find(substrs)>=0
        strs.index(substrs)>=0
        strs.count(substrs)>=0
        :param strs:
        :param sbustrs:
        :return:
        """
        return substrs in strs

    def remove_escape_codes(self, text):
        """
        Remove ANSI escapes codes from string. It's used to remove
        "colors" from log messages.
        """
        return ANSI_ESCAPE.sub("", text)

    @classmethod
    def is_num_float(cls, in_str):
        """
        判定是数字或者float
        :param in_str:
        :return:
        """
        if in_str.isdigit():
            return True
        else:
            try:
                float(in_str)
                return True
            except:
                return False
