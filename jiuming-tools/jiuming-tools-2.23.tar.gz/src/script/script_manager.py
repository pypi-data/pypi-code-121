import copy
import os
import pathlib
import stat
import time

import click
import yaml

from src.config.global_config import config_default_file, script_default_file

script_config_default_file = config_default_file + '/script_config.yaml'


def script_create(type, name, remark):
    """
        添加服务配置
        :param type: 脚本类型名称
        :param name: 服务器名称
        :param remark: 脚本备注
        :return:
        """
    # 追加模式
    s_file_path = script_default_file + '/{}'.format(name)
    if os.path.exists(s_file_path):
        click.echo("{}已存在!".format(name))
        return
    y_file = open(script_config_default_file, 'a+')
    sc = ScriptConfig(type=type, name=name, remark=remark, path=s_file_path)
    yaml.safe_dump([sc.__dict__], y_file)
    s_file = open(s_file_path, 'w+')
    write_str = """#!/usr/bin/env {} 
#author ming 
#创建时间:{} 
#{}
""".format(type, time.strftime('%Y-%m-%d %H:%M:%S'), remark)
    s_file.write(write_str)
    s_file.close()
    os.chmod(s_file_path, stat.S_IRWXU)
    os.system('vi {}'.format(s_file_path))


def script_remove(name):
    """
    删除服务器配置信息
    获取所有配置  删除其中name符合的数据
    :param name: 服务器名称
    :return:
    """
    y_read_file = open(script_config_default_file, 'r')
    config_list = yaml.safe_load(y_read_file)
    if config_list is None:
        click.echo("暂无脚本!")
        return
    # 深拷贝 配置列表 进行操作列表
    new_config_list = copy.deepcopy(config_list)
    for c in config_list:
        sc = ScriptConfig.to_obj(c)
        if sc.name == name:
            new_config_list.remove(c)
            os.remove(sc.path)
            click.echo("删除{}脚本".format(sc.name))
    # 重新打开链接
    if len(new_config_list) != 0:
        yaml.safe_dump(new_config_list, open(script_config_default_file, 'w+'))
    else:
        # 清空配置
        open(script_config_default_file, 'w+').truncate()
        click.echo("脚本已清空!")


def script_list():
    config_file = pathlib.Path(script_config_default_file)
    if not config_file.exists():
        click.echo("暂无脚本！")
        return
    if not config_file.is_file():
        click.echo("{}不是配置文件".format(script_config_default_file))
        return
    y_read_file = open(script_config_default_file, 'r')
    config_list = yaml.safe_load(y_read_file)
    if config_list is None:
        click.echo("暂无脚本!")
        return
    config_str = '脚本列表信息:\n'
    for index, c in enumerate(config_list):
        sc = ScriptConfig.to_obj(c)
        config_str += '第{}个脚本名称:{},执行引擎:{},备注:{},脚本地址:{}'.format(index + 1, sc.name, sc.type, sc.remark, sc.path) + '\n'
    config_str += "\n共{}脚本\n".format(len(config_list))
    click.echo(config_str)


def script_details(name):
    y_read_file = open(script_config_default_file, 'r')
    config_list = yaml.safe_load(y_read_file)
    if config_list is None:
        click.echo("暂无脚本!")
        return
    for c in config_list:
        sc = ScriptConfig.to_obj(c)
        if sc.name == name:
            os.system('cat {}'.format(sc.path))


def script_exec(name):
    y_read_file = open(script_config_default_file, 'r')
    config_list = yaml.safe_load(y_read_file)
    if config_list is None:
        click.echo("暂无脚本!")
        return
    for c in config_list:
        sc = ScriptConfig.to_obj(c)
        if sc.name == name:
            start_time = time.perf_counter_ns()
            click.echo(
                click.style("{}脚本开始执行,脚本引擎{},脚本备注:{},脚本地址:{}".format(sc.name, sc.type, sc.remark, sc.path), fg='green'))
            click.echo(click.style("start--------------------------------", fg='green'))
            result = os.system(sc.path)
            end_time = time.perf_counter_ns()
            click.echo(click.style("end--------------------------------", fg='green'))
            click.echo("{}执行耗时:{}ms,结果:{}".format(sc.name, str(
                round((int(round((end_time - start_time) / 1000000))), 2)), str(result)))


class ScriptConfig(object):
    """
    脚本配置 对象
    """
    # 脚本类型  如 sh  bash  python   以linux shell的脚本引擎名称   执行脚本的时候  就是 type ./xxx
    type: str
    # 脚本名称
    name: str
    # 脚本备注
    remark: str
    # 脚本地址
    path: str

    def __init__(self, type, name, remark, path):
        self.type = type
        self.name = name
        self.remark = remark
        self.path = path

    @staticmethod
    def to_obj(d: dict):
        """
        将读取的dict 转换为 serverConfig
        :param d:  dict
        :return: ServerConfig
        """
        return ScriptConfig(type=d['type'], name=d['name'],
                            remark=d['remark'], path=d['path'])
