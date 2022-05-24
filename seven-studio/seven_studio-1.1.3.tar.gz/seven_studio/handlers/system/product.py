# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2020-04-22 14:32:40
:LastEditTime: 2020-12-10 10:14:37
:LastEditors: ChenXiaolei
:Description: 产品相关Handler
"""

from seven_studio.handlers.studio_base import *
from seven_studio.models.db_models.product.product_info_model import *
from seven_studio.models.db_models.product.product_user_model import *


class GetProductListHandler(StudioBaseHandler):
    """
    :description: 产品列表
    """
    @login_filter(True)
    @power_filter(True)
    def post_async(self):
        """
        :description: 产品列表
        :param {type} 
        :return: 
        :last_editors: HuangJingCan
        """
        product_info_model = ProductInfoModel(
            config.get_value("base_manage_context_key"))
        page_index = self.get_page_index()
        page_size = self.get_page_size()
        condition, order = self.get_condition_by_body()

        source_dict_list = product_info_model.get_dict_list(
            condition, "", order)
        if len(source_dict_list) > 0:
            merge_dict_list = UserInfoModel(
                self.get_manage_context_key()).get_dict_list(
                    field="UserID,UserName")
            source_dict_list = DictUtil.merge_dict_list(
                source_dict_list, "SuperID", merge_dict_list, "UserID",
                "UserID,UserName")
        page_dict = self.get_dict_page_info_list(page_index, page_size,
                                                 source_dict_list)

        self.reponse_json_success(page_dict)


class GetAllProductListHandler(StudioBaseHandler):
    """
    :description: 全部产品列表
    """
    @login_filter(True)
    def get_async(self):
        """
        :description: 全部产品列表
        :param {type} 
        :return: 
        :last_editors: HuangJingCan
        """
        product_info_model = ProductInfoModel(
            config.get_value("base_manage_context_key"))
        source_dict_list = product_info_model.get_dict_list()

        self.reponse_json_success(source_dict_list)


class SaveProductHandler(StudioBaseHandler):
    """
    :description: 保存产品
    """
    @login_filter(True)
    @power_filter(True)
    def post_async(self):
        """
        :description: 保存产品
        :param {type} 
        :return: 
        :last_editors: HuangJingCan
        """
        base_manage_context_key = config.get_value("base_manage_context_key")
        # 获取参数
        product_id = int(self.get_param("ProductID", "0"))
        product_name = self.get_param("ProductName")
        product_sub_name = self.get_param("ProductSubName")
        manage_url = self.get_param("ManageUrl")
        power_url = self.get_param("PowerUrl")
        summary = self.get_param("Summary")
        image_url = self.get_param("ImageUrl")
        super_id = self.get_param("SuperID")
        file_context_key = self.get_param("FileContextKey")
        manage_context_key = self.get_param("ManageContextKey")
        log_context_key = self.get_param("LogContextKey")
        plug_work_context_key = self.get_param("PlugWorkContextKey")
        is_release = int(self.get_param("IsRelease", "0"))
        is_brank = int(self.get_param("IsBrank", "0"))

        # 验证数据
        if product_name == "":
            return self.reponse_common("ProductNameEmpty", "产品名称为空")

        if not config.get_value(manage_context_key):
            return self.reponse_common("HasExit", "ManageContentKey链接字符串未配置")

        product_info_model = ProductInfoModel(base_manage_context_key)
        product_info = ProductInfo()
        if product_id > 0:
            product_info = product_info_model.get_entity_by_id(product_id)
            if not product_info:
                return self.reponse_common("NoExit", "产品不存在")
            if not manage_url == "" or not power_url == "":
                product_info_c = product_info_model.get_entity(
                    "(ManageUrl=%s OR PowerUrl=%s) AND ProductID<>%s",
                    params=[manage_url, power_url, product_id])
                if product_info_c:
                    return self.reponse_common("HasExit", "WebUrl或ApiUrl已存在")
        elif not manage_url == "" or not power_url == "":
            product_info_c = product_info_model.get_entity(
                "ManageUrl=%s OR PowerUrl=%s", params=[manage_url, power_url])
            if product_info_c:
                return self.reponse_common("HasExit", "WebUrl或ApiUrl已存在")

        # 赋值
        product_info.ProductName = product_name
        product_info.ProductSubName = product_sub_name
        product_info.ManageUrl = manage_url
        product_info.PowerUrl = power_url
        product_info.Summary = summary
        product_info.ImageUrl = image_url
        product_info.SuperID = super_id
        product_info.Summary = summary
        product_info.FileContextKey = file_context_key
        product_info.ManageContextKey = manage_context_key
        product_info.LogContextKey = log_context_key
        product_info.PlugWorkContextKey = plug_work_context_key
        product_info.IsRelease = is_release
        product_info.IsBrank = is_brank
        if product_id > 0:
            product_info_model.update_entity(product_info)
        else:
            product_id = product_info_model.add_entity(product_info)
            product_info.ProductID = product_id

        user_info_model = UserInfoModel(manage_context_key)

        user_info_model.update_table("IsSuper=0", "Account<>'seven'")
        user_info_model.update_table("IsSuper=1",
                                     "UserID=%s",
                                     params=[super_id])

        self.reponse_json_success(product_info)


class DeleteProductHandler(StudioBaseHandler):
    """
    :description: 删除产品
    """
    @login_filter(True)
    @power_filter(True)
    def get_async(self):
        """
        :description: 删除产品
        :param {type} 
        :return: 
        :last_editors: HuangJingCan
        """
        product_id = int(self.get_param("ProductID", 0))

        if product_id <= 0:
            return self.reponse_json_error_params()

        product_info_model = ProductInfoModel(
            config.get_value("base_manage_context_key"))

        product_info_model.del_entity("ProductID=%s", product_id)

        self.reponse_json_success()