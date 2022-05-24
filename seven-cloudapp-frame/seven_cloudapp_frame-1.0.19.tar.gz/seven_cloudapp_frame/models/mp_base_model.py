# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-12-20 16:07:52
@LastEditTime: 2022-03-09 18:23:03
@LastEditors: HuangJianYi
@Description: 中台接口相关处理业务模型
"""
from seven_framework import *

from seven_cloudapp_frame.libs.customize.seven_helper import SevenHelper

class MPBaseModel():
    """
    :description: 中台接口相关处理业务模型
    """
    def __init__(self, context=None, logging_error=None, logging_info=None):
        self.context = context
        self.logging_link_error = logging_error
        self.logging_link_info = logging_info

    def get_public_function_list(self, project_code):
        """
        :description:  获取公共功能列表
        :param project_code:收费项目代码（服务管理-收费项目列表）
        :return list: 
        :last_editors: HuangJianYi
        """

        public_function_list = []
        if not project_code:
            return public_function_list
        #产品id
        product_id = config.get_value("project_name")
        if not product_id:
            return public_function_list
        requst_url = config.get_value("mp_url","http://taobao-mp-s.gao7.com") + "/general/project_code_list"
        data = {}
        data["project_code"] = project_code
        data["product_id"] = product_id
        result = HTTPHelper.get(requst_url, data, {"Content-Type": "application/json"})
        if result and result.ok and result.text:
            obj_data = SevenHelper.json_loads(result.text)
            public_function_list = obj_data["Data"]
        return public_function_list

    def get_custom_function_list(self, store_user_nick):
        """
        :description:  获取定制功能列表
        :param store_user_nick:商家主账号昵称
        :return list: 
        :last_editors: HuangJianYi
        """
        custom_function_list = []
        #产品id
        product_id = config.get_value("project_name")
        if not product_id:
            return custom_function_list
        requst_url = config.get_value("mp_url", "http://taobao-mp-s.gao7.com") + "/custom/query_skin_managemen_list"
        data = {}
        data["product_id"] = product_id
        data["store_user_nick"] = store_user_nick
        result = HTTPHelper.get(requst_url, data, {"Content-Type": "application/json"})
        if result and result.ok and result.text:
            obj_data = SevenHelper.json_loads(result.text)
            custom_function_list = obj_data["Data"]
        return custom_function_list
    
    def get_key_power_list(self, store_user_nick, project_code, key_names,user_type=0):
        """
        :description:  指定模块权限列表
        :param store_user_nick:商家主账号昵称
        :param project_code:项目编码
        :param key_names:权限代码，多个逗号分隔
        :param user_type:0-不限1-SAAS用户2-SAAS定制用户
        :return list: 
        :last_editors: HuangJianYi
        """
        power_list = []
        #产品id
        product_id = config.get_value("project_name")
        if not product_id:
            return power_list
        requst_url = config.get_value("mp_url", "http://taobao-mp-s.gao7.com") + "/general/jurisdiction_list"
        data = {}
        data["product_id"] = product_id
        data["project_code"] = project_code
        data["store_user_nick"] = store_user_nick
        data["key_name"] = key_names
        if user_type > 0:
            data["user_type"] = user_type
        result = HTTPHelper.get(requst_url, data, {"Content-Type": "application/json"})
        if result and result.ok and result.text:
            obj_data = SevenHelper.json_loads(result.text)
            power_list = obj_data["Data"]
        return power_list
    
    def check_high_power(self, store_user_nick, project_code, key_names,user_type=0):
        """
        :description:  检验是否有指定模块的权限
        :param store_user_nick:商家主账号昵称
        :param project_code:项目编码
        :param key_names:权限代码，多个逗号分隔
        :param user_type:0-不限1-SAAS用户2-SAAS定制用户
        :return bool: 是否有权限
        :last_editors: HuangJianYi
        """
        power_list = self.get_key_power_list(store_user_nick, project_code, key_names, user_type)
        is_power = True    
        for key in power_list:
            if key["is_power"] == False:
                is_power = False
                break
        return is_power