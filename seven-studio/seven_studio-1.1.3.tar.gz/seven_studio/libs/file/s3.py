# -*- coding: utf-8 -*-
"""
:Author: ChenXiaolei
:Date: 2020-04-29 10:02:31
:LastEditTime: 2022-05-24 20:41:13
:LastEditors: ChenXiaolei
:Description: AWS S3存储
"""
import base64
from enum import Enum
from seven_framework.log import *
from seven_framework.uuid import *
from seven_framework.file import S3Helper

from seven_studio.utils.random import *

from seven_studio.models.seven_model import InvokeResult, FileUploadInfo


class S3:
    """
    :description: AWSS3
    :last_editors: ChenXiaolei
    """
    logger_error = Logger.get_logger_by_name("log_error")
    logger_info = Logger.get_logger_by_name("log_info")

    @classmethod
    def upload(self, storage_config, file_name='', stream=None, file_path=''):
        """
        :description: 文件上传
        :param storage_config：配置内容
        :param file_name：文件名(按路径上传时此参数为空)
        :param stream：文件内容(按路径上传时此参数为空)
        :param file_path：文件路径(为空按stream上传，不为空则按路径上传)
        :return: InvokeResult
        :last_editors: ChenXiaolei
        """

        invoke_result = InvokeResult()
        file_upload_info = FileUploadInfo()
        file_upload_config = json.loads(storage_config)

        access_key = file_upload_config.get("AccessKey", "")
        secret_key = file_upload_config.get("SecretKey", "")
        bucket = file_upload_config.get("Bucket", "")
        end_point = file_upload_config.get("EndPoint", "")
        domain = file_upload_config.get("Domain", "").rstrip('/')
        is_autofile_name = file_upload_config.get("IsAutoFileName", 0)
        folder = file_upload_config.get("Folder", "").strip('/')
        folder = folder + "/" if folder != "" else folder

        # 返回文件名
        file_name = os.path.basename(file_path) if file_path != "" else file_name

        if is_autofile_name == 1:
            file_extension = os.path.splitext(file_name)[1]
            file_name = UUIDHelper.get_uuid().replace("-", "") + file_extension

        try:
            conn = S3Helper(access_key, secret_key, end_point)
            key_name = folder + file_name
            result = False
            if file_path != "":
                result = conn.put_file_from_file_path(bucket, key_name, file_path)
            else:
                result = conn.put_file(bucket, key_name, stream)

            if result:
                virtual_name = RandomUtil.get_random_switch_string(domain).rstrip('/')
                file_upload_info.ResourcePath = virtual_name + "/" + key_name
                invoke_result.Data = file_upload_info.__dict__
        except Exception as ex:
            self.logger_error.exception(ex)
            invoke_result.ResultCode = "1"
            invoke_result.ResultMessage = "S3上传文件出错"

        return invoke_result

    @classmethod
    def delete(self, storage_config, file_path):
        """
        :description: 删除文件
        :param storage_config：配置内容
        :param file_path：文件路径
        :return: 成功返回1 失败0
        :last_editors: ChenXiaolei
        """

        if file_path == "":
            return 1
        file_upload_config = json.loads(storage_config)

        access_key = file_upload_config.get("AccessKey", "")
        secret_key = file_upload_config.get("SecretKey", "")
        bucket = file_upload_config.get("Bucket", "")
        end_point = file_upload_config.get("EndPoint", "")
        folder = file_upload_config.get("Folder", "").strip('/')
        folder = folder + "/" if folder != "" else folder

        # 返回文件名
        file_name = os.path.basename(file_path) if file_path != "" else ""

        result = 0

        try:
            conn = S3Helper(access_key, secret_key, end_point)
            conn.del_file(bucket, folder + file_name)
            result = 1
        except Exception as ex:
            self.logger_error.exception(ex)

        return result

    @classmethod
    def get(self, storage_config, file_path):
        """
        :description: 获取文件
        :param storage_config：配置内容
        :param file_path：文件路径或者文件名
        :return: 文件流
        :last_editors: ChenXiaolei
        """
        invoke_result = InvokeResult()
        file_upload_config = json.loads(storage_config)

        access_key = file_upload_config.get("AccessKey", "")
        secret_key = file_upload_config.get("SecretKey", "")
        bucket = file_upload_config.get("Bucket", "")
        end_point = file_upload_config.get("EndPoint", "")
        folder = file_upload_config.get("Folder", "").strip('/')
        folder = folder + "/" if folder != "" else folder

        # 返回文件名
        file_name = os.path.basename(file_path) if file_path != "" else ""

        result = ""

        try:
            conn = S3Helper(access_key, secret_key, end_point)
            result = conn.get_file_contents(bucket, folder + file_name)
        except Exception as ex:
            self.logger_error.exception(ex)

        return result

    @classmethod
    def get_list(self, storage_config, prefix=""):
        """
        :description: 列举Bucket内的文件或者目录
        :param storage_config：配置内容
        :param file_path：文件路径
        :param prefix：指定前缀
        :return: 文件列表，目录列表
        :last_editors: ChenXiaolei
        """
        invoke_result = InvokeResult()
        file_upload_config = json.loads(storage_config)

        access_key = file_upload_config.get("AccessKey", "")
        secret_key = file_upload_config.get("SecretKey", "")
        bucket = file_upload_config.get("Bucket", "")
        end_point = file_upload_config.get("EndPoint", "")
        folder = file_upload_config.get("Folder", "").strip('/')
        folder = folder + "/" if folder != "" else folder

        result_list = []
        result_dir = []

        try:
            conn = S3Helper(access_key, secret_key, end_point)
            result_list, result_dir = conn.get_bucket_objects(bucket, prefix)
        except Exception as ex:
            self.logger_error.exception(ex)

        return result_list, result_dir

    @classmethod
    def upload_part(self, storage_config, source_path):
        """
        :description: 分块上传-单线程
        :param storage_config：配置内容
        :param source_path：文件路径
        :param prefix：指定前缀
        :return: 文件列表，目录列表
        :last_editors: ChenXiaolei
        """
        invoke_result = InvokeResult()
        file_upload_info = FileUploadInfo()
        file_upload_config = json.loads(storage_config)

        access_key = file_upload_config.get("AccessKey", "")
        secret_key = file_upload_config.get("SecretKey", "")
        bucket = file_upload_config.get("Bucket", "")
        end_point = file_upload_config.get("EndPoint", "")
        domain = file_upload_config.get("Domain", "").rstrip('/')
        is_autofile_name = file_upload_config.get("IsAutoFileName", 0)
        folder = file_upload_config.get("Folder", "").strip('/')
        folder = folder + "/" if folder != "" else folder

        file_name = ""
        # 返回文件名
        file_name = os.path.basename(source_path) if source_path != "" else file_name

        if is_autofile_name == 1:
            file_extension = os.path.splitext(file_name)[1]
            file_name = UUIDHelper.get_uuid().replace("-", "") + file_extension

        try:
            conn = S3Helper(access_key, secret_key, end_point)
            conn.multi_put_file(bucket, folder + file_name, source_path)

            virtual_name = RandomUtil.get_random_switch_string(domain).rstrip('/')
            file_upload_info.ResourcePath = virtual_name + "/" + folder + file_name
            invoke_result.Data = file_upload_info.__dict__

        except Exception as ex:
            self.logger_error.exception(ex)
            invoke_result.ResultCode = "1"
            invoke_result.ResultMessage = "S3上传文件出错"

        return invoke_result

    @classmethod
    def water_marker_text(self, img_url, text, font="", fontsize="", fill="", dissolve="", gravity="", dx="", dy="", q=""):
        pass

    @classmethod
    def water_marker_img(self, img_url, image, wtw="", wth="", dissolve="", gravity="", dx="", dy="", q=""):
        pass

    @classmethod
    def img_scale(self, img_url, w="", h="", m="", p="", so="", q="", F="", r="", c="", f="", s="", cox="", coy="", rotate="", et="", etw="", eth="", etc=""):
        pass