import base64
from typing import Any

from kikyo_api import KikyoClient
from kikyo_api.errors import KikyoAPIError
from kikyo_api.nsclient.base import NamespacedClient
from kikyo_api.utils import read_json_data


class OssClient(NamespacedClient):
    """
    提供对象存储服务
    """

    api_prefix = '/api/oss'

    def __init__(self, client: KikyoClient):
        super().__init__(client)

        self.object_link_template = self._get_object_link_template()

    def bucket(self, name: str) -> 'Bucket':
        """获取bucket

        :param name: bucket名称
        """
        return Bucket(name, self)

    def _get_object_link_template(self) -> str:
        data = read_json_data(
            self.session.get(f'{self.api_prefix}/object-link-template'),
        )
        return data['object_link_template']


class Bucket:
    def __init__(self, bucket: str, client: OssClient):
        self._bucket = bucket
        self._client = client

    def get_object_link(self, key: str) -> str:
        """
        获取对象的下载链接

        :param key: 文件的名称
        """

        return self._client.object_link_template.format(bucket=self._bucket, key=key)

    def put_object(self, key: str, data: Any):
        """
        上传对象

        :param key: 对象的key
        :param data: 对象数据
        """
        if isinstance(data, bytes):
            _type = 'bytes'
            _data = base64.a85encode(data).decode()
        elif isinstance(data, str):
            _type = 'str'
            _data = data
        else:
            raise KikyoAPIError(f"Only support 'bytes' and 'str', but got: {type(data)}")
        read_json_data(
            self._client.session.put(
                f'{self._client.api_prefix}/buckets/{self._bucket}',
                json={
                    'type': _type,
                    'data': _data,
                },
                params={
                    'key': key,
                },
            )
        )

    def get_object(self, key: str) -> Any:
        """
        获取对象
        :param key: 对象的key
        """
        data = read_json_data(
            self._client.session.get(
                f'{self._client.api_prefix}/buckets/{self._bucket}',
                params={
                    'key': key,
                },
            )
        )
        _type = data['type']
        _data = data['data']
        if _type == 'str':
            return _data
        return base64.a85decode(_data.encode())
