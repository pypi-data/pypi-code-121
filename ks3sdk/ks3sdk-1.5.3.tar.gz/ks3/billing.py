# coding:utf-8
import json

from ks3.exception import KS3ResponseError
from ks3.http import make_request_v4


def get_buckets_data(access_key_id, access_key_secret, start_time, end_time, bucket_names=None, products="", date_type="Day"):
    query_args = {
        'Action': 'QueryKs3Data',
        'Version': 'v1',
        'StartTime': start_time,
        'EndTime': end_time,
        'DateType': date_type,
        'Ks3Product': products
    }

    if bucket_names:
        query_args['BucketName'] = bucket_names

    response = make_request_v4(access_key_id, access_key_secret, method='GET', service='ks3bill',
                               region='cn-beijing-6', query_args=query_args)
    body = response.read()
    if response.status != 200:
        raise KS3ResponseError(response.status, response.reason, body)
    return json.loads(body)