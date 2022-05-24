import boto3
import botocore
from boto3.session import Session

# boto3 该开发工具包由两个关键的 Python 包组成：
# Botocore（提供在 Python 开发工具包和 AWS CLI 之间共享的低级功能的库）
# 和 Boto3（实现 Python 开发工具包本身的包）


"""
aws_access_key_id = 'minioa'
aws_secret_access_key = 'minio123'
endpoint_url = 'http://192.168.31.164:9000'
bbt = BaseBoto3(aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                endpoint_url=endpoint_url)
bbt.conn_session()
bbt.set_is_low_level(False)
bbt.get_client()
print("**********************")
print(bbt.delete_buckets("test1"))
# bbt.set_is_low_level(False)
# bbt.get_client()
# print("**********************")
# print(bbt.create_buckets("create2"))
"""


class BaseBoto3(object):

    def __init__(self, aws_access_key_id="", aws_secret_access_key="", endpoint_url=""):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.endpoint_url = endpoint_url
        self.session = None
        self.client = None
        self.is_low_level = False
        self.bucket = None

    def set_is_low_level(self, is_low_level):
        self.is_low_level = is_low_level
        return self

    def set_aws_access_key_id(self, aws_access_key_id):
        self.aws_access_key_id = aws_access_key_id
        return self

    def set_aws_secret_access_key(self, aws_secret_access_key):
        self.aws_secret_access_key = aws_secret_access_key
        return self

    def set_endpoint_url(self, endpoint_url):
        self.endpoint_url = endpoint_url
        return self

    def conn_session(self):
        self.session = Session(aws_access_key_id=self.aws_access_key_id,
                               aws_secret_access_key=self.aws_secret_access_key)
        return self.session

    def get_client(self):
        assert self.session is not None
        if self.is_low_level:
            # 根据名称创建低级服务客户端
            # botocore.client.S3
            self.client = self.session.client('s3', endpoint_url=self.endpoint_url)
            print(type(self.client))
        else:
            # boto3.resources.factory.s3.ServiceResource
            # 按名称创建资源服务客户端
            self.client = self.session.resource('s3', endpoint_url=self.endpoint_url)
            print(type(self.client))

    def get_all_buckets(self):
        """
        获取所有的桶信息
        :return:
        """
        if self.is_low_level is False:
            return self.client.buckets.all()
        else:
            return self.client.list_buckets()

    def create_buckets(self, buckets_name):
        """

        :param buckets_name:
        :return:
        如果get_client 使用 client 返回
        {'ResponseMetadata': {'RequestId': '16BC90EED4A433C4', 'HostId': '', 'HTTPStatusCode': 200, 'HTTPHeaders': {'accept-ranges': 'bytes', 'content-length': '0', 'content-security-policy': 'block-all-mixed-content', 'location': '/create1', 'server': 'MinIO', 'strict-transport-security': 'max-age=31536000; includeSubDomains', 'vary': 'Origin, Accept-Encoding', 'x-amz-request-id': '16BC90EED4A433C4', 'x-content-type-options': 'nosniff', 'x-xss-protection': '1; mode=block', 'date': 'Wed, 01 Dec 2021 07:28:39 GMT'}, 'RetryAttempts': 0}, 'Location': '/create1'}
        如果resource 使用 client 返回
        s3.Bucket(name='create2')
        """
        assert buckets_name.find("_") == -1, "新建一个bucket桶(bucket name 中不能有_下划线)"
        # 新建一个bucket桶(bucket name 中不能有_下划线)
        return self.client.create_bucket(Bucket=buckets_name)

    def delete_buckets(self, bucket_name):
        """
        删除桶 删除bucket(只能删除空的bucket)
        :return:
        """
        if self.is_low_level is False:
            bucket = self.client.Bucket(bucket_name)
            response = bucket.delete()
        else:
            response = self.client.delete_bucket(Bucket=bucket_name)
        return response

    def get_bucket(self, bucket_name):
        """
        获取 bucket 对象
        :param bucket_name:
        :return:
        """
        if self.is_low_level is False:
            self.bucket = self.client.Bucket(bucket_name)
            return self.bucket

    def get_all_obs_filter(self, Prefix):
        """
        Prefix 为匹配模式
        例：列出前缀为 haha 的文件
        Prefix='haha'
        :param Prefix:
        :return: 可以调用 obj.key
        """
        if not self.is_low_level:
            for obj in self.bucket.objects.filter(Prefix=Prefix):
                yield obj
        else:
            raise Exception("请设置 is_low_level 为 False")

    def get_object(self, bucket_name):
        """
        会返回包括目录在内的所有对象
        :param bucket_name:
        :return:
        """
        if self.is_low_level is False:
            bucket = self.client.Bucket(bucket_name)
            # boto3.resources.collection.s3.Bucket.objectsCollection
            all_obj = bucket.objects.all()
            return all_obj
            # for obj in bucket.objects.all():
            #     print('obj name:%s' % obj.key)
        else:
            return self.client.list_objects(Bucket=bucket_name)

    def upload_file(self, local_file, bucket_name, key):
        """
        # key 桶中的位置 test1/test.pdf
        :param local_file:  本地文件路径
        :param bucket_name: 桶名
        :param key: 远程文件路径
        :return:
        """

        if self.is_low_level is False:
            self.client.Bucket(bucket_name).upload_file(local_file, key)
        else:
            self.client.upload_file(local_file, bucket_name, key)

    def upload_fileobj(self, fileobj, bucket_name, key):
        # fileobj 字节流
        if self.is_low_level is False:
            self.client.Bucket(bucket_name).upload_file(fileobj, key)
        else:
            self.client.upload_file(fileobj, bucket_name, key)

    def download_file(self, local_file, bucket_name, key):
        if self.is_low_level is False:
            self.client.Bucket(bucket_name).download_file(key, local_file)
        else:
            self.client.download_file(bucket_name, key, local_file)

    def download_fileobj(self, fileobj, bucket_name, key):
        if self.is_low_level is False:
            self.client.Bucket(bucket_name).download_fileobj(key, fileobj)
        else:
            self.client.download_fileobj(bucket_name, key, fileobj)
