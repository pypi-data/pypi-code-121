import datetime as dt

from typing import Any
from typing import Dict
from typing import List
from typing import IO
from typing import Union

import boto3


def s3_bucket(bucket: str) -> Any:
    s3_resource = boto3.resource('s3')
    return s3_resource.Bucket(name=bucket)


def get_object(bucket_name: str, key: str, stream: bool = False) -> Any:
    bucket = s3_bucket(bucket_name)
    obj = bucket.Object(key=key)
    body = obj.get().get('Body')
    return body.iter_lines() if stream else body.read()


def put_object(bucket_name: str, key: str, content: Union[bytes, IO], **kwargs):
    bucket = s3_bucket(bucket_name)
    obj = bucket.Object(key=key)
    obj.put(Body=content, **kwargs)


def delete_object(bucket_name: str, key: str):
    bucket = s3_bucket(bucket_name)
    obj = bucket.Object(key=key)
    obj.delete()


def delete_folder_in_bucket(bucket_name: str, prefix: str):
    bucket = s3_bucket(bucket_name)
    bucket.objects.filter(Prefix=prefix).delete()


def list_objects(bucket_name: str, path: str = None, return_object_keys: bool = True) -> List[Any]:
    bucket = s3_bucket(bucket_name)
    return [obj.key if return_object_keys else obj for obj in bucket.objects.filter(
        Prefix=path if path else ''
    )]


def list_common_object_prefixes(bucket_name: str, path: str = None,
                                delimiter: str = '/') -> List[str]:
    objects = boto3.client('s3').list_objects_v2(
        Bucket=bucket_name,
        Prefix=path,
        Delimiter=delimiter
    )
    return [cp['Prefix'] for cp in objects.get('CommonPrefixes', [])]


def copy_objects(source_bucket_name: str, destination_bucket_name: str, keys: Dict[str, str],
                 destination_path: str = ''):
    destination_bucket = s3_bucket(destination_bucket_name)

    # Ensure folder structure of destination path
    if destination_path and not destination_path.endswith('/'):
        destination_path += '/'

    for source_key, destination_key in keys.items():
        copy_source = {
            'Bucket': source_bucket_name,
            'Key': source_key
        }
        obj = destination_bucket.Object(key=f'{destination_path}{destination_key}')
        obj.copy(copy_source)


def generate_presigned_url(bucket_name: str, key: str, **kwargs) -> str:
    client_kwargs = {'config': kwargs.pop('Config'), 'region_name': kwargs.pop('RegionName')}
    client = boto3.client('s3', **client_kwargs)
    return client.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': bucket_name,
            'Key': key
        },
        **kwargs
    )


def get_last_updated_object_key_in_bucket(bucket_name: str, key: str):
    """
    This function gets the last modified object by date (last modified date) in an s3 path
    """
    get_last_modified = lambda obj: int(obj.last_modified.strftime('%s'))
    objs = list_objects(bucket_name=bucket_name, path=key, return_object_keys=False)
    objs = [obj for obj in sorted(objs, key=get_last_modified)]
    last_added = objs[-1].key
    return last_added


def clear_s3_path(s3_bucket: str, s3_key: str, backup_bucket: str):
    """ Clears objects in S3 path specified by <s3_bucket> and <s3_key>. """
    s3_objects = list_objects(bucket_name=s3_bucket, path=s3_key, return_object_keys=True)
    s3_objects_dict = {key: key for key in s3_objects}

    copy_objects(source_bucket_name=s3_bucket, destination_bucket_name=backup_bucket,
                 keys=s3_objects_dict)

    for s3_key in s3_objects:
        delete_object(bucket_name=s3_bucket, key=s3_key)


def get_last_modified_timestamp(bucket_name: str, key: str) -> dt.datetime:
    """ Gets the last modified timestamp for s3://<bucket_name>/<key>.

    Wrapper function around boto3.client.head_object()

    Raises:
        ValueError if <key> evaluates to false (e.g. empty string or None).
    """
    if not key:
        raise ValueError("The <key> function parameter cannot be None or an empty string.")
    # Add forward slash after key in case it's missing
    key = key + '/' if key[-1] != '/' else key
    # Get last modified timestamp
    client = boto3.client('s3')
    last_modified_ts = client.head_object(Bucket=bucket_name, Key=key)["LastModified"]
    return last_modified_ts
