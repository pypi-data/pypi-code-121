# -*- coding: utf8 -*-
import sys
import oss2


class StoreOSS(object):
    """
    阿里云OSS操作
    Args:
        key_id：用户访问密钥AccessKeyId，用于签名
        key_secret：用户访问密钥AccessKeySecret，用于签名
        endpoint：访问域名
        bucket_name：存储空间（Bucket）名称
        connect_timeout：连接超时时间
    """
    def __init__(self, key_id, key_secret, endpoint, bucket_name, connect_timeout=None):
        self.bucket = oss2.Bucket(oss2.Auth(key_id, key_secret), endpoint, bucket_name, connect_timeout)

    def put(self, key, data):
        """
        上传数据对象
        Args:
            key：上传到OSS的文件名
            data：bytes，str或file-like object，待上传的内容
        """
        result = self.bucket.put_object(key, data)
        return result

    def get(self, key, filename=None):
        """
        下载数据对象
        Args:
            key：下载对象在OSS的文件名
            filename：要保存的文件名，如果未传递则返回类文件对象
        """
        if filename is None:
            return self.bucket.get_object(key)
        else:
            return self.bucket.get_object_to_file(key, filename)

    def delete(self, key):
        """
        删除数据对象
        Args:
            key：对象在OSS的文件名
        """
        return self.bucket.delete_object(key)

    def batch_delete(self, key_list):
        """
        批量删除数据对象
        Args:
            key_list：数据对象在OSS的文件名list
        """
        for i in range(0, len(key_list), 1000):
            self.bucket.batch_delete_objects(key_list[i:i+1000])


def test():
    oss = StoreOSS("BWUNG5LjYOHpKyr1", "JWyFaaDz2ydzz1bvFRggIdjRknjXhx", 'http://oss-cn-shanghai.aliyuncs.com', "cluster2016")
    oss.put('test.txt', 'just a test')
    r = oss.get('test.txt')
    print(r.read())
    oss.delete('test.txt')


if __name__ == "__main__":
    test()
