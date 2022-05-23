import configparser
import os
from lxml import etree

from common.config.config import CONFIG_INI_PATH
from common.file.handle_system import adjust_path

def get_ini_data(filePath,section, name):
    """
    获取ini文件数据
    :param filePath:
    :return:
    """
    _path = adjust_path(filePath)
    if not os.path.exists(_path):
        raise FileNotFoundError("No such file: config.ini")
    _config = configparser.ConfigParser()
    _config.read(_path, encoding='utf-8-sig')
    return _config.get(section, name)


def get_data(name):
    _temp=get_common_data(name)
    if len(_temp)>0:
        return _temp
    else:
        return get_api_data(name)

def get_ini_data(section, name):
    """
        获取ini文件数据
        :param filePath:
        :return:
        """
    _path = adjust_path(CONFIG_INI_PATH)
    if not os.path.exists(_path):
        raise FileNotFoundError("No such file: config.ini")
    _config = configparser.RawConfigParser()
    _config.read(_path, encoding='utf-8-sig')
    return _config.get(section,name)

def get_common_data(name):
    """
        获取COMMON文件数据
        :param filePath:
        :return:
        """
    _path = CONFIG_INI_PATH
    if not os.path.exists(_path):
        raise FileNotFoundError("No such file: config.ini")
    _config = configparser.RawConfigParser()
    _config.read(_path, encoding='utf-8-sig')
    return _config.get("common",name)

def get_item(section):
    _path = CONFIG_INI_PATH
    if not os.path.exists(_path):
        raise FileNotFoundError("No such file: config.ini")
    _config = configparser.RawConfigParser()
    _config.read(_path, encoding='utf-8-sig')
    return _config.items(section)


def get_api_data(name):
    """
        获取API文件数据
        :param filePath:
        :return:
        """
    _path = CONFIG_INI_PATH
    if not os.path.exists(_path):
        raise FileNotFoundError("No such file: config.ini")
    _config = configparser.RawConfigParser()
    _config.read(_path, encoding='utf-8-sig')
    return _config.get("api_path",name)


def get_xml_data(fileName):
    """
    获取XML文件
    :param fileName:
    :return:
    """
    _filePath = adjust_path(fileName)
    _data = etree.parse(_filePath)
    return _data

if __name__ == '__main__':
     print(os.path.dirname(os.path.abspath("..")))


