import json
import logging
import os
import tempfile
from json import JSONDecodeError
from typing import List, NamedTuple

import oss2
from oss2.iterators import ObjectIteratorV2

from robertcommonbasic.basic.validation import input as input_checker


class OSSConfig(NamedTuple):
    ENDPOINT: str
    ACCESS_KEY_ID: str
    ACCESS_KEY_SECRET: str


class OSSAccessor:
    def __init__(self, config: OSSConfig):
        self.endpoint = input_checker.ensure_not_none_str(
            'ENDPOINT', config.ENDPOINT)
        self.access_key_id = input_checker.ensure_not_none_str(
            'ACCESS_KEY_ID', config.ACCESS_KEY_ID)
        self.access_key_secret = input_checker.ensure_not_none_str(
            'ACCESS_KEY_SECRET', config.ACCESS_KEY_SECRET)

    def _get_bucket(self, bucket_name: str):
        bucket = oss2.Bucket(
            oss2.Auth(self.access_key_id, self.access_key_secret),
            self.endpoint, bucket_name)
        return bucket

    def upload_by_file_path(self,
                            bucket_name: str,
                            oss_path: str,
                            file_path: str,
                            headers: dict = {}):
        # data is string or file stream
        logging.info(
            f'upload oss file to bucket_name={bucket_name}, oss_path={oss_path}'
        )
        bucket = self._get_bucket(bucket_name)
        with open(oss2.to_unicode(file_path), 'rb') as f:
            bucket.put_object(oss_path, f, headers=headers)
        return

    def get_oss_data_file(self, bucket_name, oss_path):
        bucket = self._get_bucket(bucket_name)
        f = None
        try:
            f = bucket.get_object(oss_path)
            return f
        except oss2.exceptions.NoSuchKey:
            logging.error(
                f'bucket_name={bucket_name}, oss path={oss_path} not exists')
            return None
        except Exception as e:
            logging.error(
                f'bucket_name={bucket_name}, '
                f'oss path={oss_path} can not fetch, {e}',
                exc_info=True)
            return None

    def get_oss_data_json(self, bucket_name, oss_path):
        try:
            f = self.get_oss_data_file(bucket_name, oss_path)
            if not f:
                return None
            j = json.load(f)
            return j
        except JSONDecodeError:
            logging.error(f'bucket_name={bucket_name}, '
                          f'oss_path={oss_path}, error json format')
            return None

    def delete_oss_objects(self, bucket_name, oss_path_list: List[str]):
        bucket = self._get_bucket(bucket_name)
        bucket.batch_delete_objects(oss_path_list)
        return

    def oss_path_iterator(self, bucket_name, oss_path_prefix):
        bucket = self._get_bucket(bucket_name)
        for object_info in ObjectIteratorV2(bucket, prefix=oss_path_prefix):
            yield object_info

    def upload_text(self,
                    bucket_name: str,
                    oss_path: str,
                    text: str,
                    mode: str = 'w',
                    headers: dict = {}):
        t = tempfile.NamedTemporaryFile(mode=mode, delete=False)
        t.write(text)
        t.close()
        try:
            self.upload_by_file_path(bucket_name, oss_path, t.name, headers)
        finally:
            os.remove(t.name)
        return

    def upload_json(self,
                    bucket_name: str,
                    oss_path: str,
                    j: dict,
                    headers: dict = {}):
        new_headers = {'Content-Type': 'application/json'}
        new_headers.update(headers)
        text = json.dumps(j, ensure_ascii=False)
        self.upload_text(bucket_name, oss_path, text, headers=new_headers)
        return