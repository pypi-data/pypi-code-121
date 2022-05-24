from pypers.core.interfaces.storage.base import StorageBase
import os
import boto3
from pypers.core.interfaces.storage.test import MockS3
import json


class S3Storage:
    def __init__(self):
        self.protocol = 's3'
        self.buckets = {}

    def get_storage(self, bucket):
        if bucket not in self.buckets.keys():
            self.buckets[bucket] = S3Interface(bucket)
        return self.buckets[bucket]

    def do_store(self, file, bucket, location):
        s3_bucket = self.get_storage(bucket)
        s3_bucket.save_file_with_location(file, location)
        storage_location = self.protocol + '://' + os.path.join(bucket, location)
        return storage_location

    def get_file(self, source_file, dest_file):
        file_parts = source_file.replace("%s://" % self.protocol, '').split('/')
        bucket_name = file_parts[0]
        source_file = os.path.join(*file_parts[1:])
        s3_bucket = self.get_storage(bucket_name)
        return s3_bucket.get_file_by_key(source_file, save_to_file=dest_file)

    def remove_old(self, bucket_name, key, current_version, delete_all=False):
        s3_bucket = self.get_storage(bucket_name)
        all_versions = s3_bucket.list_files(type=key)
        for version in all_versions:
            if current_version not in version or delete_all:
                s3_bucket.delete_key(version)

class S3Interface(StorageBase):
    """S3 manager"""

    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
        if os.environ.get("S3_URL", None):
            endpoint_url = os.environ['S3_URL']
        else:
            endpoint_url = None
        if os.environ.get("GITHUB_TOKEN", None):
            self.s3 = MockS3()
        else:
            self.s3 = boto3.client('s3', endpoint_url=endpoint_url)
        super(S3Interface, self).__init__()

    def create_space_if_not_exists(self):
        buckets = self.s3.list_buckets()['Buckets']
        if self.bucket_name not in [b['Name'] for b in buckets]:
            self.s3.create_bucket(Bucket=self.bucket_name)

    def save_file_with_location(self, local_path, key, string_input=None):
        if string_input:
            data = string_input
        else:
            with open(local_path, 'rb') as f:
                data = f.read()
        retrys = 0
        while retrys < 3:
            try:
                self.s3.put_object(Body=data, Bucket=self.bucket_name,
                                   Key=key)
                return
            except Exception as e:
                retrys += 1
                if retrys >= 3:
                    raise e

    def save_file(self, type, collection, filename, local_path,
                  string_input=None):
        if string_input:
            data = string_input
        else:
            with open(local_path, 'rb') as f:
                data = f. read()
        key = '%s/%s/%s' % (type, collection, filename)
        retrys = 0
        while retrys < 3:
            try:
                self.s3.put_object(Body=data, Bucket=self.bucket_name,
                                   Key=key)
                return
            except Exception as e:
                retrys += 1
                if retrys >= 3:
                    raise e


    def get_objects(self, type, collection, full=False):
        key = '%s/%s/' % (type, collection)
        results = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=key)
        if full:
            return results.get('Contents', [])
        return [res['Key'] for res in results.get('Contents', [])]

    def get_file(self, type, collection, filename, save_to_file=None):
        key = '%s/%s/%s' % (type, collection, filename)
        response = self.s3.get_object(Bucket=self.bucket_name, Key=key)
        if save_to_file:
            with open(save_to_file, 'wb') as f:
                f.write(response['Body'].read())
        # returns stream reader (should used with read)
        else:
            return response['Body']

    def get_file_by_key(self, key, save_to_file=None):
        if key == None:
            return {}
        retrys = 0
        while retrys < 3:
            try:
                response = self.s3.get_object(Bucket=self.bucket_name, Key=key)
                break
            except Exception as e:
                retrys += 1
                if retrys >= 3:
                    raise e
        if save_to_file:
            with open(save_to_file, 'wb') as f:
                f.write(response['Body'].read())
        else:
            return json.load(response['Body'])

    def delete_key(self, key):
        try:
            self.s3.delete_object(Bucket=self.bucket_name, Key=key)
        except:
            pass

    def list_files(self, type=None, collection=None):
        files = []
        filter = ''
        if type:
            filter = os.path.join(filter, type)
        if collection:
            filter = os.path.join(filter, collection)
        for key in self.s3.list_objects(Bucket=self.bucket_name).get('Contents', {}):
            if filter != '':
                if filter in key['Key']:
                    files.append(key)
            else:
                files.append(key)
        return files

