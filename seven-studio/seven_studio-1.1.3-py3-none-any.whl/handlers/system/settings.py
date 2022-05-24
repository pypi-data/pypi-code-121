# -*- coding: utf-8 -*-
"""
:Author: ChenXiaolei
:Date: 2020-12-09 19:11:51
:LastEditTime: 2020-12-25 10:04:04
:LastEditors: ChenXiaolei
:Description: 
"""

from seven_studio.handlers.studio_base import *
from seven_studio.models.db_models.settings.settings_base_model import *


class BaseSettingsHandler(StudioBaseHandler):
    @login_filter(True)
    def post_async(self):
        """
        :description: 设置站点基础信息
        :return 基础信息
        :last_editors: ChenXiaolei
        """
        login_background = self.get_param("login_background")
        login_logo = self.get_param("login_logo")
        banner_logo = self.get_param("banner_logo")
        title = self.get_param("title")

        settings_base = SettingsBaseModel().get_entity("")

        if not settings_base:
            settings_base = SettingsBase()

        settings_base.login_background = login_background
        settings_base.login_logo = login_logo
        settings_base.banner_logo = banner_logo
        settings_base.title = title

        if settings_base.id > 0:
            SettingsBaseModel().update_entity(settings_base)
        else:
            SettingsBaseModel().add_entity(settings_base)

        return self.reponse_json_success(settings_base)

    def get_async(self):
        """
        :description: 获取站点基础信息
        :return 基础信息
        :last_editors: ChenXiaolei
        """
        settings_base = SettingsBaseModel().get_dict("")

        if not settings_base:
            return self.reponse_json_success(None)

        return self.reponse_json_success(settings_base)
