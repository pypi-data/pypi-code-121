import os

import toml


class TomlConfig(object):
    """
    toml 格式的配置文件
    """

    def __init__(self, configfile=""):
        # 配置文件路径
        self.configfile = configfile
        self.content = None

    def set_config_path(self, configfile):
        self.configfile = configfile
        return self

    def read_file_remove_bom(self):
        if not os.path.exists(self.configfile):
            print(self.configfile + ' not found')
            raise FileNotFoundError("配置文件不存在")
        with open(self.configfile, mode='rb') as f:
            content = f.read()
        if content.startswith(b'\xef\xbb\xbf'):  # 去掉 utf8 bom 头
            content = content[3:]
        self.content = content
        return self

    def get_dicts(self, encoding="utf8"):
        """
        加载后是一个doc的形式
        :param content:
        :param encoding:
        :return:
        """
        dic = toml.loads(self.content.decode(encoding))
        return dic

    def get_config_dicts(self, encoding="utf8"):
        """
        加载后是一个doc的形式
        :param content:
        :param encoding:
        :return:
        """
        self.read_file_remove_bom()
        return self.get_dicts()
