import logging
import os
import boto3
from botocore.exceptions import ClientError
from io import StringIO
import pandas as pd

def set_location(local_file_path, folders=None):
    print('Expected format: [pair, day, hour] or similar')
    clean_f = []
    if folders is not None:
        for subfolder in folders:
            clean_f.append(subfolder.replace(' ', '_'))
        return '/'.join(clean_f) + '/' + os.path.basename(local_file_path)
    else:
        print('No subfolders found - file will be located in main')
        return os.path.basename(local_file_path)

class CryptoS3Connector:
    """
    -- Methods included in boto --
​
    Create key inside a bucket:
        k = Key(self.resource.Bucket('bucket_name'))
​
    Set up key location (use randomize_key):
        k.key = 'location'
​
    Access existing key:
        k = self.resource.Bucket('bucket_name').get_key('key_name')
​
    Set contents from string:
        k.set_contents_from_string('string')
​
    Return content string:
        k.get_contents_as_string()
​
    Upload a file from local_path:
        k.set_contents_from_filename('local_path')
​
    Upload a local file into a bucket (one liner)
        self.resource.Bucket(bucket_name).upload_file(Filename='local_path', Key='your_key')
​
    Upload a local file into a bucket (alternatively):
        self.client.put_object(Bucket = 'bucket_name', Body = 'body', Key = 'my_key')
​
    Get contents to local_path:
        k.get_contents_to_filename('local_path')
​
    Get list of all keys in bucket:
        mybucket.list()
​
    Get list of all buckets (resource-greedy):
        self.client.get_all_buckets()
    """

    def __init__(self, aws_access_key_id, aws_secret_access_key, region=None):
        session = boto3.Session(aws_access_key_id, aws_secret_access_key)
        self.resource = session.resource('s3', region_name=region)
        self.client = session.client('s3', region_name=region)
        self.subfolders = None
        self.region = region

    def bucket_exist(self, bucket_name):
        return False if self.resource.Bucket(bucket_name).creation_date is None else True

    def create_bucket(self, bucket_name, region=None):
        region = self.region
        if region is None:
            try:
                self.client.create_bucket(Bucket=bucket_name)
            except ClientError as e:
                logging.error(e)
                return False
        else:
            location = {'LocationConstraint': region}
            self.client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)
        print('-- Done -- ')

    def set_current_folder(self, folders):
        self.subfolders=folders

    def upload_content(self, bucket, local_file_path):
        '''
        if not bool(os.system("'FileChunkIO' in sys.modules")):
            raise SystemError('<< pip install FileChunkIO >> required')
​
        file_size = os.stat(local_file_path).st_size
        b = self.resource.Bucket(bucket)
        s3_file_name = set_location(local_file_path, self.subfolders)
        mp = b.initiate_multipart_upload(s3_file_name)
        chunk_count = int(math.ceil(file_size / float(max_chunk_size)))
        for i in range(chunk_count):
            offset = chunk_size * i
            bytes_ = min(chunk_size, source_size - offset)
            with FileChunkIO(local_file_path, 'r', offset=offset, bytes=bytes_) as fp:
                mp.upload_part_from_file(fp, part_num=i + 1)
        mp.complete_upload()
        '''
        key_location = set_location(local_file_path, self.subfolders)
        ExtraArgs = {'ContentType': os.path.splitext(local_file_path)[1], 'ACL': "public-read"}
        self.client.upload_file(local_file_path, bucket, key_location, ExtraArgs)
        print('-- Done uploading ' + os.path.basename(local_file_path) + ' @key ' + key_location)


    def download_content(self,bucket, filename):
        obj = self.client.get_object(Bucket=bucket, Key=filename)
        content = obj['Body'].read()
        #results = [r for r in obj['Body'].iter_lines()]
        #return results
        return content

    def download_dataframe_from_csv(self, bucket, filename, sep = ','):
        obj = self.client.get_object(Bucket=bucket, Key=filename)
        bytes_data_csv = obj['Body'].read()
        string_data_csv = StringIO(str(bytes_data_csv, 'utf-8'))
        dataframe = pd.read_csv(string_data_csv, sep=sep)
        return dataframe


    def upload_file(self, bucket, local_file_path):
        '''
        if not bool(os.system("'FileChunkIO' in sys.modules")):
            raise SystemError('<< pip install FileChunkIO >> required')
​
        file_size = os.stat(local_file_path).st_size
        b = self.resource.Bucket(bucket)
        s3_file_name = set_location(local_file_path, self.subfolders)
        mp = b.initiate_multipart_upload(s3_file_name)
        chunk_count = int(math.ceil(file_size / float(max_chunk_size)))
        for i in range(chunk_count):
            offset = chunk_size * i
            bytes_ = min(chunk_size, source_size - offset)
            with FileChunkIO(local_file_path, 'r', offset=offset, bytes=bytes_) as fp:
                mp.upload_part_from_file(fp, part_num=i + 1)
        mp.complete_upload()
        '''
        key_location = set_location(local_file_path, self.subfolders)
        ExtraArgs = {'ContentType': os.path.splitext(local_file_path)[1], 'ACL': "public-read"}
        self.client.upload_file(local_file_path, bucket, key_location, ExtraArgs)
        print('-- Done uploading ' + os.path.basename(local_file_path) + ' @key ' + key_location)

    def list_files(self, bucket):
        b = self.resource.Bucket(bucket)
        for key in b.objects.all():
            print(key)

    def download_file(self, bucket, file_name, target_local_path):
        self.client.download_file(bucket, set_location(file_name, self.subfolders), target_local_path)
        print('-- Done -- ')