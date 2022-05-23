import os
import re
import tempfile
import requests
import shutil
import functools
from geodesic.utils.backoff import backoff

try:
    from google.cloud import storage
except ImportError:
    storage = None

try:
    import boto3
except ImportError:
    boto3 = None

# Regex to get/extract bucket and key from Google Cloud Storage or S3
gs_re = re.compile(r"gs://([\w\-]{1,})\/([\/\w\.\-]{1,})", re.UNICODE)
s3_re = re.compile(r"s3://([\w\-]{1,})\/([\/\w\.\-]{1,})", re.UNICODE)

s3_re_other = [
    (re.compile(r"https://([\w\-]{1,})?\.?s3\.([\w\-]{1,})?\.?amazonaws\.com\/([\/\w\.\-]{1,})", re.UNICODE), (1, 3))
]

gs_client = None
if storage is not None:
    gs_client = storage.Client()

s3_client = None
if boto3 is not None:
    s3_client = boto3.client('s3')


def download(uri, out_dir=None):
    """
    Given a URI for some object, downloads to a specified directory and returns location.
    If that directory is None, stores to a tmp directory. Delete when you are done.
    """

    if out_dir is None:
        out_dir = tempfile.mkdtemp()

    m = gs_re.match(uri)

    if m:
        bucket = m.group(1)
        key = m.group(2)
        return download_gs(bucket, key, out_dir)

    m = s3_re.match(uri)

    if m:
        bucket = m.group(1)
        key = m.group(2)

        return download_s3(bucket, key, out_dir)

    if (
        uri.startswith("http://")
        or uri.startswith("https://")
        or uri.startswith("ftp://")
    ):
        return download_file(uri, out_dir)

    return uri


@backoff
def download_gs(bucket_name: str, key: str, out_dir: str) -> str:
    if gs_client is None:
        raise ValueError("google cloud API not installed!")

    bucket = gs_client.bucket(bucket_name)

    blob = bucket.blob(key)

    bname = os.path.basename(key)
    out = os.path.join(out_dir, bname)
    blob.download_to_filename(out)

    return out


@backoff
def download_s3(bucket_name: str, key: str, out_dir: str) -> str:
    if s3_client is None:
        raise ValueError("boto3 is not installed!")

    bname = os.path.basename(key)
    out = os.path.join(out_dir, bname)

    s3_client.download_file(bucket_name, key, out)
    return out


@backoff
def download_file(url: str, out_dir: str):
    bname = os.path.basename(url)
    out = os.path.join(out_dir, bname)

    # NOTE the stream=True parameter below
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        r.raw.read = functools.partial(r.raw.read, decode_content=True)
        with open(out, 'wb') as f:
            shutil.copyfileobj(r.raw, f)
    return out
