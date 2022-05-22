from sqlite3 import DataError
import traceback
import httpx
from aiohttp_retry import ExponentialRetry, RetryClient
from aiofile import async_open

from qiniu import put_file, put_data, Auth, etag
from qiniu import BucketManager, build_batch_delete
from qiniu import Zone, set_default

from hamunafs.backends.base import BackendBase

class Qiniu(BackendBase):
    def __init__(self, cfg):
        key, secret, domain, default_bucket = cfg['key'], cfg['secret'], cfg['domain'], cfg['default_bucket']
        self.auth = Auth(key, secret)
        self.domain = domain
        self.default_bucket = default_bucket
        self.bucket = BucketManager(self.auth)
    
    def get_token(self, filename):
        return self.auth.upload_token(self.default_bucket, filename)
    
    def geturl(self, entrypoint):
        bucket, bucket_name = entrypoint.split('/')
        return 'http://{}/{}_{}'.format(self.domain, bucket, bucket_name)

    def put(self, file, bucket, bucket_name, tmp=True):
        try:
            if tmp:
                _bucket = 'tmp_file_' + bucket
            else:
                _bucket = bucket
            b_name = '{}_{}'.format(_bucket, bucket_name)
            print('acquiring upload token....')
            token = self.auth.upload_token(self.default_bucket, b_name)
            print('upload token acquired -> {}'.format(token))
            print('uploading...')
            ret, info = put_file(token, b_name, file)
            if ret is not None:
                print('upload success.')
                return True, '{}/{}'.format(_bucket, bucket_name)
            print('upload failed.')
            return False, '上传失败'
        except Exception as e:
            traceback.print_exc()
            return False, str(e)
    
    async def put_async(self, file, bucket, bucket_name, tmp=True):
        return self.put(file, bucket, bucket_name, tmp)

    def put_buffer(self, buffer, bucket, bucket_name):
        try:
            b_name = '{}_{}'.format(bucket, bucket_name)
            token = self.auth.upload_token(self.default_bucket, b_name)
            ret, info = put_data(token, b_name, buffer)
            if ret is not None:
                return True, '{}/{}'.format(bucket, bucket_name)
            return False, '上传失败'
        except Exception as e:
            return False, str(e)

    async def put_buffer_async(self, buffer, bucket, bucket_name):
        return self.put_buffer(buffer, bucket, bucket_name)

    def get(self, download_path, bucket, bucket_name, tries=0):
        try:
            if tries >= 3:
                return False, '下载出错'
            else:
                url = 'http://{}/{}'.format(self.domain, '{}_{}'.format(bucket, bucket_name))
                print(url)
                with httpx.stream('GET', url) as response:
                    if response.status_code == 200:
                        with open(download_path, mode='wb') as f:
                            for chunk in response.iter_bytes():
                                f.write(chunk)
                    else:
                        raise DataError()
                return True, download_path
        except Exception as e:
            if tries >= 3:
                return False, str(e)
            else:
                return self.get(download_path, bucket, bucket_name, tries+1)

    async def get_async(self, download_path, bucket, bucket_name):
        try:
            url = 'http://{}/{}'.format(self.domain, '{}_{}'.format(bucket, bucket_name))
            print(url)
            retry_opts = ExponentialRetry(attempts=3)
            async with RetryClient(retry_options=retry_opts) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        async with async_open(download_path, mode='wb') as f:
                            while True:
                                chunk = await response.content.read(4096)
                                if not chunk:
                                    break
                                await f.write(chunk)
                    else:
                        raise DataError()
            return True, download_path
        except Exception as e:
            return False, str(e)


            
