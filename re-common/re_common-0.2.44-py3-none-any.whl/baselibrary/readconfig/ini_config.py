"""
1.基本的读取配置文件

-read(filename) 直接读取ini文件内容

-sections() 得到所有的section，并以列表的形式返回

-options(section) 得到该section的所有option

-items(section) 得到该section的所有键值对

-get(section,option) 得到section中option的值，返回为string类型

-getint(section,option) 得到section中option的值，返回为int类型，还有相应的getboolean()和getfloat() 函数。

2.基本的写入配置文件

-add_section(section) 添加一个新的section

-set( section, option, value) 对section中的option进行设置，需要调用write将内容写入配置文件。
如果配置文件如下
[mysqllocalhost]
host = 127.0.0.1
port = 3306
user = root
passwd = xujiang1994323
db = test.txt
chartset = utf8mb4


[mysqlfdfs]
host = xujiang5.xicp.io
port = 3307
user = root
passwd = xujiang1994323
db = fdfs
chartset = utf8

"""
import configparser
# 读取配置文件
import sys
import traceback
import warnings
from abc import ABCMeta, abstractmethod
from collections import OrderedDict
from configparser import DEFAULTSECT


class ConfigParserMoudle():
    """
    config 解析的默认参数 防止以后需要使用 现在全部使用默认
    """

    def __init__(self):
        self.defaults = None
        self.allow_no_value = False
        self.delimiters = ('=', ':')
        self.comment_prefixes = ('#', ';')
        self.inline_comment_prefixes = None
        self.strict = True
        self.empty_lines_in_values = True
        self.default_section = DEFAULTSECT

    def to_dict(self):
        return self.__dict__

    def __str__(self):
        return str(self.__dict__)


class ConfigParserBuilderAbstract:
    __metaclass__ = ABCMeta

    @abstractmethod
    def build_defaults(self):
        pass

    @abstractmethod
    def build_allow_no_value(self):
        pass

    @abstractmethod
    def build_delimiters(self):
        pass

    @abstractmethod
    def build_comment_prefixes(self):
        pass

    @abstractmethod
    def use_inline_comment_prefixes(self):
        pass

    @abstractmethod
    def build_strict(self):
        pass

    @abstractmethod
    def use_empty_lines_in_values(self):
        pass

    @abstractmethod
    def build_default_section(self):
        pass

    @abstractmethod
    def get_moudle(self):
        pass


default_config_parser_moudle = ConfigParserMoudle()


class MyParser(configparser.ConfigParser):
    """
    继承了ConfigParser 方便以后重写
    """

    def __init__(self, configmoudle: ConfigParserMoudle):
        super(MyParser, self).__init__(**configmoudle.to_dict())


class IniConfig(object):

    def __init__(self, configpath=''):
        # 配置文件路径
        self.configpath = configpath
        # 指定的moudle格式 无特殊需求不用传入
        self.moudle = default_config_parser_moudle
        self.keep_keys_case = True
        self.encoding = "utf-8"

    def set_encoding(self, encoding="utf-8"):
        """
        设置读取文件编码
        :param encoding:
        :return:
        """
        self.encoding = encoding
        return self

    def set_keep_keys_case(self, keep_keys_case=True):
        """
        保持option的大小写
        :return:
        """
        self.keep_keys_case = keep_keys_case
        return self

    def set_config_path(self, configPath):
        """
        设置config文件路径
        :param configPath:
        :return:
        """
        self.configpath = configPath
        return self

    def set_configmoudle(self, configmoudle: ConfigParserMoudle):
        """
        设置 modudle,一般情况下不需要传入设置 使用默认设置即可
        :param configmoudle:
        :return:
        """
        self.moudle = configmoudle
        return self

    def read_config(self):
        """
        读取配置文件 这样cf本身就是一个字典
        :param encoding:
        :param configPath:
        :return:
        """
        assert self.cf, AttributeError("还没有调用get_configparser为其赋值 请先调用该函数")
        try:
            self.cf.read(self.configpath, encoding=self.encoding)
        except:
            print('读取配置失败:' + traceback.format_exc())
            sys.exit(-1)
        return self

    def read_config_string(self):
        """
        读取配置文件 将文件读成一个string传入
        :param cfstr:
        :return:
        """
        assert self.cf, AttributeError("还没有调用get_configparser为其赋值 请先调用该函数")
        try:
            with open(self.configpath, mode='rb') as f:
                content = f.read()
                if content.startswith(b'\xef\xbb\xbf'):  # 去掉 utf8 bom 头
                    content = content[3:]
            self.cf.read_string(content.decode(self.encoding))
        except:
            print('读取配置失败:' + traceback.format_exc())
            sys.exit(-1)
        return self

    def builder(self, is_read_str=False):
        self.cf = MyParser(self.moudle)
        if self.keep_keys_case:
            assert self.cf, AttributeError("还没有调用get_configparser为其赋值 请先调用该函数")
            self.cf.optionxform = str
        if is_read_str:
            self.read_config_string()
        else:
            self.read_config()
        return self

    def get_cf(self):
        """
        获取config的对象对其操作
        :return:
        """
        assert self.cf, AttributeError("还没有调用get_configparser为其赋值 请先调用该函数")
        return self.cf

    def get_all_sections(self) -> list:
        """
        传入参数为configparser.ConfigParser
        返回为 list
        该函数得到所有sections 即配置文件中  [mysqlfdfs] 这种
        是配置文件的一级参数
        :param cf:
        :return:
        """
        assert self.cf, AttributeError("还没有调用get_configparser为其赋值 请先调用该函数")
        secs = self.cf.sections()
        if not secs:
            warnings.warn("sections is null,maybe your are cionfig path is wrong")
        return secs

    def get_sesc_options(self, sesc_str: str) -> list:
        """
        返回为 list
        该函数得到指定sections的options
        像 host 这种
        是配置文件的一级参数
        :param sesc_str:
        :return:
        """
        assert self.cf, AttributeError("还没有调用get_configparser为其赋值 请先调用该函数")
        opts = self.cf.options(sesc_str)
        if not opts:
            warnings.warn("opts is null,maybe your are sesc_str is wrong")
        return opts

    def get_items(self, sesc: str):
        """
        :return: [('host', '127.0.0.1'), ('port', '3306'), ('user', 'root'), ('passwd', 'xujiang1994323'), ('db', 'test.txt'), ('chartset', 'utf8mb4')]
        """
        assert self.cf, AttributeError("还没有调用get_configparser为其赋值 请先调用该函数")
        kvs = self.cf.items(sesc)
        return kvs

    def get_value(self, sec_str: str, opt_key: str) -> str:
        """
        获取值 str
        :param cf:
        :param sec_str:
        :param opt_key:
        :return:
        """
        assert self.cf, AttributeError("还没有调用get_configparser为其赋值 请先调用该函数")
        str_value = self.cf.get(sec_str, opt_key)
        return str_value

    def get_value_int(self, sec_str: str, opt_key: str) -> int:
        """
        获取配置文件的值按Int形式
        :param cf:
        :param sec_str:
        :param opt_key:
        :return:
        """
        assert self.cf, AttributeError("还没有调用get_configparser为其赋值 请先调用该函数")
        int_value = self.cf.getint(sec_str, opt_key)
        return int_value

    def set_value(self, sec_str: str, opt_key: str, opt_value: str, filePath: str):
        """
        设置或者更新值
        :param cf:
        :param sec_str:
        :param opt_key:
        :param opt_value:
        :return:
        """
        assert self.cf, AttributeError("还没有调用get_configparser为其赋值 请先调用该函数")
        self.cf.set(sec_str, opt_key, opt_value)
        self.cf.write(open(filePath, "w"))

    def add_new_section(self, secs: str, filePath: str):
        """
        设置section
        :param secs:
        :param filePath:
        :return:
        """
        assert self.cf, AttributeError("还没有调用get_configparser为其赋值 请先调用该函数")
        self.cf.add_section(secs)
        self.cf.write(open(filePath, "w"))

    def get_config_dict(self) -> OrderedDict:
        """
        读取文件转dict
        :param cf:
        :return:
        """
        assert self.cf, AttributeError("还没有调用get_configparser为其赋值 请先调用该函数")
        d = OrderedDict(self.cf._sections)
        for k in d:
            d[k] = OrderedDict(d[k])
        return d
