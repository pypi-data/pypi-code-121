# -*- encoding: utf-8 -*-
"""
@Author  : zh_o
"""
import os
from typing import Text, Dict
import yaml
from melon import ROOT_DIR, CONFIG_PATH


def __read_yaml(yaml_path: Text) -> Dict:
    """读取yaml文件"""
    with open(yaml_path, encoding='UTF-8') as file:
        contents = yaml.load(file, yaml.FullLoader)
    return contents


def __load():
    """加载配置文件"""
    contents = __read_yaml(CONFIG_PATH)
    active_profile = contents.get('melon', {}).get('profiles', {}).get('active', '')
    if not active_profile:
        return contents

    active_profile_path = os.path.join(ROOT_DIR, f'melon-{active_profile}.yaml')
    profile_contents = __read_yaml(active_profile_path)

    __append(contents, profile_contents)
    return contents


def __append(base_content, append_content):
    """追加配置内容"""
    for k, v in append_content.items():
        if type(v) != dict or k not in base_content.keys():
            base_content[k] = v
            continue
        # 递归追加
        __append(base_content[k], v)


config = __load()


def get_config(keys_str: Text, default=None):
    """获取配置内容"""
    target = config
    keys = keys_str.split('.')
    for key in keys:
        if not key:
            continue
        target = target.get(key, default)
    return target
