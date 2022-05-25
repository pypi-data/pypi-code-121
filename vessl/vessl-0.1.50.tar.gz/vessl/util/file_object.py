import base64
import json
import os

import boto3
import requests
from tqdm import tqdm
from tqdm.utils import CallbackIOWrapper

from vessl.util import logger


class UploadableFileObject:
    def __init__(self, url, base_path, path):
        self.url = url
        self.base_path = base_path
        self.full_path = os.path.join(base_path, path)
        self.path = path

    def read_in_chunks(filename, chunk_size=65535, chunks=-1, callback=None):
        """Lazy function (generator) to read a file piece by piece."""
        with open(filename, "rb") as f:
            while chunks:
                data = f.read(chunk_size)
                if not data:
                    break
                yield data

                if callback:
                    callback(data)
                chunks -= 1

    def upload_chunks(self, *, callback=None):
        return self.read_in_chunks(self.full_path, callback=callback)

    def upload_hooks(self, *, callback=None):
        def fn(resp, **kwargs):
            if resp.status_code != 200:
                logger.warning(
                    f"Upload for {resp.request.url} failed. Detail: {resp.data}"
                )

        return {
            "response": fn,
        }

    def upload(self, session=requests.Session()):
        file_size = os.path.getsize(self.full_path)

        # send empty data when file is empty
        if os.stat(self.full_path).st_size == 0:
            future = session.put(
                self.url,
                data="",
                headers={"content-type": "application/octet-stream"},
                hooks=self.upload_hooks(),
            )
            return future

        with open(self.full_path, "rb") as f:
            with tqdm(
                total=file_size,
                desc=self.path,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
            ) as t:
                wrapped_file = CallbackIOWrapper(t.update, f, "read")
                requests.put(self.url, data=wrapped_file)
        return


class UploadableS3Object:
    def __init__(self, local_path: str, bucket, key, token, verbose=False):
        self.path = local_path
        self.bucket = bucket
        self.key = key
        self.token = token

        self.s3_client = self._get_s3_client_from_token()

        if verbose:
            boto3.set_stream_logger(name="botocore")

    def upload(self):
        self.s3_client.upload_file(self.path, self.bucket, self.key)

    def _get_s3_client_from_token(self):
        credentials = base64.b64decode(self.token).decode()
        credentials_dict = json.loads(credentials)
        return boto3.client(
            "s3",
            aws_access_key_id=credentials_dict["AccessKeyId"],
            aws_secret_access_key=credentials_dict["SecretAccessKey"],
            aws_session_token=credentials_dict["SessionToken"],
        )
