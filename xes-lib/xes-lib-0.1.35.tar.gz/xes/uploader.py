# coding=utf-8
import requests
import json
import hashlib
import os

class XesUploader:

    # 文件相对路径
    def upload(self, relativeFilePath):
        absolutePath = os.getcwd() + "/" + relativeFilePath
        return self.uploadAbsolutePath(absolutePath)

    # 文件绝对路径
    def uploadAbsolutePath(self, filepath):
        md5 = None
        contents = None
        if os.path.isfile(filepath):
            fp = open(filepath, 'rb')
            contents = fp.read()
            fp.close()
            md5 = hashlib.md5(contents).hexdigest()

        if md5 is None or contents is None:
            raise Exception("文件不存在")

        uploadParams = self._getUploadParams(filepath, md5)
        requests.request(method="PUT", url=uploadParams['host'], data=contents, headers=uploadParams['headers'])
        return uploadParams['url']

    # 获取上传签名
    def _getUploadParams(self, filename, md5):
        url = 'https://code.xueersi.com/api/assets/get_oss_upload_params'
        params = {"scene": "offline_python_assets", "md5": md5, "filename": filename}
        response = requests.get(url=url, params=params)
        data = json.loads(response.text)['data']

        return data

# 调用示例
# from xes import uploader
# uploader = XesUploader()
# imgurl = uploader.upload("小雪-小低.png")
# print(imgurl)
