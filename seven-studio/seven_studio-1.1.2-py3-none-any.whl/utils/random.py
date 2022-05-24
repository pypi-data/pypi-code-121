# -*- coding: utf-8 -*-
"""
:Author: ChenXiaolei
:Date: 2020-12-07 19:13:46
:LastEditTime: 2020-12-07 19:14:06
:LastEditors: ChenXiaolei
:Description: 
"""
import random
class RandomUtil:
    @classmethod
    def get_random_switch_string(self, random_str, split_chars=","):
        """
        :description: 随机取得字符串
        :param trimChars：根据什么符号进行分割
        :return: 随机字符串
        :last_editors: HuangJingCan
        """
        if random_str == "":
            return ""
        random_list = [i for i in random_str.split(split_chars) if i != ""]
        return random.choice(random_list)