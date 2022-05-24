import copy
import os
import pathlib

import click
import yaml

from src.config.global_config import config_default_file

# 默认配置file
server_config_default_file = config_default_file + '/server_config.yaml'


def create(sc):
    y_file = open(server_config_default_file, 'a+')
    yaml.safe_dump([sc.__dict__], y_file)


def edit():
    click.edit(filename=server_config_default_file)


def remove_by_name(name):
    name = name.strip()
    sc_list = find_all()
    if sc_list is None:
        return None
    # 深拷贝 配置列表 进行操作列表
    new_sc_list = copy.deepcopy(sc_list)
    for index, sc in enumerate(sc_list):
        if sc.name == name:
            new_sc_list.remove(new_sc_list[index])
            if sc.secret_key_path is not None:
                os.remove(sc.secret_key_path)
            click.echo("删除{}服务器".format(sc.name))
    # 重新打开链接
    if len(new_sc_list) != 0:
        dict_list = []
        for sc in new_sc_list:
            dict_list.append(sc.__dict__)
        yaml.safe_dump(dict_list, open(server_config_default_file, 'w+'))
    else:
        # 清空配置
        open(server_config_default_file, 'w+').truncate()
        click.echo("服务器配置已清空!")


def find_by_name(name):
    name = name.strip()
    sc_list = find_all()
    if sc_list is None:
        return None
    for sc in sc_list:
        if name == sc.name:
            return sc
    return None


def find_all():
    config_file = pathlib.Path(server_config_default_file)
    if not config_file.exists():
        click.echo("暂无服务器配置信息！")
        return None
    if not config_file.is_file():
        click.echo("{}不是配置文件".format(server_config_default_file))
        return None
    config_list = yaml.safe_load(open(server_config_default_file, 'r'))
    if config_list is None:
        click.echo("暂无服务器配置信息!")
        return None
    result = []
    for c in config_list:
        result.append(ServerConfig.to_obj(c))
    return result


class ServerConfig(object):
    """
    服务器配置模板class
    """
    # 名字
    name: str
    # 地址
    host: str
    # ssh端口
    port: int
    # 服务器用户名
    username: str
    # 密码
    password: str
    # 密钥位置
    secret_key_path: str

    def __init__(self, name, host, port, username, password, secret_key_path):
        self.name = name
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.secret_key_path = secret_key_path

    @staticmethod
    def to_obj(d: dict):
        """
        将读取的dict 转换为 serverConfig
        :param d:  dict
        :return: ServerConfig
        """
        return ServerConfig(name=d['name'], host=d['host'], port=d['port'], username=d['username'],
                            password=d['password'], secret_key_path=d.get('secret_key_path', None))
