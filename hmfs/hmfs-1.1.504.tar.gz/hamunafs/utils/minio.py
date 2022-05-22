try:
    from contextlib import AsyncExitStack
except:
    from async_exit_stack import AsyncExitStack
import traceback
from minio import Minio

from aiobotocore.session import get_session
from aiofile import async_open


class MinioAgent:
    def __init__(self, endpoint, acs_key, secret_key, secure=True, location='default'):
        self.client = Minio(endpoint, access_key=acs_key,
                            secret_key=secret_key, secure=secure, region=location)
        self.location = location

    def create_bucket_if_not_exists(self, bucket_name, location):
        try:
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name, location=location)

            return True
        except Exception as e:
            traceback.print_exc()
            return False

    def upload_file(self, path, bucket, bucket_filename, tries=0):
        try:
            if self.create_bucket_if_not_exists(bucket, self.location):
                self.client.fput_object(bucket, bucket_filename, path)
                return True, 'minio://{}/{}'.format(bucket, bucket_filename)
            else:
                print('創建bucket失敗: {}'.format(bucket))
                return False, '創建bucket失敗'
        except Exception as e:
            if tries > 3:
                return False, e
            else:
                return self.upload_file(path, bucket, bucket_filename, tries+1)

    def upload_file_by_buffer(self, buffer, bucket, bucket_filename, tries=0):
        try:
            if self.create_bucket_if_not_exists(bucket, self.location):
                self.client.put_object(
                    bucket, bucket_filename, buffer, len(buffer.getvalue()))
                return True, 'minio://{}/{}'.format(bucket, bucket_filename)
            else:
                return False, '創建bucket失敗'
        except Exception as e:
            if tries > 3:
                return False, e
            else:
                return self.upload_file_by_buffer(buffer, bucket, bucket_filename, tries+1)

    def download_file(self, path, bucket, bucket_filename, tries=0):
        try:
            self.client.fget_object(bucket, bucket_filename, path)
            return True, path
        except Exception as e:
            if tries > 5:
                return False, e
            else:
                return self.download_file(path, bucket, bucket_filename, tries+1)

    def delete(self, bucket, bucket_name, tries):
        try:
            self.client.remove_object(bucket, bucket_name)
            return True, None
        except Exception as e:
            if tries > 5:
                return False, e
            else:
                return self.delete(bucket, bucket_name, tries + 1)

    def exists(self, bucket, bucket_name):
        meta = self.client.stat_object(bucket, bucket_name)

        return meta is not None


class MinioAgentAsync:
    def __init__(self, endpoint, acs_key, secret_key, secure=True, location='default', loop=None):
        self._exit_stack = AsyncExitStack()
        
        print('EndPoint: {}'.format(endpoint))
        session = get_session()
        self.client = loop.run_until_complete(self._exit_stack.enter_async_context(
            session.create_client('s3',
                                  use_ssl=False,
                                  verify=False,
                                  aws_secret_access_key=secret_key,
                                  aws_access_key_id=acs_key,
                                  endpoint_url=endpoint)
        ))
        self.location = location

    async def create_bucket_if_not_exists(self, bucket_name, location):
        try:
            await self.client.create_bucket(Bucket=bucket_name)

            return True
        except Exception as e:
            print(e)
            if 'BucketAlreadyOwnedByYou' in str(type(e)):
                return True

            return False

    async def upload_file(self, path, bucket, bucket_filename, tries=0):
        try:
            if await self.create_bucket_if_not_exists(bucket, self.location):
                resp = await self.client.put_object(Bucket=bucket, Key=bucket_filename, Body=open(path, 'rb'))
                if 'ETag' in resp:
                    return True, 'minio://{}/{}'.format(bucket, bucket_filename)
                else:
                    return False, '上传文件错误'
            else:
                print('創建bucket失敗: {}'.format(bucket))
                return False, '创建bucket失败'
        except Exception as e:
            if tries > 3:
                return False, e
            else:
                return self.upload_file(path, bucket, bucket_filename, tries+1)

    async def upload_file_by_buffer(self, buffer, bucket, bucket_filename, tries=0):
        try:
            if self.create_bucket_if_not_exists(bucket, self.location):
                resp = await self.client.put_object(Bucket=bucket, Key=bucket_filename, Body=buffer)
                if 'ETag' in resp:
                    return True, 'minio://{}/{}'.format(bucket, bucket_filename)
                else:
                    return False, '上传错误'
            else:
                return False, '创建bucket失败'
        except Exception as e:
            if tries > 3:
                return False, e
            else:
                return self.upload_file_by_buffer(buffer, bucket, bucket_filename, tries+1)

    async def download_file(self, path, bucket, bucket_filename, tries=0):
        try:
            response = await self.client.get_object(Bucket=bucket, Key=bucket_filename)
            async with async_open(path, 'wb') as f:
                async with response['Body'] as stream:
                    await f.write(await stream.read())
            return True, path
        except Exception as e:
            if tries > 5:
                return False, e
            else:
                return self.download_file(path, bucket, bucket_filename, tries+1)

    async def delete(self, bucket, bucket_name, tries):
        try:
            await self.client.delete_object(Bucket=bucket, Key=bucket_name)
            return True, None
        except Exception as e:
            if tries > 5:
                return False, e
            else:
                return self.delete(bucket, bucket_name, tries + 1)

    async def exists(self, bucket, bucket_name):
        meta = await self.client.get_object_acl(bucket, bucket_name)

        return meta is not None
