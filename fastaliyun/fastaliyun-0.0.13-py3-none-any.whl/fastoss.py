#!/usr/bin/env python3
# coding = utf8
"""
@ Author : ZeroSeeker
@ e-mail : zeroseeker@foxmail.com
@ GitHub : https://github.com/ZeroSeeker
@ Gitee : https://gitee.com/ZeroSeeker
"""
import showlog
import oss2
import envx
"""
SDK文档：https://help.aliyun.com/document_detail/32026.html
"""
env_file_name_default = 'aliyun.oss.env'


def make_con_info(
        env_file_name: str = env_file_name_default
):
    inner_env = envx.read(file_name=env_file_name)
    if inner_env is None or len(inner_env) == 0:
        showlog.warning('[%s]文件不存在或文件填写错误！' % env_file_name)
        exit()
    else:
        con_info = dict()

        bucket_name = inner_env.get('bucket_name')
        if bucket_name is not None and len(bucket_name) > 0:
            con_info['bucket_name'] = bucket_name
        else:
            showlog.warning('bucket_name 未填写')
            exit()

        end_point = inner_env.get('endpoint')
        if end_point is not None and len(end_point) > 0:
            con_info['endpoint'] = end_point
        else:
            showlog.warning('endpoint 未填写，将设置为默认值：oss-cn-shanghai.aliyuncs.com')
            con_info['endpoint'] = 'oss-cn-shanghai.aliyuncs.com'

        access_key_id = inner_env.get('access_key_id')
        if access_key_id is not None and len(access_key_id) > 0:
            con_info['access_key_id'] = access_key_id
        else:
            showlog.warning('access_key_id 未填写')
            exit()

        access_key_secret = inner_env.get('access_key_secret')
        if access_key_secret is not None and len(access_key_secret) > 0:
            con_info['access_key_secret'] = access_key_secret
        else:
            showlog.warning('access_key_secret 未填写')
            exit()

        return con_info


class Basics:
    def __init__(
            self,
            con_info=None
    ):
        if con_info is not None:
            self.access_key_id = con_info['access_key_id']
            self.access_key_secret = con_info['access_key_secret']
            self.endpoint = con_info['endpoint']
            self.endpoint_url = "https://%s" % con_info['endpoint']
            self.bucket_name = con_info['bucket_name']
            # 创建Bucket对象，所有Object相关的接口都可以通过Bucket对象来进行
            self.oss_host = "https://%s" % self.endpoint
            self.auth = oss2.Bucket(
                oss2.Auth(
                    self.access_key_id,
                    self.access_key_secret
                ),
                self.endpoint_url,
                self.bucket_name
            )
        else:
            exit()

    def get_auth_bucket(
            self
    ):
        # 鉴权
        return oss2.Bucket(
            oss2.Auth(
                self.access_key_id,
                self.access_key_secret
            ),
            self.endpoint_url,
            self.bucket_name
        )

    def upload_file(
            self,
            key,
            filename,
            headers: dict = None
    ):
        """
        上传文件（本地）
        :param str key: 上传到OSS的文件名
        :param str filename: 本地文件名，需要有可读权限
        :param str headers:
        """
        return self.auth.put_object_from_file(
            key=key,
            filename=filename,
            headers=headers
        )

    def upload_object(
            self,
            key,
            data,
            headers: dict = None
    ):
        """
        上传内容，二进制流
        :param str key: 上传到OSS的文件名
        :param str data: 内容二进制,
        :param str headers: 用户指定的HTTP头部。可以指定Content-Type、Content-MD5、x-oss-meta-开头的头部等
                缓存控制 Cache-Control: max-age=86400就可以了，max-age以秒为单位，86400即24小时。
        :param str progress_callback:
        """
        return self.auth.put_object(
            key=key,
            data=data,
            headers=headers
        )

    def show_bucket(
            self,
            limit=None
    ):
        # [打印]列举Bucket下10个Object，并打印它们的最后修改时间、文件名
        if limit is None:
            for i, object_info in enumerate(oss2.ObjectIterator(self.get_auth_bucket())):
                print("{0} {1}".format(object_info.last_modified, object_info.key))
        else:
            for i, object_info in enumerate(oss2.ObjectIterator(self.get_auth_bucket())):
                print("{0} {1}".format(object_info.last_modified, object_info.key))
                if i >= (limit - 1):
                    break

    def get_bucket_list(
            self,
            limit=None
    ):
        # [返回]列举Bucket下10个Object，并打印它们的最后修改时间、文件名
        bucket_list = list()
        if limit is None:
            for i, object_info in enumerate(oss2.ObjectIterator(self.get_auth_bucket())):
                bucket_list.append({'last_modified': object_info.last_modified, "object_key": object_info.key})
        else:
            for i, object_info in enumerate(oss2.ObjectIterator(self.get_auth_bucket())):
                bucket_list.append({'last_modified': object_info.last_modified, "object_key": object_info.key})
                if i >= (limit - 1):
                    break
        return bucket_list

    def get_content(
            self,
            key
    ):
        return self.get_auth_bucket().get_object(key).read().decode('utf-8')

    def download(
            self,
            key,
            filename=None,
            path=''
    ):
        if filename is None:
            return self.get_auth_bucket().get_object_to_file(key, '%s/%s' % (path, key))
        else:
            return self.get_auth_bucket().get_object_to_file(key, '%s/%s' % (path, filename))


def upload_file(
        oss_filename,
        local_filename,
        custom_host=None,
        env_file_name: str = env_file_name_default,
        con_info: dict = None,
        headers: dict = None
):
    """
    上传文件（从本地读取）
    :param oss_filename: 上传oss后的文件名
    :param local_filename: 本地待上传的文件名
    :param custom_host: 自定义域名
    :param env_file_name: 环境文件名
    :param con_info: 环境
    :param headers: {'Cache-Control':'max-age=5'}表示缓存有效期为5秒
    """
    # ---------------- 固定设置 ----------------
    if con_info is None:
        con_info = make_con_info(env_file_name=env_file_name)
    else:
        pass
    # ---------------- 固定设置 ----------------
    basic = Basics(con_info=con_info)
    res = basic.upload_file(
        key=oss_filename,
        filename=local_filename,
        headers=headers
    )
    base_url = 'https://%s.%s/%s' % (basic.bucket_name, basic.endpoint, oss_filename)
    if custom_host is None:
        custom_http_url = ''
        custom_https_url = ''
    else:
        custom_http_url = 'http://%s/%s' % (custom_host, oss_filename)
        custom_https_url = 'https://%s/%s' % (custom_host, oss_filename)
    response = {
        'status': res.status,
        'e_tag': res.etag,  # Etag
        'version_id': res.versionid,  # 版本信息
        'base_url': base_url,
        'custom_host': custom_host,
        'custom_http_url': custom_http_url,
        'custom_https_url': custom_https_url
    }
    return response


def upload_content(
        oss_filename,
        data,
        custom_host=None,
        env_file_name: str = env_file_name_default,
        con_info: dict = None,
        headers: dict = None
):
    """
    上传内容（二进制对象）
    :param oss_filename: 上传oss后的文件名
    :param data: 待上传对象，二进制内容
    :param custom_host: 自定义域名
    :param env_file_name: 环境文件名
    :param con_info: 环境
    :param headers: {'Cache-Control':'max-age=5'}表示缓存有效期为5秒
    """
    # ---------------- 固定设置 ----------------
    if con_info is None:
        con_info = make_con_info(env_file_name=env_file_name)
    else:
        pass
    # ---------------- 固定设置 ----------------
    basic = Basics(con_info=con_info)
    res = basic.upload_object(
        key=oss_filename,
        data=data,
        headers=headers
    )
    base_url = 'https://%s.%s/%s' % (basic.bucket_name, basic.endpoint, oss_filename)
    if custom_host is None:
        custom_http_url = ''
        custom_https_url = ''
    else:
        custom_http_url = 'http://%s/%s' % (custom_host, oss_filename)
        custom_https_url = 'https://%s/%s' % (custom_host, oss_filename)
    response = {
        'status': res.status,
        'e_tag': res.etag,  # Etag
        'version_id': res.versionid,  # 版本信息
        'base_url': base_url,
        'custom_host': custom_host,
        'custom_http_url': custom_http_url,
        'custom_https_url': custom_https_url
    }
    return response
