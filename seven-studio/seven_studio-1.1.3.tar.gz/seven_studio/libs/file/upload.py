# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2020-04-29 11:00:52
:LastEditTime: 2022-05-24 20:42:21
:LastEditors: ChenXiaolei
:Description: 文件上传信息
"""
from PIL import Image
from io import BytesIO
from seven_studio.libs.file.ks3 import *
from seven_studio.libs.file.oss2 import *
from seven_studio.libs.file.cos import *
from seven_studio.libs.file.bos import *
from seven_studio.libs.file.s3 import *
from seven_studio.utils.random import *
from seven_framework.time import *
from seven_framework.uuid import *
from seven_framework.crypto import *

from seven_studio.models.seven_model import InvokeResult
from seven_studio.models.seven_model import FileUploadInfo
from seven_studio.models.enum import AccessModeCodeType
from seven_studio.models.db_models.file.file_storage_path_model import *
from seven_studio.models.db_models.file.file_restrict_model import *
from seven_studio.models.db_models.file.file_history_model import *


class FileUpload():
    """
    :description: 文件相关操作类
    :param {type} 
    :return: 
    :last_editors: HuangJingCan
    """
    def __init__(self, file_context_key='db_sevenstudio'):
        self.file_context_key = file_context_key

    def upload(self, resource_code, restrict_code, dict_file):
        """
        :description: 文件上传
        :param resource_code：资源代码
        :param restrict_code：资源限制码
        :param dict_file：字典文件信息
        :return: InvokeResult
        :last_editors: HuangJingCan
        """
        invoke_result = InvokeResult()

        if resource_code == "" or restrict_code == "":
            invoke_result.ResultCode = "1"
            invoke_result.ResultMessage = "ResourceCode或RestrictCode为空"
            return invoke_result

        storage_config = ""
        file_restrict_model = FileRestrictModel(self.file_context_key)
        file_restrict = file_restrict_model.get_entity("ResourceCode=%s AND RestrictCode=%s", params=[resource_code, restrict_code])
        if not file_restrict:
            invoke_result.ResultCode = "NoExistFileRestrict"
            invoke_result.ResultMessage = "文件配置不存在"
            return invoke_result

        if not dict_file:
            invoke_result.ResultCode = "NoExistFile"
            invoke_result.ResultMessage = "文件不存在"
            return invoke_result

        list_file = dict_file["file"]
        for info in list_file:
            file_name = info["filename"]
            file_body = info["body"]

            invoke_result = self.upload_file(file_body, file_name, file_restrict)
            if invoke_result.ResultCode == "0" and invoke_result.Data:
                invoke_result.Data = invoke_result.Data.ResourcePath

        return invoke_result

    def upload_file(self, stream, file_name, file_restrict, image_width=0, image_height=0, quality=0, is_format_jpeg=0, is_water_mark=0, horizontal_align=0, vertical_align=0):
        """
        :description: 文件上传
        :param {type} 
        :return: 
        :last_editors: HuangJingCan
        """
        invoke_result = InvokeResult()
        file_upload_info = FileUploadInfo()
        file_extension = os.path.splitext(file_name)[1]
        if file_restrict.FileExtension != "":
            file_find = file_restrict.FileExtension.find(file_extension.lower().strip("."))
            if file_find == -1:
                invoke_result.ResultCode = "1"
                invoke_result.ResultMessage = f"上传的文件扩展名必须是{file_restrict.FileExtension}，当前文件是:{file_extension}"
                return invoke_result
        file_size = len(stream)
        if file_restrict.FileMaxSize > 0 and file_size / 1024 > file_restrict.FileMaxSize:
            invoke_result.ResultCode = "1"
            invoke_result.ResultMessage = f"对不起支持上传的文件大小为{self.__to_file_size(file_restrict.FileMaxSize * 1024)}，当前的文件大小为{self.__to_file_size(file_size)}，已超出"
            return invoke_result

        if file_extension.__contains__(".gif"):
            return self.switch_upload(stream, file_name, file_restrict)

        if image_width > 0 or image_height > 0 or (file_extension.__contains__(".bmp") or file_extension.__contains__(".png")) and is_format_jpeg or is_water_mark or (quality > 0 and quality < 100):
            # 其他图片格式转jpg
            # im = Image.open(BytesIO(stream))
            # im = im.convert("RGB")
            # im.save("G:\\Temp\\test.jpg")
            return self.switch_upload(stream, file_name, file_restrict)
        else:
            return self.switch_upload(stream, file_name, file_restrict)

    def __to_file_size(self, size):
        """
        :description: 文件大小格式化
        :param size：文件大小
        :return: 
        :last_editors: HuangJingCan
        """
        if size < 1000:
            return '%i' % size + 'size'
        elif 1024 <= size < 1048576:
            return '%.2f' % float(size / 1024) + 'KB'
        elif 1048576 <= size < 1073741824:
            return '%.2f' % float(size / 1048576) + 'MB'
        elif 1073741824 <= size < 1000000000000:
            return '%.2f' % float(size / 1073741824) + 'GB'
        elif 1000000000000 <= size:
            return '%.2f' % float(size / 1000000000000) + 'TB'

    def switch_upload(self, stream, file_name, file_restrict):
        """
        :description: 文件上传
        :param {type} 
        :return: 
        :last_editors: HuangJingCan
        """
        invoke_result = InvokeResult()
        file_upload_info = FileUploadInfo()
        file_extension = os.path.splitext(file_name)[1].lower()
        query_size = ""
        image_width = 0
        image_height = 0
        # 返回图片尺寸
        if file_restrict.IsReturnSize == 1:
            im = Image.open(BytesIO(stream))
            if im:
                image_width = im.width
                image_height = im.height
                query_size = f"?w={image_width}&h={image_height}"

        file_storage_path_model = FileStoragePathModel(self.file_context_key)
        file_storage_path = file_storage_path_model.get_entity_by_id(file_restrict.FileStoragePathID)
        if file_storage_path.StorageTypeID == 1:
            # 本地文件
            resource_code = file_restrict.ResourceCode
            create_date_time = TimeHelper.get_now_datetime()
            resource_ver_id = UUIDHelper.get_uuid()

            resource_uuid_file_name = resource_ver_id + file_extension
            virtual_name = RandomUtil.get_random_switch_string(file_storage_path.VirtualName)
            path_format_value = self.get_resource_path_format_value(create_date_time, resource_ver_id, file_restrict.PathFormatCodeType)
            resource_url = self.get_resource_url(virtual_name, file_restrict.AccessModeCodeType, resource_code, path_format_value, resource_uuid_file_name, file_name)
            full_file_name = self.get_resource_full_file_name_path(file_storage_path.StoragePath, file_restrict.AccessModeCodeType, resource_code, path_format_value, resource_uuid_file_name, file_name)

            if file_restrict.IsMd5 == 1:
                file_upload_info.Md5Value = CryptoHelper.md5_encrypt_bytes(stream).upper()

            im = Image.open(BytesIO(stream))
            im.save(full_file_name)

            file_upload_info.FilePath = full_file_name
            file_upload_info.OriginalName = file_name
            file_upload_info.ResourcePath = resource_url

            # return file_upload_info
        elif file_storage_path.StorageTypeID == 2:
            # FTP服务器
            pass
        elif file_storage_path.StorageTypeID == 3:
            # FastDFS文件服务器
            pass
        elif file_storage_path.StorageTypeID in (4, 5, 6, 7, 8):
            if file_storage_path.StorageTypeID == 4:
                # 金山云
                invoke_result = KS3.upload(file_storage_path.StorageConfig, file_name, stream)
            elif file_storage_path.StorageTypeID == 5:
                # 阿里云
                invoke_result = OSS2.upload(file_storage_path.StorageConfig, file_name, stream)
            elif file_storage_path.StorageTypeID == 6:
                # 腾讯云
                invoke_result = COS.upload(file_storage_path.StorageConfig, file_name, stream)
            elif file_storage_path.StorageTypeID == 7:
                # 百度云
                invoke_result = BOS.upload(file_storage_path.StorageConfig, file_name, stream)
            elif file_storage_path.StorageTypeID == 8:
                # AWS
                invoke_result = S3.upload(file_storage_path.StorageConfig, file_name, stream)

            if invoke_result.ResultCode != "0":
                return invoke_result

            if invoke_result.Data:
                file_upload_info.Md5Value = invoke_result.Data["Md5Value"]
                file_upload_info.ResourcePath = invoke_result.Data["ResourcePath"]
                file_upload_info.OriginalName = invoke_result.Data["OriginalName"]
                file_upload_info.FilePath = invoke_result.Data["FilePath"]
                file_upload_info.ImageWidth = invoke_result.Data["ImageWidth"]
                file_upload_info.ImageHeight = invoke_result.Data["ImageHeight"]

        if file_restrict.IsHistory == 1:
            file_history = FileHistory()
            file_history.FileResourceID = file_restrict.FileResourceID
            file_history.FileRestrictID = file_restrict.FileRestrictID
            file_history.FileStoragePathID = file_restrict.FileStoragePathID
            file_history.FileType = file_restrict.FileType
            file_history.FileStatus = 1
            file_history.FileTitle = file_name
            file_history.FileUrl = file_upload_info.ResourcePath
            file_history.CreateDate = TimeHelper.get_now_format_time()
            file_history.CreateUserID = 0

            file_history_model = FileHistoryModel(self.file_context_key)
            file_history_model.add_entity(file_history)

        file_upload_info.ResourcePath = file_upload_info.ResourcePath + query_size
        file_upload_info.ImageWidth = image_width
        file_upload_info.ImageHeight = image_height

        invoke_result.Data = file_upload_info

        return invoke_result

    def get_resource_path_format_value(self, create_date_time, resource_ver_id, path_format_code_id):
        """
        :description: 获取附件路径格式值规则
        :param {type} 
        :return: 
        :last_editors: HuangJingCan
        """
        result = ""
        if path_format_code_id == 0:
            result = TimeHelper.datetime_to_format_time(create_date_time, "%Y-%m-%d")
        elif path_format_code_id == 1:
            result = TimeHelper.datetime_to_format_time(create_date_time, "%Y-%m-%d-%H")
        elif path_format_code_id == 2:
            result = str(resource_ver_id)
        return result

    def get_resource_url(self, virtual_name, access_mode_code_value, resource_code, path_format_value, resource_uuid_file_name, resource_file_name):
        """
        :description: 获取资源网址规则 [组合附件网址]
        :param {type} 
        :return: 
        :last_editors: HuangJingCan
        """
        resource_url = ""
        uuid_file_name = os.path.splitext(resource_uuid_file_name)[0]
        virtual_name = virtual_name.rstrip("/")
        if path_format_value != "":
            if access_mode_code_value == AccessModeCodeType.VirtualAccess.value:
                resource_url = f"{virtual_name}/{resource_code}/{path_format_value}/{resource_uuid_file_name}"
                return resource_url
            resource_url = f"{virtual_name}/{resource_code}/{path_format_value}/{uuid_file_name}/{resource_file_name}"
            return resource_url
        if access_mode_code_value == AccessModeCodeType.VirtualAccess.value:
            resource_url = f"{virtual_name}/{resource_code}/{resource_uuid_file_name}"
            return resource_url
        resource_url = f"{virtual_name}/{resource_code}/{uuid_file_name}/{resource_file_name}"
        return resource_url

    def get_resource_full_file_name_path(self, storage_path, access_mode_code_value, resource_code, path_format_value, resource_uuid_file_name, resource_file_name, is_create_directory=True):
        """
        :description: 获取附件完整文件名规则 [组合完整文件名]
        :param {type} 
        :return: 
        :last_editors: HuangJingCan
        """
        resource_directory = ""
        if storage_path == "":
            resource_directory = self.get_resource_directory_path(access_mode_code_value, resource_code, path_format_value, resource_uuid_file_name)
        else:
            dir_path = self.get_resource_directory_path(access_mode_code_value, resource_code, path_format_value, resource_uuid_file_name)
            resource_directory = os.path.join(storage_path, dir_path)
        if is_create_directory:
            if not os.path.exists(resource_directory):
                os.makedirs(resource_directory)
        if access_mode_code_value == AccessModeCodeType.VirtualOriginalAccess.value:
            return resource_directory + "\\" + resource_file_name
        return resource_directory + "\\" + resource_uuid_file_name

    def get_resource_directory_path(self, access_mode_code_value, resource_code, path_format_value, resource_uuid_file_name):
        """
        :description: 获取资源目录规则
        :param {type} 
        :return: 
        :last_editors: HuangJingCan
        """
        resource_directory = ""
        if path_format_value != "":
            resource_directory = os.path.join(resource_code, path_format_value)
        else:
            resource_directory = resource_code
        if access_mode_code_value == AccessModeCodeType.VirtualOriginalAccess.value:
            resource_directory = os.path.join(resource_directory, os.path.splitext(resource_uuid_file_name)[0])

        return resource_directory
