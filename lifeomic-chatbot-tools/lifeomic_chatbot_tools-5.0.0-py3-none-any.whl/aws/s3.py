import os
import typing as t

from lifeomic_chatbot_tools._utils import ImportExtraError


try:
    import boto3
    from botocore import exceptions as boto3_exceptions
    from botocore.config import Config
except ImportError:
    raise ImportExtraError("aws", __name__)


class S3Client:
    def __init__(self):
        endpoint = os.getenv("AWS_ENDPOINT")
        region = os.getenv("AWS_REGION")
        self.resource = boto3.resource("s3", endpoint_url=endpoint, config=Config(region_name=region))
        self.client = boto3.client("s3", endpoint_url=endpoint, config=Config(region_name=region))

    def upload_dir(self, source_path: str, target_bucket: str, target_path: str):
        """
        Recursively uploads all files in the directory at ``source_path`` as objects in the AWS ``target_bucket``, all
        saved under the "directory" ``target_path``.
        """
        assert os.path.isdir(source_path)
        for root, _, filenames in os.walk(source_path):
            for filename in filenames:
                file_path_local = os.path.join(root, filename)
                object_key = os.path.join(target_path, file_path_local[1 + len(source_path) :])
                self.client.upload_file(file_path_local, target_bucket, object_key)

    def download_dir(self, source_bucket: str, source_path: str, target_path: str):
        """
        Recursively downloads all files living under the ``source_path`` directory in the AWS ``source_bucket``.
        Downloads them to the local directory ``target_path``.
        """
        objects = self.resource.Bucket(source_bucket).objects.filter(Prefix=source_path)
        for obj in objects:
            obj_save_path = os.path.join(target_path, obj.key[1 + len(source_path) :])
            save_dir = os.path.abspath(os.path.dirname(obj_save_path))
            if not os.path.isdir(save_dir):
                os.makedirs(save_dir)
            os.makedirs(os.path.dirname(obj_save_path), exist_ok=True)
            self.client.download_file(source_bucket, obj.key, obj_save_path)

    def get_object(self, bucket: str, key: str, **kwargs) -> t.Optional[bytes]:
        """
        Retrieves the object living at `s3://{bucket}/{key}`. Returns `None` if there is no object living there, rather
        than throwing an error.
        """
        try:
            data = self.client.get_object(Bucket=bucket, Key=key, **kwargs)
            return data["Body"].read()
        except boto3_exceptions.ClientError as error:
            if error.response["Error"]["Code"] != "NoSuchKey":
                raise error
        return None

    def delete_object(self, bucket: str, key: str, **kwargs) -> bool:
        """
        Attempts to delete the object living at `s3://{bucket}/{key}`. Returns `True` if it was deleted, and `False` if
        no object lived there.
        """
        try:
            self.client.head_object(Bucket=bucket, Key=key)
        except boto3_exceptions.ClientError as error:
            if error.response["Error"]["Code"] != "404":
                raise error
            # The object does not exist
            return False
        self.client.delete_object(Bucket=bucket, Key=key, **kwargs)
        return True
