from zs3 import logger
from zs3.config import Config
import boto3
from zs3.error_handler import parse_error
from botocore.config import Config as BConfig
import requests


class S3:
    def __init__(self, connection_parameter=None, b_config=None):
        logger.debug('[S3]: Initiating S3 Connection Class')
        self._connection_parameter = connection_parameter
        if self._connection_parameter:
            self.set_connection_parameter(**connection_parameter)
        self._resource = None
        self._config = BConfig(retries={'max_attempts': 3, 'mode': 'standard'})

    def set_connection_parameter(self, **kwargs):
        self._connection_parameter = {
            'region': Config.AWS['region'] if not kwargs.get('region') else kwargs.get('region'),
            "s3_key_id": Config.AWS['s3_key_id'] if not kwargs.get('s3_key_id') else kwargs.get('s3_key_id'),
            "s3_key_secret": Config.AWS['s3_key_secret'] if not kwargs.get('s3_key_secret') else kwargs.get(
                's3_key_secret'),
            "s3_bucket_name": Config.AWS['s3_bucket_name'] if not kwargs.get('s3_bucket_name') else kwargs.get(
                's3_bucket_name'),
        }

    def get_connection_parameter(self):
        return self._connection_parameter

    @property
    def connection(self):
        if self._resource is None:
            self.connect()
        return self._resource

    def connect(self):
        if self._connection_parameter is None:
            self.set_connection_parameter()
        try:
            logger.debug('[S3]: Creating s3 connection')
            s3_resource = boto3.resource('s3', region_name=self._connection_parameter['region'],
                                         aws_access_key_id=self._connection_parameter['s3_key_id'],
                                         aws_secret_access_key=self._connection_parameter['s3_key_secret'],
                                         config=self._config)
            bucket = s3_resource.meta.client.head_bucket(Bucket=self._connection_parameter['s3_bucket_name'])

            if bucket.get('ResponseMetadata') and bucket.get('ResponseMetadata').get('HTTPStatusCode') == 200:
                self._resource = s3_resource
                logger.info(f'[S3]: Connection Successful. Connection={self._resource}')
            else:
                raise Exception(f'Unable to connect to bucket={self._connection_parameter["s3_bucket_name"]}')
        except Exception as e:
            self._resource = None
            logger.error(f'[S3]: connection issue, conn={self._resource}', exc_info=True)
            raise Exception(f'[S3]: Connection Error with S3. Error={e}')

    def url_upload_to_s3(self, upload_from, object_id, folder_name=None, bucket=None, public_read=True,
                         extra_args=None):
        r = requests.get(upload_from, stream=True)
        bucket_name = bucket if bucket is not None else Config.AWS['s3_upload_bucket_name']
        key = f'{folder_name}/{str(object_id)}' if folder_name else str(object_id)
        bucket = self.connection.Bucket(bucket_name)
        upload_to = f'https://{bucket_name}.s3.{self._connection_parameter["region"]}.amazonaws.com/{key}'
        args = {'ACL': 'public-read'} if public_read else {}
        if extra_args:
            args = args | extra_args
        try:
            bucket.upload_fileobj(r.raw, key, ExtraArgs=args)
            logger.info(f'[S3] Success {upload_from}->{upload_to}')
        except Exception as e:
            logger.error(f'[S3] Failed {upload_from}->{upload_to}', exc_info=True)
            return False, parse_error('ZE002', details=f'{upload_from}->{upload_to}', description=str(e))

        return True, {'message': 's3 upload success',
                      'upload_to': upload_to
                      }

    def file_upload_to_s3(self, upload_from, object_id, folder_name=None, bucket=None, public_read=True,
                          extra_args=None):
        bucket_name = bucket if bucket is not None else Config.AWS['s3_upload_bucket_name']
        key = f'{folder_name}/{str(object_id)}' if folder_name else str(object_id)
        bucket = self.connection.Bucket(bucket_name)
        upload_to = f'https://{bucket_name}.s3.{self._connection_parameter["region"]}.amazonaws.com/{key}'
        args = {'ACL': 'public-read'} if public_read else {}
        if extra_args:
            args = args | extra_args
        try:
            bucket.upload_file(Filename=upload_from, Key=key, ExtraArgs=args)
            logger.info(f'[S3] Success {upload_from}->{upload_to}')
        except Exception as e:
            logger.error(f'[S3] Failed {upload_from}->{upload_to}', exc_info=True)
            return False, parse_error('ZE002', details=f'{upload_from}->{upload_to}', description=str(e))

        return True, {'message': 's3 upload success',
                      'upload_to': upload_to
                      }

    def bytes_upload_to_s3(self, file_obj, object_id, folder_name=None, bucket=None, public_read=True, extra_args=None):
        # Upload a file like object to s3
        bucket_name = bucket if bucket is not None else Config.AWS['s3_upload_bucket_name']
        key = f'{folder_name}/{str(object_id)}' if folder_name else str(object_id)
        bucket = self.connection.Bucket(bucket_name)
        upload_to = f'https://{bucket_name}.s3.{self._connection_parameter["region"]}.amazonaws.com/{key}'
        args = {'ACL': 'public-read'} if public_read else {}
        if extra_args:
            args = args | extra_args
        try:
            bucket.upload_fileobj(file_obj, key, ExtraArgs=args)
            logger.info(f'[S3] Upload Success {upload_to}')
        except Exception as e:
            logger.error(f'[S3] Upload Failed {upload_to}', exc_info=True)
            return False, parse_error('ZE002', details=f'bytes_start {file_obj} bytes_end->{upload_to}',
                                      description=str(e))

        return True, {'message': 's3 upload success',
                      'upload_to': upload_to
                      }
