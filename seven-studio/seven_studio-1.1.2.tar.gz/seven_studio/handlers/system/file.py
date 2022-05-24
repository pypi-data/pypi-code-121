"""
:Author: HuangJingCan
:Date: 2020-03-17 16:12:54
:LastEditTime: 2020-12-25 10:04:37
:LastEditors: ChenXiaolei
:Description: 文件操作相关接口
"""
from seven_studio.handlers.studio_base import *

from seven_studio.models.db_models.file.file_storage_path_model import *
from seven_studio.models.db_models.file.file_resource_model import *
from seven_studio.models.db_models.file.file_restrict_model import *
from seven_studio.models.db_models.file.file_water_image_model import *
from seven_studio.models.db_models.file.file_history_model import *
from seven_studio.models.seven_model import InvokeResult
from seven_studio.libs.file.ks3 import *


class GetStoragePathListHandler(StudioBaseHandler):
    """
    :description: 获取存储配置列表
    """
    @login_filter(True)
    @power_filter(True)
    def post_async(self):
        """
        :description: 获取存储配置列表
        :param {type} 
        :return: 
        :last_editors: HuangJingCan
        """
        file_storage_path_model = FileStoragePathModel(self.get_file_context_key())
        page_index = self.get_page_index()
        page_size = self.get_page_size()
        condition, order = self.get_condition_by_body()

        p_dict, total = file_storage_path_model.get_dict_page_list("*", page_index, page_size, condition, "", order)

        self.reponse_json_success(self.get_dict_page_info_list(page_index, page_size, p_dict, total))


class GetStoragePathDataHandler(StudioBaseHandler):
    """
    :description: 获取存储配置
    :param {type} 
    :return: 
    :last_editors: HuangJingCan
    """
    @login_filter(True)
    @power_filter(True)
    def get_async(self):
        """
        :description: 获取存储配置
        :param {type} 
        :return: 
        :last_editors: HuangJingCan
        """
        file_storage_path_model = FileStoragePathModel(self.get_file_context_key())
        p_dict = file_storage_path_model.get_dict_list("", "FileStoragePathID,StoragePathName")

        self.reponse_json_success(p_dict)


class SaveStoragePathHandler(StudioBaseHandler):
    """
    :description: 保存存储配置
    """
    @login_filter(True)
    @power_filter(True)
    def post_async(self):
        """
        :description: 保存存储配置
        :param {type} 
        :return: 
        :last_editors: HuangJingCan
        """
        # 获取参数
        file_storage_path_id = self.get_param("FileStoragePathID")
        storage_path_name = self.get_param("StoragePathName")
        storage_type_id = int(self.get_param("StorageTypeID", "0"))
        virtual_name = self.get_param("VirtualName")
        storage_path = self.get_param("StoragePath")
        ip_address = self.get_param("IPAddress")
        account = self.get_param("Account")
        password = self.get_param("Password")
        port = self.get_param("Port")
        storage_config = self.get_param("StorageConfig")

        # 验证数据
        if storage_path_name == "":
            return self.reponse_common("StoragePathNameEmpty", "存储名称参数为空")

        file_storage_path_model = FileStoragePathModel(self.get_file_context_key())
        file_storage_path = FileStoragePath()
        if file_storage_path_id != "":
            file_storage_path = file_storage_path_model.get_entity_by_id(file_storage_path_id)
            if not file_storage_path:
                return self.reponse_common("NoExist", "数据不存在")

        # 赋值
        file_storage_path.StoragePathName = storage_path_name
        file_storage_path.StorageTypeID = storage_type_id
        file_storage_path.VirtualName = virtual_name
        file_storage_path.StoragePath = storage_path
        file_storage_path.IPAddress = ip_address
        file_storage_path.Account = account
        file_storage_path.Password = password
        file_storage_path.Port = port
        file_storage_path.StorageConfig = storage_config

        if file_storage_path.FileStoragePathID != "":
            file_storage_path_model.update_entity(file_storage_path)
        else:
            file_storage_path.FileStoragePathID = UUIDHelper.get_uuid()
            file_storage_path_model.add_entity(file_storage_path)

        self.reponse_json_success(file_storage_path)


class DeleteStoragePathHandler(StudioBaseHandler):
    """
    :description: 删除存储配置
    """
    @login_filter(True)
    @power_filter(True)
    def get_async(self):
        """
        :description: 删除存储配置
        :param id：id
        :return: 
        :last_editors: HuangJingCan
        """
        file_storage_path_id = self.get_param("FileStoragePathID")
        if file_storage_path_id == "":
            return self.reponse_common("FileStoragePathIDEmpty", "存储配置ID为空")

        FileStoragePathModel(self.get_file_context_key()).del_entity("FileStoragePathID=%s", file_storage_path_id)

        self.reponse_json_success()


class GetResourceListHandler(StudioBaseHandler):
    """
    :description: 获取文件配置列表
    """
    @login_filter(True)
    @power_filter(True)
    def post_async(self):
        """
        :description: 获取文件配置列表
        :param {type} 
        :return: 
        :last_editors: HuangJingCan
        """
        file_resource_model = FileResourceModel(self.get_file_context_key())
        page_index = self.get_page_index()
        page_size = self.get_page_size()
        condition, order = self.get_condition_by_body()

        p_dict, total = file_resource_model.get_dict_page_list("*", page_index, page_size, condition, "", order)

        self.reponse_json_success(self.get_dict_page_info_list(page_index, page_size, p_dict, total))


class GetResourceInfoHandler(StudioBaseHandler):
    """
    :description: 获取文件配置
    """
    @login_filter(True)
    @power_filter(True)
    def get_async(self):
        """
        :description: 获取文件配置
        :param {type} 
        :return: 
        :last_editors: HuangJingCan
        """
        file_resource_model = FileResourceModel(self.get_file_context_key())
        p_dict = file_resource_model.get_dict_by_id(self.get_page_cote_id())

        self.reponse_json_success(p_dict)


class SaveResourceHandler(StudioBaseHandler):
    """
    :description: 保存文件配置
    """
    @login_filter(True)
    @power_filter(True)
    def post_async(self):
        """
        :description: 保存文件配置
        :param id：id
        :return: 
        :last_editors: HuangJingCan
        """
        # 获取参数
        file_resource_id = self.get_param("FileResourceID")
        file_resource_name = self.get_param("FileResourceName")
        file_resource_code = self.get_param("FileResourceCode")

        # 验证数据
        if file_resource_name == "":
            return self.reponse_common("FileResourceNameEmpty", "FileResourceName参数为空")
        if file_resource_code == "":
            return self.reponse_common("FileResourceCodeEmpty", "FileResourceCode参数为空")

        file_resource_model = FileResourceModel(self.get_file_context_key())
        file_resource = FileResource()
        if file_resource_id != "":
            file_resource = file_resource_model.get_entity_by_id(file_resource_id)
            if not file_resource:
                return self.reponse_common("NoExist", "数据不存在")

        # 赋值保存
        file_resource.FileResourceName = file_resource_name
        file_resource.FileResourceCode = file_resource_code
        file_resource.CreateDate = TimeHelper.get_now_format_time()
        if file_resource_id != "":
            file_resource_model.update_entity(file_resource)
        else:
            file_resource.FileResourceID = UUIDHelper.get_uuid()
            file_resource_model.add_entity(file_resource)

        self.reponse_json_success(file_resource)


class DeleteResourceHandler(StudioBaseHandler):
    """
    :description: 删除资源
    """
    @login_filter(True)
    @power_filter(True)
    def get_async(self):
        """
        :description: 删除资源
        :param id：id
        :return: 
        :last_editors: HuangJingCan
        """
        file_resource_id = self.get_param("FileResourceID")
        if file_resource_id == "":
            return self.reponse_common("FileResourceIDEmpty", "资源ID为空")

        FileResourceModel(self.get_file_context_key()).del_entity("FileResourceID=%s", file_resource_id)

        self.reponse_json_success()


class GetRestrictListHandler(StudioBaseHandler):
    """
    :description: 获取上传限制
    """
    @login_filter(True)
    @power_filter(True)
    def post_async(self):
        """
        :description: 获取上传限制
        :param {type} 
        :return: reponse_json_success
        :last_editors: HuangJingCan
        """
        condition = ""
        con, order = self.get_condition_by_body()
        page_cote_id = self.get_page_cote_id()
        if page_cote_id:
            condition = f"FileResourceID='{page_cote_id}'"
            if con:
                condition = condition + " AND " + con
        else:
            condition = con

        file_context_key = self.get_file_context_key()
        file_restrict_model = FileRestrictModel(file_context_key)
        page_index = self.get_page_index()
        page_size = self.get_page_size()
        source_dict_list = file_restrict_model.get_dict_list(condition)
        if len(source_dict_list) > 0:
            merge_dict_list = FileStoragePathModel(file_context_key).get_dict_list(field="FileStoragePathID,StoragePathName")
            source_dict_list = DictUtil.merge_dict_list(source_dict_list, "FileStoragePathID", merge_dict_list, "FileStoragePathID", "FileStoragePathID,StoragePathName")
        page_dict = self.get_dict_page_info_list(page_index, page_size, source_dict_list)

        self.reponse_json_success(page_dict)


class SaveRestrictHandler(StudioBaseHandler):
    """
    :description: SaveRestrict
    """
    @login_filter(True)
    @power_filter(True)
    def post_async(self):
        """
        :description: SaveRestrict
        :param id：id
        :return: reponse_json_success
        :last_editors: HuangJingCan
        """
        # 获取参数
        file_restrict_id = self.get_param("FileRestrictID")
        file_storage_path_id = self.get_param("FileStoragePathID")
        access_mode_code_type = int(self.get_param("AccessModeCodeType", "0"))
        path_format_code_type = int(self.get_param("PathFormatCodeType", "0"))
        restrict_name = self.get_param("RestrictName")
        restrict_code = self.get_param("RestrictCode")
        file_type = int(self.get_param("FileType", "0"))
        file_extension = self.get_param("FileExtension")
        file_max_size = int(self.get_param("FileMaxSize", "0"))
        is_return_size = int(self.get_param("IsReturnSize", "0"))
        is_md5 = int(self.get_param("IsMd5", "0"))
        is_history = int(self.get_param("IsHistory", "0"))
        is_water_mark = int(self.get_param("IsWaterMark", "0"))
        is_format_jpeg = int(self.get_param("IsFormatJpeg", "0"))
        water_mark_text = self.get_param("WatermarkText")
        horizontal_align = int(self.get_param("HorizontalAlign", "0"))
        vertical_align = int(self.get_param("VerticalAlign", "0"))
        image_width = int(self.get_param("ImageWidth", "0"))
        image_height = int(self.get_param("ImageHeight", "0"))
        quality_value = int(self.get_param("QualityValue", "0"))
        water_mark_type = int(self.get_param("WatermarkType", "0"))
        water_image_id = self.get_param("WaterImageID")

        # 验证数据
        if restrict_name == "":
            return self.reponse_common("RestrictNameEmpty", "RestrictName参数为空")
        if restrict_code == "":
            return self.reponse_common("RestrictCodeEmpty", "RestrictCode参数为空")

        file_restrict_model = FileRestrictModel(self.get_file_context_key())
        file_restrict = FileRestrict()
        if file_restrict_id != "":
            file_restrict = file_restrict_model.get_entity_by_id(file_restrict_id)
            if not file_restrict:
                return self.reponse_common("NoExistFileResource", "数据不存在")
        page_cote_id = self.get_page_cote_id()
        file_resource = FileResourceModel(self.get_file_context_key()).get_entity_by_id(page_cote_id)
        if not file_resource:
            return self.reponse_common("NoExistFileResource", "数据不存在")

        # 赋值保存
        file_restrict.ResourceCode = file_resource.FileResourceCode
        file_restrict.FileResourceID = page_cote_id
        file_restrict.FileStoragePathID = file_storage_path_id
        file_restrict.AccessModeCodeType = access_mode_code_type
        file_restrict.PathFormatCodeType = path_format_code_type
        file_restrict.RestrictName = restrict_name
        file_restrict.RestrictCode = restrict_code
        file_restrict.FileType = file_type
        file_restrict.FileExtension = file_extension
        file_restrict.FileMaxSize = file_max_size
        file_restrict.IsReturnSize = is_return_size
        file_restrict.IsMd5 = is_md5
        file_restrict.IsHistory = is_history
        file_restrict.IsWaterMark = is_water_mark
        file_restrict.IsFormatJpeg = is_format_jpeg
        file_restrict.WatermarkText = water_mark_text
        file_restrict.HorizontalAlign = horizontal_align
        file_restrict.VerticalAlign = vertical_align
        file_restrict.ImageWidth = image_width
        file_restrict.ImageHeight = image_height
        file_restrict.QualityValue = quality_value
        file_restrict.WatermarkType = water_mark_type
        file_restrict.WaterImageID = water_image_id

        if file_restrict_id != "":
            file_restrict_model.update_entity(file_restrict)
        else:
            file_restrict.FileRestrictID = UUIDHelper.get_uuid()
            file_restrict_model.add_entity(file_restrict)

        self.reponse_json_success(file_restrict)


class DeleteRestrictHandler(StudioBaseHandler):
    """
    :description: DeleteRestrict
    """
    @login_filter(True)
    @power_filter(True)
    def get_async(self):
        """
        :description: 删除
        :param id：id
        :return: 
        :last_editors: HuangJingCan
        """
        file_restrict_id = self.get_param("FileRestrictID")
        if file_restrict_id == "":
            return self.reponse_common("FileRestrictIDEmpty", "FileRestrictID为空")

        FileRestrictModel(self.get_file_context_key()).del_entity("FileRestrictID=%s", file_restrict_id)

        self.reponse_json_success()


class GetWaterImageListHandler(StudioBaseHandler):
    """
    :description: 获取水印图片列表
    """
    @login_filter(True)
    @power_filter(True)
    def post_async(self):
        """
        :description: 获取水印图片列表
        :param {type} 
        :return: 
        :last_editors: HuangJingCan
        """
        file_water_image_model = FileWaterImageModel(self.get_file_context_key())
        page_index = self.get_page_index()
        page_size = self.get_page_size()
        condition, order = self.get_condition_by_body()

        p_dict, total = file_water_image_model.get_dict_page_list("*", page_index, page_size, condition, "", order)

        self.reponse_json_success(self.get_dict_page_info_list(page_index, page_size, p_dict, total))


class GetWaterImageDataHandler(StudioBaseHandler):
    """
    :description: 获取水印图片
    """
    @login_filter(True)
    @power_filter(True)
    def get_async(self):
        """
        :description: 获取水印图片
        :param {type} 
        :return: 
        :last_editors: HuangJingCan
        """
        file_water_image_model = FileWaterImageModel(self.get_file_context_key())
        p_dict = file_water_image_model.get_dict_list(field="WaterImageID,WaterName")

        self.reponse_json_success(p_dict)


class SaveWaterImageHandler(StudioBaseHandler):
    """
    :description: 保存图片水印
    """
    @login_filter(True)
    @power_filter(True)
    def post_async(self):
        """
        :description: 保存图片水印
        :param WaterImageID：水印图片id 
        :param WaterImagePath：水印图片路径
        :param WaterName：水印图片名称
        :return: reponse_json_success
        :last_editors: HuangJingCan
        """
        # 获取参数
        water_image_id = self.get_param("WaterImageID")
        water_image_path = self.get_param("WaterImagePath")
        water_name = self.get_param("WaterName")

        # 验证数据
        if water_name == "":
            return self.reponse_common("WaterNameEmpty", "水印名称为空")

        file_water_image_model = FileWaterImageModel(self.get_file_context_key())
        file_water_image = FileWaterImage()
        if water_image_id != "":
            file_water_image = file_water_image_model.get_entity_by_id(water_image_id)
            if not file_water_image:
                return self.reponse_common("NoExist", "数据不存在")

        # 赋值
        file_water_image.WaterImagePath = water_image_path
        file_water_image.WaterName = water_name

        if water_image_id != "":
            file_water_image_model.update_entity(file_water_image)
        else:
            file_water_image.WaterImageID = UUIDHelper.get_uuid()
            file_water_image_model.add_entity(file_water_image)

        self.reponse_json_success(file_water_image)


class DeleteWaterImageHandler(StudioBaseHandler):
    """
    :description: 删除水印图
    """
    @login_filter(True)
    @power_filter(True)
    def get_async(self):
        """
        :description: 删除
        :param WaterImageID：主键id
        :return: 
        :last_editors: HuangJingCan
        """
        water_image_id = self.get_param("WaterImageID")
        if water_image_id == "":
            return self.reponse_common("WaterImageIDEmpty", "WaterImageID为空")

        FileWaterImageModel(self.get_file_context_key()).del_entity("WaterImageID=%s", water_image_id)

        self.reponse_json_success()


class GetHistoryListHandler(StudioBaseHandler):
    """
    :description: 获取文件历史
    """
    @login_filter(True)
    @power_filter(True)
    def post_async(self):
        """
        :description: 获取文件历史
        :param {type} 
        :return: 
        :last_editors: HuangJingCan
        """
        file_history_model = FileHistoryModel(self.get_file_context_key())
        page_index = self.get_page_index()
        page_size = self.get_page_size()
        condition, order = self.get_condition_by_body()

        p_dict, total = file_history_model.get_dict_page_list("*", page_index, page_size, condition, "", order)

        self.reponse_json_success(self.get_dict_page_info_list(page_index, page_size, p_dict, total))


class DeleteHistoryHandler(StudioBaseHandler):
    """
    :description: 删除文件历史记录
    """
    @login_filter(True)
    @power_filter(True)
    def get_async(self):
        """
        :description: 删除文件历史记录
        :param FileHistoryID：主键id
        :return: 
        :last_editors: HuangJingCan
        """
        file_history_id = self.get_param("FileHistoryID")
        if file_history_id == "":
            return self.reponse_common("FileHistoryIDEmpty", "FileHistoryID为空")

        result = 0
        file_context_key = self.get_file_context_key()
        file_history_model = FileHistoryModel(file_context_key)
        file_history = file_history_model.get_entity_by_id(file_history_id)
        if file_history:
            file_storage_path_model = FileStoragePathModel(file_context_key)
            file_storage_path = file_storage_path_model.get_entity_by_id(file_history.FileStoragePathID)
            if file_storage_path:
                if file_storage_path.VirtualName == "Seven.Manage.KS3":
                    result = KS3.delete(file_storage_path.StorageConfig, file_history.FileUrl)
                    if result == 0:
                        # 判断文件是否还在云服务器，不存在就删除本地历史记录
                        contents = KS3.get(file_storage_path.StorageConfig, file_history.FileUrl)
                        if contents == "":
                            result = 1
                elif file_storage_path.StorageTypeID == 1:
                    if os.path.exists(file_history.FileUrl):
                        os.remove(file_history.FileUrl)
                    result = 1
            else:
                result = 1

        if result > 0:
            file_history_model.del_entity("FileHistoryID=%s", file_history_id)

        self.reponse_json_success()