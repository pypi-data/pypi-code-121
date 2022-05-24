# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2020-04-22 14:32:40
:LastEditTime: 2020-12-09 10:27:49
:LastEditors: ChenXiaolei
:Description: 用户信息扩展类
"""

from seven_studio.models.db_models.user.user_info_model import *
from seven_framework.crypto import *


class UserInfoModelEx(UserInfoModel):
    def __init__(self, db_connect_key='db_sevenstudio', sub_table=None, db_transaction=None):
        super().__init__(db_connect_key=db_connect_key, sub_table=sub_table)
    def sign_password(self, login_password="", userid=""):
        if login_password.strip() == '':
            return CryptoHelper.md5_encrypt(config.get_value("default_password"), userid)
        return CryptoHelper.md5_encrypt(login_password, userid).upper()

    def verify_password(self, login_password="", password="", userid=""):
        return password.upper() == CryptoHelper.md5_encrypt(login_password, userid).upper()

    def is_force_password(self, user_info):
        if user_info:
            return self.verify_password(config.get_value("default_password"), user_info.Password, user_info.UserID)
        return False
