# -*- coding: utf-8 -*-
import json
import os

from .log import i, e
from .utils import encrypt

CONFIG_FILE = "pcs-get.cfg"
K_USER = "user"
K_PW = "password"
K_LANG = "lang"
K_SESSION = "session"
K_TOKEN = "token"
K_DEBUG = "debug"
SUPPORTED_KEY = [K_USER, K_PW, K_LANG, K_SESSION, K_TOKEN, K_DEBUG]


def setup_config(key, value):
    """
    :type key: str
    :type value: str
    """
    if len(value) == 0:
        e("--set with empty-str param is illegal!")
        return
    if key not in SUPPORTED_KEY:
        e("--set for %s is not supported!" % key)
        return
    if key == K_LANG and (value != "java" and value != "kotlin"):
        e("%s is illegal lang now! [java, kotlin]" % value)
        return
    d = {key: value}
    update_config(**d)


def read_config():
    # 读取配置（用户目录下脚本目录）
    try:
        with open(_get_config_file_path(), 'r', encoding='UTF-8') as fp:
            return json.load(fp)
    except IOError as e:
        return {K_USER: '', K_PW: '', K_SESSION: '', K_LANG: 'java', K_DEBUG: False}


def is_debug_mode():
    cfg = read_config()
    return K_DEBUG in cfg and cfg[K_DEBUG]


def update_config(**kw):
    """
    保存配置项
    """
    actual_updated = False
    curr_cfg_json = read_config()
    if K_USER in kw:
        curr_cfg_json[K_USER] = kw[K_USER]
        actual_updated = True
    if K_PW in kw:
        pw = kw[K_PW]
        encrypted_pw = encrypt(pw)
        curr_cfg_json[K_PW] = encrypted_pw
        actual_updated = True
    if K_LANG in kw:
        curr_cfg_json[K_LANG] = kw[K_LANG]
        actual_updated = True
    if K_SESSION in kw:
        curr_cfg_json[K_SESSION] = kw[K_SESSION]
        actual_updated = True
    if K_TOKEN in kw:
        curr_cfg_json[K_TOKEN] = kw[K_TOKEN]
        actual_updated = True
    if K_DEBUG in kw:
        curr_cfg_json[K_DEBUG] = kw[K_DEBUG]
        actual_updated = True

    if actual_updated:
        n_cfg_json = json.dumps(curr_cfg_json)
        with open(_get_config_file_path(), 'w', encoding='UTF-8') as fp:
            fp.write(n_cfg_json)
            i("config for %s was updated!" % str(kw.keys()))
    else:
        e("none config was updated!")


def _get_config_file_path():
    """
    获取配置文件路径
    :rtype str
    """
    user_home = os.path.expanduser("~")
    return os.path.join(user_home, CONFIG_FILE)
