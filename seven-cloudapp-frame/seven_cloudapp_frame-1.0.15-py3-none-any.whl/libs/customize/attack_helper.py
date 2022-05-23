# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-10-22 13:32:07
@LastEditTime: 2022-02-21 11:16:39
@LastEditors: HuangJianYi
@Description: 
"""
import re

class AttackHelper:
    """
    :description:攻击帮助类
    """

    #sql关键字
    _sql_pattern_key = r"\b(and|like|exec|execute|insert|create|select|drop|grant|alter|delete|update|asc|count|chr|mid|limit|union|substring|declare|master|truncate|char|delclare|or)\b|(\*|;)"
    #Url攻击正则
    _url_attack_key = r"\b(alert|xp_cmdshell|xp_|sp_|restore|backup|administrators|localgroup)\b"

    @classmethod
    def is_contain_sql(self, str):
        """
        :description: 是否包含sql关键字
        :param str:参数值
        :return:
        :last_editors: HuangJianYi
        """
        result = re.search(self._sql_pattern_key, str.lower())
        if result:
            return True
        else:
            return False

    @classmethod
    def filter_routine_key(self, key):
        """
        :description: 过滤常规字符
        :param key:参数值
        :return:
        :last_editors: HuangJianYi
        """
        routine_key_list = ["\u200b"]
        if not isinstance(key, str):
            return key
        for item in routine_key_list:
            key = key.replace(item, "")
        return key

    @classmethod
    def filter_sql(self, key):
        """
        :description: 过滤sql关键字
        :param key:参数值
        :return:
        :last_editors: HuangJianYi
        """
        if not isinstance(key, str):
            return key
        result = re.findall(self._sql_pattern_key, key.lower())
        for item in result:
            key = key.replace(item[0], "")
            key = key.replace(item[0].upper(), "")
        return key

    @classmethod
    def filter_special_key(self, key):
        """
        :description: 过滤sql特殊字符
        :param key:参数值
        :return:
        :last_editors: HuangJianYi
        """
        if not isinstance(key, str):
            return key
        special_key_list = ["\"", "\\", "/", "*", "'", "=", "-", "#", ";", "<", ">", "+", "%", "$", "(", ")", "%", "@","!"]
        for item in special_key_list:
            key = key.replace(item, "")
        return key

    @classmethod
    def is_attack(self, str):
        """
        :description: 处理攻击请求
        :param str:当前请求地址
        :return:
        :last_editors: HuangJianYi
        """
        if ":" in str:
            return True
        result = re.search(self._url_attack_key, str.lower())
        if result:
            return True
        else:
            return False
    
