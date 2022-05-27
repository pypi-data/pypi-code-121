import re
import boto3
from botocore.exceptions import ClientError
from .logger import Logger
import logging
from .file_utils import *
from dsocli.configs import Config

logging.getLogger('botocore').setLevel(Logger.mapped_level)
logging.getLogger('boto').setLevel(Logger.mapped_level)
logging.getLogger('boto3').setLevel(Logger.mapped_level)

UPLOAD_MULTIPART_THRESHOLD = 1024*25
UPLOAD_MULTIPART_CHUNK_SIZE = 1024*25
UPLOAD_MULTIPART_CONCURRENCY = 10

def get_s3_path(context, path_prefix='', key=None):
    if path_prefix.endswith('/'): path_prefix = path_prefix[:-1]
    return path_prefix + context.get_path(key)



# def list_s3_objects(bucket, path=''):
#     s3 = boto3.session.Session().client(service_name='s3')
#     paginator = s3.get_paginator("list_objects_v2")
#     response = paginator.paginate(Bucket=bucket, Prefix=path).build_full_result()
#     return response.get('Contents', [])


# def load_s3_path(result, bucket, path, filter=None, used_path_prefix='', object_kind='object'):
#     archives = list_s3_objects(bucket, path=path)
#     for archive in archives:
#         key = archive['Key'][len(path)+1:]
#         if filter and not re.match(filter, key): continue
#         if key in result:
#             Logger.warn(f"Inherited {object_kind} '{key}' was overridden.")
#         ctx_path = path[len(used_path_prefix):]
#         ctx = Context(*Contexts.parse_path(ctx_path)[0:3])
#         details = {
#                     'Bucket': bucket,
#                     'Path': archive['Key'],
#                     'ETag': archive['ETag'],
#                     'Stage': ctx.short_stage,
#                     'Scope': ctx.scope_translation,
#                     'Context': {
#                         'Namespace': ctx.namespace,
#                         'Application': ctx.application,
#                         'Stage': ctx.stage,
#                     },
#                     'Size': convert_file_size_unit(archive['Size']),
#                     # 'Version': archive['Version'],
#                     'Date': archive['LastModified'].strftime('%Y/%m/%d-%H:%M:%S'),
#                 }
#         result[key] = details
#     return result



# def s3_context_list_files(bucket, path_prefix='', uninherited=False, filter=None, object_kind='object'):
#     ### construct search path in hierachy with no key specified
#     paths = Contexts.get_hierachy_paths(context=Config.context, key=None, path_prefix=path_prefix, ignore_stage=Config.stage is None, uninherited=uninherited)
#     archives = {}
#     for path in paths:
#         Logger.debug(f"Loading S3 path: bucket={bucket}, path={path}")
#         load_s3_path(config=bucket=bucket, result=archives, path=path, filter=filter, used_path_prefix=path_prefix, object_kind=object_kind)
#     return archives



def list_s3_objects(bucket, path, filter=None):
    s3 = boto3.session.Session().client(service_name='s3')
    paginator = s3.get_paginator("list_objects_v2")
    response = paginator.paginate(Bucket=bucket, Prefix=path).build_full_result()
    items = response.get('Contents', [])
    result = []
    for item in items:
        key = item['Key'][len(path)+1:]
        if filter and not re.match(filter, key): continue
        details = {
                    'Key': key,
                    'Path': item['Key'],
                    'ETag': item['ETag'],
                    'Size': convert_file_size_unit(item['Size']),
                    # 'Version': item['Version'],
                    'Date': item['LastModified'].strftime('%Y/%m/%d-%H:%M:%S'),
                }
        result.append(details)
    return result



def s3_context_list_files(bucket, path_prefix='', filter=None):
    path = get_s3_path(Config.context, path_prefix, key=None)
    Logger.debug(f"Loading S3 path: bucket={bucket}, path={path}")
    response = list_s3_objects(bucket, path, filter)
    return response



def s3_context_add_file(filepath, bucket, key, path_prefix=''):
    s3 = boto3.session.Session().client(service_name='s3')
    transferConfig = boto3.s3.transfer.TransferConfig(multipart_threshold=UPLOAD_MULTIPART_THRESHOLD, max_concurrency=UPLOAD_MULTIPART_CONCURRENCY, multipart_chunksize=UPLOAD_MULTIPART_CHUNK_SIZE, use_threads=True)
    path = get_s3_path(Config.context, path_prefix, key)
    Logger.debug(f"Uploading S3 object: bucket={bucket}, path={path}")
    s3.upload_file(filepath, bucket, path, Config=transferConfig)
    result = {
        'Bucket': bucket,
        'Path': path,
    }
    return result



def s3_context_get_file(bucket, key, path_prefix=''):
    s3 = boto3.session.Session().client(service_name='s3')
    path = get_s3_path(Config.context, path_prefix, key)
    Logger.debug(f"Downloading S3 object: bucket={bucket}, path={path}")
    try:
        s3.download_file(Bucket=bucket, Key=path, Filename=key)
    except ClientError as e:
        if 'Not Found' in repr(e):
            return {}
        else:
            raise

    result = {
        'Key': key,
        'Bucket': bucket,
        'Path': path,
        'FilePath': '.' + os.path.join(os.sep, key)
    }
    return result


def s3_context_delete_file(bucket, key, path_prefix=''):
    s3 = boto3.session.Session().client(service_name='s3')
    path = get_s3_path(Config.context, path_prefix, key)
    Logger.debug(f"Deleting S3 object: bucket={bucket}, path={path}")
    try:
        s3.head_object(Bucket=bucket, Key=path)
    except ClientError as e:
        if 'Not Found' in repr(e):
            return {}
        else:
            raise

    s3.delete_object(Bucket=bucket, Key=path)
    result = {
        'Key': key,
        'Bucket': bucket,
        'Path': path,
    }
    return result

