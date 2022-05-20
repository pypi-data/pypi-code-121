import os

from boto3.s3.transfer import TransferConfig

from flow360client.httputils import flow360ApiGet, flow360ApiPut, flow360ApiPost, flow360ApiDelete
from .authentication import refreshToken
from .config import Config
from .s3utils import buildS3Client, UploadProgress

auth = Config.auth
keys = Config.user
@refreshToken
def UploadStudioItem(itemId, file):
    path, filename = os.path.split(file)
    fileSize = os.path.getsize(file)
    prog = UploadProgress(fileSize)
    key = 'users/{0}/{1}/{2}'.format(keys['accessUserId'], itemId, filename)
    config = TransferConfig(multipart_threshold=1024 * 25, max_concurrency=50,
                            multipart_chunksize=1024 * 25, use_threads=True)

    buildS3Client().upload_file(Bucket=Config.STUDIO_BUCKET,
                         Filename=file,
                         Key=key,
                         Callback=prog.report,
                         Config=config)
    item = {
        'itemId': str(itemId),
        'status': 'processed',
        's3Path': key
    }

    return UpdateStudioItem(item)

def UpdateStudioItem(item):
    return flow360ApiPut(f'studio/item/{item["itemId"]}', item)


def NewStudioItem(item):
    return flow360ApiPost(f'studio/item', item)

def GetStudioItem(itemId):
    return flow360ApiGet(f'studio/item/{itemId}')

def DeleteStudioItem(itemId):
    return flow360ApiDelete(f'studio/item/{itemId}')

def CopyResourceToMesh(itemId, meshId):
    return flow360ApiPost(f'studio/item/{itemId}/copyToMesh/{meshId}')



