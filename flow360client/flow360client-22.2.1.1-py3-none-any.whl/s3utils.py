import sys
import os
import boto3

from .config import Config
from .httputils import flow360ApiGet, portalApiGet
from .authentication import refreshToken
from botocore.exceptions import ClientError


class UploadProgress(object):

    def __init__(self, size):
        self.size = size
        self.uploadedSoFar = 0

    def report(self, bytes_in_chunk):
        self.uploadedSoFar += bytes_in_chunk
        sys.stdout.write('\rfile upload progress: {0:2.2f} %'.format(float(self.uploadedSoFar)/self.size*100))
        sys.stdout.flush()


def buildS3Client():
    resp = getUserCredential()
    print('using account: {}'.format(Config.user['accessEmail']))
    return boto3.client(
        's3',
        aws_access_key_id=resp['userAccessKey'],
        aws_secret_access_key=resp['userSecretAccessKey'],
        region_name=Config.S3_REGION
    )


def getUserCredential():
    url = f"auth/credential"
    resp = portalApiGet(url)
    return resp

@refreshToken
def DownloadFiles(files, prefix='', localPrefix=''):
    if not isinstance(files, list):
        files = [files]
    for file in files:
        keys = Config.user
        fileCloudPath = 'users/{0}/{1}'.format(keys['userId'], os.path.join(prefix, file)).replace("\\", "/")
        try:
            buildS3Client().download_file(Bucket=Config.MESH_BUCKET,
                                Filename=os.path.join(localPrefix, os.path.basename(file)),
                                Key=fileCloudPath)
        except ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("The file {} does not exist.".format(file))
            else:
                raise

              
