import math
import os

import tornado.options
from filechunkio import FileChunkIO
from ks3.connection import Connection
from ks3.key import Key
from ks3.prefix import Prefix


class Ks3Oss:
    def __init__(self, **kwargs):
        if not kwargs.get("access_key_id"):
            kwargs.update({"access_key_id": tornado.options.options.ks3_connect_config.get("access_key_id")})
        if not kwargs.get("access_key_secret"):
            kwargs.update({"access_key_secret": tornado.options.options.ks3_connect_config.get("access_key_secret")})
        if not kwargs.get("host"):
            kwargs.update({"host": tornado.options.options.ks3_connect_config.get("host")})
        bucket_name = kwargs.pop("bucket_name", None)
        self.client = Connection(**kwargs)
        if bucket_name is not None:
            self.instance = self.client.get_bucket(bucket_name)
        else:
            self.instance = None

    def create_bucket(self, bucket_name, **kwargs):
        bucket = self.client.create_bucket(bucket_name=bucket_name, **kwargs)
        return bucket

    def list_buckets(self):
        buckets = self.client.get_all_buckets()
        return [b.name for b in buckets]

    def delete_bucket(self, bucket_name):
        return self.client.delete_bucket(bucket_name)

    def save(self, key, bucket_name="", content_type="string", protocol="https", domain="ksyun.com",
             region="ks3-cn-beijing", **kwargs):
        if self.instance is None:
            self.instance = self.client.get_bucket(bucket_name)
        k = self.instance.new_key(key)
        ret = None
        if content_type == "string":
            ret = k.set_contents_from_string(**kwargs)
        elif content_type == "file":
            ret = k.set_contents_from_file(**kwargs)
        elif content_type == "filename":
            ret = k.set_contents_from_filename(**kwargs)
        elif content_type == "network":
            ret = k.fetch_object(**kwargs)
        if ret:
            if ret.status == 200:
                return f'{protocol}://{bucket_name}.{region}.{domain}/{key}'
            else:
                return False
        else:
            return False

    def get_url(self, key, bucket_name="", region="ks3-cn-beijing", domain="ksyun.com", protocol="https"):
        if self.instance is None:
            self.instance = self.client.get_bucket(bucket_name)
        if self.instance.get_key(key):
            return f'{protocol}://{bucket_name}.{region}.{domain}/{key}'
        else:
            return None

    def get_file(self, key, bucket_name="", file_path=None):
        if self.instance is None:
            self.instance = self.client.get_bucket(bucket_name)
        k = self.instance.get_key(key)
        if file_path:
            k.get_contents_to_filename(file_path)
            return True
        else:
            contents = k.get_contents_as_string().decode()
            return contents

    def get_key(self, key, bucket_name=""):
        if self.instance is None:
            self.instance = self.client.get_bucket(bucket_name)
        k = self.instance.get_key(key)
        return k

    def delete_file(self, key, bucket_name=None):
        if self.instance is None:
            self.instance = self.client.get_bucket(bucket_name)
        res = self.instance.delete_key(key)
        return res

    def list_file(self, bucket_name, delimiter="/"):
        if self.instance is None:
            self.instance = self.client.get_bucket(bucket_name)
        keys = self.instance.list(delimiter=delimiter)
        files = list()
        dirs = list()
        for k in keys:
            if isinstance(k, Key):
                files.append(k.name)
            elif isinstance(k, Prefix):
                dirs.append(k.name)

        for p in dirs:
            keys = self.instance.list(prefix=p)
            for k in keys:
                if isinstance(k, Key):
                    files.append(k.name)
                elif isinstance(k, Prefix):
                    dirs.append(k.name)
        return dirs, files

    def get_bucket_acl(self, bucket_name=None):
        if self.instance is None:
            self.instance = self.client.get_bucket(bucket_name)
        acl = self.instance.get_acl()
        return acl

    def set_bucket_acl(self, bucket_name=None, *args, **kwargs):
        if self.instance is None:
            self.instance = self.client.get_bucket(bucket_name)
        return self.instance.set_acl(*args, **kwargs)

    def get_bucket_policy(self, bucket_name=None):
        if self.instance is None:
            self.instance = self.client.get_bucket(bucket_name)
        policy = self.instance.get_bucket_policy()
        return policy

    def set_bucket_policy(self, policy, bucket_name=None, headers=None):
        if self.instance is None:
            self.instance = self.client.get_bucket(bucket_name)
        return self.instance.set_bucket_policy(policy, headers)

    def delete_bucket_policy(self, bucket_name=None, headers=None):
        if self.instance is None:
            self.instance = self.client.get_bucket(bucket_name)
        return self.instance.delete_bucket_policy(headers)

    def multipart_upload(self, file_path, chunk_size, bucket_name=None, **kwargs):
        if self.instance is None:
            self.instance = self.client.get_bucket(bucket_name)
        file_size = os.stat(file_path).st_size
        mp = self.instance.initiate_multipart_upload(os.path.basename(file_path), **kwargs)
        chunk_count = int(math.ceil(file_size * 1.0 / chunk_size * 1.0))
        for i in range(chunk_count):
            offset = chunk_size * i
            bytes = min(chunk_size, file_size - offset)
            with FileChunkIO(file_size, 'r', offset=offset, bytes=bytes) as fp:
                mp.upload_part_from_file(fp, part_num=i + 1)
        ret = mp.complete_upload()
        return ret

    def list_multipart_upload_parts(self, key, bucket_name=None, **kwargs):
        if self.instance is None:
            self.instance = self.client.get_bucket(bucket_name)
        mp = self.instance.initiate_multipart_upload(key, **kwargs)
        return mp.get_all_parts()

    def list_multipart_uploads(self, key, bucket_name=None, **kwargs):
        if self.instance is None:
            self.instance = self.client.get_bucket(bucket_name)
        return self.instance.list_multipart_uploads(key, **kwargs)

    def generate_url(self, key, second, bucket_name=None):
        if self.instance is None:
            self.instance = self.client.get_bucket(bucket_name)
        k = self.instance.get_key(key)
        if k:
            url = k.generate_url(second)
            return url
        else:
            return None

    def get_presigned_url(self, key, second, bucket_name=None, expires_in_absolute=False):
        if self.instance is None:
            self.instance = self.client.get_bucket(bucket_name)
        k = self.instance.new_key(key)
        if k:
            url = k.get_presigned_url(second, expires_in_absolute=expires_in_absolute)
            return url
        else:
            return None

    def modify_object(self, bucket_name=None, *args, **kwargs):
        if self.instance is None:
            self.instance = self.client.get_bucket(bucket_name)
        return self.instance.copy_key(*args, **kwargs)
