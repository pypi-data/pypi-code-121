# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-08-03 10:43:58
@LastEditTime: 2022-03-11 11:10:29
@LastEditors: HuangJianYi
@Description: 应用模块
"""
from seven_cloudapp_frame.handlers.frame_base import *
from seven_cloudapp_frame.models.top_base_model import *
from seven_cloudapp_frame.models.app_base_model import *
from seven_cloudapp_frame.models.mp_base_model import *
from asq.initiators import query


class InstantiateAppHandler(ClientBaseHandler):
    """
    :description: 实例化小程序
    """
    def get_async(self):
        """
        :description: 实例化小程序
        :param app_id:应用标识
        :param user_nick:用户昵称
        :param access_token:access_token
        :param is_log：是否记录返回信息
        :return app_info
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        user_nick = self.get_user_nick()
        access_token = self.get_access_token()
        is_log = int(self.get_param("is_log", 0))
        is_log = True if is_log == 1 else False

        cache_key = f"instantiate:{user_nick}"
        if SevenHelper.is_continue_request(cache_key, 10000) == True:
            return self.response_json_error("error","操作太频繁,请10秒后再试")
        invoke_result_data = self.business_process_executing()
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message,invoke_result_data.data)
        app_key, app_secret = self.get_app_key_secret()
        top_base_model = TopBaseModel(context=self)
        invoke_result_data = top_base_model.instantiate(app_id, user_nick, access_token, app_key, app_secret, is_log)
        if invoke_result_data.success == False:
            SevenHelper.redis_init().delete(cache_key)
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message,invoke_result_data.data)
        ref_params = {}
        invoke_result_data = self.business_process_executed(invoke_result_data, ref_params)
        if invoke_result_data.success == False:
            SevenHelper.redis_init().delete(cache_key)
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        SevenHelper.redis_init().delete(cache_key)
        return self.response_json_success(invoke_result_data.data)


class UpdateTelephoneHandler(ClientBaseHandler):
    """
    :description: 更新手机号
    """
    @filter_check_params("telephone")
    def get_async(self):
        """
        :description: 更新手机号
        :param app_id:应用标识
        :param telephone：手机号
        :param check_code：验证码
        :return: 
        :last_editors: HuangJianYi
        """
        open_id = self.get_open_id()
        app_id = self.get_app_id()
        telephone = self.get_param("telephone")
        check_code = self.get_param("check_code")
        modify_date = self.get_now_datetime()

        check_code_re = SevenHelper.redis_init().get("user_" + open_id + "_bind_phone_code")
        if check_code_re == None:
            return self.response_json_error("error", "验证码已过期")
        check_code_re = str(check_code_re, 'utf-8')
        if check_code != check_code_re:
            return self.response_json_error("error", "验证码错误")
        AppInfoModel(context=self).update_table("app_telephone=%s,modify_date=%s", "app_id=%s", [telephone, modify_date, app_id])
        return self.response_json_success()


class VersionUpgradeHandler(ClientBaseHandler):
    """
    :description: 前端版本更新
    """
    def get_async(self):
        """
        :description: 前端版本更新
        :param app_id:应用标识
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        access_token = self.get_access_token()
        user_nick = self.get_user_nick()
        is_log = int(self.get_param("is_log", 0))
        is_log = True if is_log == 1 else False

        base_info = BaseInfoModel(context=self).get_entity()
        client_ver = base_info.client_ver

        #中台指定账号升级
        version_info = VersionInfoModel(context=self).get_entity(where="type_id=1",order_by="id desc")
        if version_info:
            if version_info.update_scope == 2 and version_info.white_lists:
                white_lists = list(set(str(version_info.white_lists).split(',')))
                if user_nick in white_lists:
                    client_ver = version_info.version_number

        app_info = AppInfoModel(context=self).get_entity("app_id=%s", params=app_id)
        if not app_info:
            return self.response_json_error("no_app", "小程序不存在")
        test_config = config.get_value("test_config",{})
        test_client_ver = test_config.get("client_ver","")
        client_template_id = config.get_value("client_template_id")
        #配置文件指定账号升级
        store_user_nick = user_nick.split(':')[0]
        if test_client_ver and store_user_nick and store_user_nick == test_config.get("user_nick",""):
            client_ver = test_client_ver
        top_base_model = TopBaseModel(context=self)
        app_key, app_secret = self.get_app_key_secret()
        invoke_result_data = top_base_model.version_upgrade(app_id, client_template_id, client_ver, access_token,app_key, app_secret, app_info, is_log)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)


class AppInfoHandler(ClientBaseHandler):
    """
    :description: 获取小程序信息
    """
    @filter_check_params()
    def get_async(self):
        """
        :description: 获取小程序信息
        :return app_info
        :last_editors: HuangJianYi
        """
        app_base_model = AppBaseModel(context=self)
        app_key, app_secret = self.get_app_key_secret()
        invoke_result_data = app_base_model.get_app_info_result(self.get_user_nick(), self.get_open_id(), self.get_access_token(), app_key, app_secret)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)


class CheckGmPowerHandler(ClientBaseHandler):
    """
    :description: 校验是否有GM工具权限
    """
    def get_async(self):
        """
        :description: 校验是否有GM工具权限
        :param 
        :return: True是 False否
        :last_editors: HuangJianYi
        """
        is_power = False
        user_nick = self.get_user_nick()
        if not user_nick:
            return self.response_json_error("error", "对不起,请先授权登录")
        store_user_nick = user_nick.split(':')[0]
        app_info_dict = AppInfoModel(context=self).get_dict("store_user_nick=%s", field="is_gm", params=store_user_nick)
        if not app_info_dict:
            is_power = False
        if app_info_dict["is_gm"] == 1:
            is_power = True
        return self.response_json_success(is_power)


class GetAppidByGmHandler(ClientBaseHandler):
    """
    :description: GM工具获取应用标识
    """
    @filter_check_params("store_name")
    def get_async(self):
        """
        :description: 获取应用标识
        :param store_name:店铺名称
        :return app_id
        :last_editors: HuangJianYi
        """
        app_id = ""
        store_name = self.get_param("store_name")
        user_nick = self.get_user_nick()
        if not user_nick:
            return self.response_json_error("error", "对不起,请先授权登录")
        store_user_nick = user_nick.split(':')[0]
        is_power = False
        
        app_info_dict = AppInfoModel(context=self).get_dict("store_user_nick=%s", field="is_gm", params=store_user_nick)
        if app_info_dict and app_info_dict["is_gm"] == 1:
            is_power = True
        if is_power == True:
            app_info_dict = AppInfoModel(context=self).get_dict("store_name=%s", field="app_id", params=[store_name])
            if app_info_dict:
                app_id = app_info_dict["app_id"]
        return self.response_json_success(app_id)


class GetShortUrlHandler(ClientBaseHandler):
    """
    :description: 获取淘宝短链接
    """
    def get_async(self):
        """
        :description: 获取淘宝短链接
        :param url:链接地址
        :return: 
        :last_editors: HuangJianYi
        """
        access_token = self.get_access_token()
        is_log = int(self.get_param("is_log", 0))
        is_log = True if is_log == 1 else False
        url = self.get_param("url")
        app_key, app_secret = self.get_app_key_secret()
        top_base_model = TopBaseModel(context=self)
        app_key, app_secret = self.get_app_key_secret()
        invoke_result_data = top_base_model.get_short_url(url, access_token, app_key, app_secret, is_log)
        if invoke_result_data.success == False:
            return self.response_json_success("")
        else:
            return self.response_json_success(invoke_result_data.data)


class GetHighPowerListHandler(ClientBaseHandler):
    """
    :description: 获取中台配置的高级权限列表
    """
    def get_async(self):
        """
        :description: 获取中台配置的高级权限列表
        :return: list
        :last_editors: HuangJianYi
        """
        user_nick = self.get_user_nick()
        if not user_nick:
            return self.response_json_error("Error", "对不起,请先授权登录")
        store_user_nick = user_nick.split(':')[0]
        access_token = self.get_access_token()
        top_base_model = TopBaseModel(context=self)
        mp_base_model = MPBaseModel(context=self)
        custom_function_list = mp_base_model.get_custom_function_list(store_user_nick)
        config_data_list = []
        if len(custom_function_list) == 0:
            config_data = {}
            config_data["is_customized"] = 0
            config_data["name"] = ""
            config_data["project_code"] = ""
            config_data["cloud_app_id"] = 0
            config_data["function_config_list"] = []
            config_data["skin_config_list"] = []
            app_key, app_secret = self.get_app_key_secret()
            #获取项目编码
            project_code = top_base_model.get_project_code(store_user_nick, access_token, app_key, app_secret)
            public_function_list = mp_base_model.get_public_function_list(project_code)
            if len(public_function_list) > 0:
                config_data["function_config_list"] = query(public_function_list[0]["function_info_second_list"]).select(lambda x: {"name": x["name"], "key_name": x["key_name"]}).to_list()
                config_data["skin_config_list"] = query(public_function_list[0]["skin_ids_second_list"]).select(lambda x: {"name": x["name"], "theme_id": x["theme_id"]}).to_list()
                config_data["name"] = public_function_list[0]["name"]
                config_data["project_code"] = public_function_list[0]["project_code"]
            config_data_list.append(config_data)
        else:
            for custom_function in custom_function_list:
                config_data = {}
                config_data["is_customized"] = 1
                config_data["name"] = "定制版"
                config_data["project_code"] = ""
                config_data["cloud_app_id"] = custom_function["cloud_app_id"]
                config_data["function_config_list"] = query(custom_function["function_info_second_list"]).select(lambda x: {"name": x["name"], "key_name": x["key_name"]}).to_list()
                config_data["skin_config_list"] = query(custom_function["skin_ids_second_list"]).select(lambda x: {"name": x["name"], "theme_id": x["theme_id"]}).to_list()
                config_data["module_name"] = custom_function["module_name"]
                config_data["module_pic"] = custom_function["module_pic"]
                config_data_list.append(config_data)
        self.response_json_success(config_data_list)