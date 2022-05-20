import base64
import csv
import json
import logging
import uuid
from io import StringIO
from os import path
from urllib.parse import urlparse

import boto3
import botocore

bucket = 'sagemaker-us-west-2-079310353266'
prefix = 'sagemaker/sagemaker-xgboost-lending/'
s3_client = boto3.client('s3')

LOGGER = logging.getLogger(__name__)


class S3Uri:
    """bucket, object_key for an S3 uri."""

    def __init__(
        self, bucket: str, key: str, auth_context: dict = {}, endpoint_url=None
    ):
        self.bucket = bucket
        self.key = key

        if auth_context and (
            auth_context.get('aws_access_key_id')
            and auth_context.get('aws_secret_access_key')
        ):
            # using supplied credentials
            self.s3 = boto3.resource(
                's3',
                endpoint_url=endpoint_url,
                aws_access_key_id=auth_context['aws_access_key_id'],
                aws_secret_access_key=auth_context['aws_secret_access_key'],
                aws_session_token=auth_context.get('aws_session_token'),
            )
        elif boto3.session.Session().get_credentials():
            # using default credentials
            # if not auth_context, assume that the credentials are set up
            # elsewhere viz., envvars, credentials file etc.
            LOGGER.info('Gettting credentials from the boto3 session')
            self.s3 = boto3.resource('s3', endpoint_url=endpoint_url)
        else:
            # there are no credentials.. Maybe, the user is expecting to
            # download from a public S3 bucket?
            # using no credentials
            LOGGER.info('No credentials provided using public bucket')
            cnfg = botocore.config.Config(signature_version=botocore.UNSIGNED)
            self.s3 = boto3.resource('s3', endpoint_url=endpoint_url, config=cnfg)

    @property
    def uri(self):
        return f's3://{self.bucket}/{self.key}'

    def s3_bucket(self):  # Bucket
        """Returns Bucket object `boto3.resource('s3').Bucket(bucket)`."""
        return self.s3.Bucket(self.bucket)

    def s3_object(self, relative_path: str = None):  # Bucket.Object()
        """Returns S3 Object for path under this uri."""
        if not relative_path:
            return self.s3_bucket().Object(self.key)
        else:
            return self.s3_bucket().Object(path.join(self.key, relative_path))

    def read_object(self, relative_path: str = None) -> bytes:
        """Reads contents of object located at `relative_path`.
        Be careful not to read large objects.
        :returns: file content as byte array"""
        return self.s3_object(relative_path).get()['Body'].read()

    def is_object_readable(self, relative_path: str = None):
        """Reads object located at `relative_path`.
        :returns: True if successful."""
        try:
            self.s3_object(relative_path).get()
        except botocore.exceptions.ClientError as e:
            return False, str(e)
        return True, None

    def download_file(self, local_path: str, relative_path: str = None):
        """Downloads the remote file `relative_path` to `local_path`."""
        return self.s3_object(relative_path).download_file(local_path)

    @staticmethod
    def from_uri(s3_uri: str, auth_context: dict = {}):
        parsed = urlparse(s3_uri)
        if parsed.scheme != 's3':
            raise ValueError(f'`s3://<bucket>/<prefix>` expected, but got `{s3_uri}`')
        return S3Uri(parsed.netloc, parsed.path.lstrip('/'), auth_context)


class GcsUri(S3Uri):
    """bucket, object_key for an S3 uri."""

    def __init__(self, bucket: str, key: str, auth_context: dict = {}):
        endpoint_url = 'https://storage.googleapis.com'
        super().__init__(bucket, key, auth_context, endpoint_url=endpoint_url)

    @staticmethod
    def from_uri(gs_uri: str, auth_context: dict = {}):
        parsed = urlparse(gs_uri)
        if parsed.scheme != 'gs':
            raise ValueError(f'`gs://<bucket>/<prefix>` expected, but got `{gs_uri}`')
        return S3Uri(
            parsed.netloc,
            parsed.path.lstrip('/'),
            auth_context,
            endpoint_url='https://storage.googleapis.com',
        )


def validate_s3_uri_access(url, credentials, throw_error=False):
    if credentials is None:
        credentials = {}
    s3_handle = S3Uri.from_uri(url, credentials)
    is_valid_s3, message = s3_handle.is_object_readable()
    if not is_valid_s3:
        if throw_error:
            raise ValueError(f'Unable to access S3 URI\n{message}')
        return False

    return True


def validate_gcp_uri_access(url, credentials, throw_error=False):
    if credentials is None:
        credentials = {}
    gcs_handle = GcsUri.from_uri(url, credentials)
    is_valid_gcs, message = gcs_handle.is_object_readable()
    if not is_valid_gcs:
        if throw_error:
            raise ValueError(f'Unable to access GS URI\n{message}')
        return False

    return True


def sample_data_capture_log(bucket, prefix, sample_size):
    objects = s3_client.list_objects(Bucket=bucket, Prefix=prefix)

    result = []
    for obj in objects['Contents']:
        key = obj['Key']
        if key.endswith('.jsonl'):
            tmpkey = key.replace('/', '')
            download_path = '/tmp/{}{}'.format(uuid.uuid4(), tmpkey)
            s3_client.download_file(bucket, key, download_path)
            with open(download_path) as f:
                for line in f:
                    pline = json.loads(line)
                    input = base64.b64decode(
                        pline['captureData']['endpointInput']['data']
                    ).decode('ascii')
                    output = base64.b64decode(
                        pline['captureData']['endpointOutput']['data']
                    ).decode('ascii')
                    # input = pline['captureData']['endpointInput']['data']
                    # output = pline['captureData']['endpointOutput']['data']
                    inputstr = StringIO(input)
                    inarray = next(csv.reader(inputstr, delimiter=','))
                    outputstr = StringIO(output)
                    outarray = next(csv.reader(outputstr, delimiter=','))
                    result.append(inarray + outarray)
                    if len(result) >= sample_size:
                        return result

    return result
