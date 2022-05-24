'''
Author: hexu
Date: 2021-11-19 10:29:02
LastEditTime: 2022-04-18 14:19:38
LastEditors: Hexu
Description: 文件存储服务
FilePath: /iw-algo-fx/intelliw/utils/storage_service.py
'''
import json
import os
from intelliw.utils import iuap_request
from intelliw.config.config import STORAGE_SERVICE_URL


class StorageService:
    """
        文件传输，通过服务端获取的临时url进行文件在多个云存储（AliOss/Minio/HWObs）上的操作
        所有的请求需要进行加签
    """

    def __init__(self, key, client_type, process_type):
        """
        初始化下载/上传链接
            Args:
                key : 
                    upload ： 文件存储于桶的位置（包含文件名） OSS_PATH + filename
                    download : AI工作坊存储在环境变量的值     DATA_SOURCE_ADDRESS
                client_type ： AliOss/Minio/HWObs
                process_type : download/upload
            Returns:
                self.service_url 为服务端根据client_type，process_type生成的链接， download和upload操作需要此链接
        """
        self.key = key
        self.client_type = client_type
        self.service_url = self.__client_init(key, client_type, process_type)

    def __client_init(self, key, client_type, process_type):
        """
        从服务端获取云存储操作链接

        下载链接一般可以直接下载的
        """
        if not STORAGE_SERVICE_URL and process_type == "download" and key.startswith("http"):
            return self.key 
    
        resp = iuap_request.get(url=STORAGE_SERVICE_URL, params={
                                "key": key, "UrlType": process_type, "clientType": client_type})
        resp.raise_for_status
        result = json.loads(resp.body)
        assert result.get("status") == 1, result
        return result.get("data")

    def upload(self, filepath):
        """
        通过操作链接进行上传操作
            Args: 
                filepath ： 上传文件本地路径
        """
        if os.path.exists(filepath) and os.path.isfile(filepath):
            try:
                with open(filepath, 'rb') as f:
                    payload = f.read()
                    resp = iuap_request.put_file(
                        url=self.service_url, headers={'Content-Type': 'application/octet-stream'}, data=payload)
                    resp.raise_for_status()
            except Exception as e:
                raise Exception(f'{e}')
        else:
            raise FileNotFoundError(f'文件 {filepath} 不存在')

    def download(self, output_path):
        """
        通过操作链接进行下载操作
            Args: 
                output_path ： 下载文件保存路径
        """
        if os.path.exists(output_path):
            raise FileExistsError(f'文件 {output_path} 已存在')
        resp = iuap_request.get(url=self.service_url)
        resp.raise_for_status()
        mode = "wb"
        if type(resp.body) == str:
            mode = "w"
        with open(output_path, mode) as code:
            code.write(resp.body)
    
    