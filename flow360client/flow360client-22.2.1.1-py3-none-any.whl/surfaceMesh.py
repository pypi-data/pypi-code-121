import json
import os
import time

from boto3.s3.transfer import TransferConfig
from .authentication import refreshToken
from .httputils import flow360ApiPost, flow360ApiGet, flow360ApiDelete, flow360ApiPut
from .s3utils import buildS3Client, UploadProgress, DownloadFiles
from .httputils import FileDoesNotExist
from .config import Config

auth = Config.auth
keys = Config.user


@refreshToken
def AddSurfaceMesh(name, tags, solver_version, format):
    body = {
        "name": name,
        "tags": tags,
        "format": format
    }

    if solver_version:
        body['solverVersion'] = solver_version

    resp = flow360ApiPost("surfacemeshes", data=body)
    return resp


@refreshToken
def GenerateSurfaceMeshFromGeometry(name, config, tags, solver_version):
    body = {
        "name": name,
        "tags": tags,
        "config": json.dumps(config),
    }

    if solver_version:
        body['solverVersion'] = solver_version

    resp = flow360ApiPost("surfacemeshes", data=body)
    return resp


@refreshToken
def DeleteSurfaceMesh(surfaceMeshId):
    resp = flow360ApiDelete(f"surfacemeshes/{surfaceMeshId}")
    return resp


@refreshToken
def GetSurfaceMeshInfo(surfaceMeshId):
    url = f"surfacemeshes/{surfaceMeshId}"
    resp = flow360ApiGet(url)
    return resp


@refreshToken
def CompleteSurfaceMeshUpload(meshId, fileName):
    url = f"surfacemeshes/{meshId}/completeUpload?fileName={fileName}"
    resp = flow360ApiPost(url)
    return resp


@refreshToken
def ListSurfaceMeshes(include_deleted=False):
    resp = flow360ApiGet("surfacemeshes")
    if not include_deleted:
        resp = list(filter(lambda i: i['status'] != 'deleted', resp))
    return resp


@refreshToken
def UploadGeometry(surfaceMeshId, geoFile):
    '''
    Upload for files other than surface mesh
    '''

    if not os.path.exists(geoFile):
        print('mesh file {0} does not Exist!'.format(geoFile))
        raise FileDoesNotExist(geoFile)

    meshInfo = GetSurfaceMeshInfo(surfaceMeshId)


    fileSize = os.path.getsize(geoFile)
    prog = UploadProgress(fileSize)
    config = TransferConfig(multipart_threshold=1024 * 25, max_concurrency=10,
                            multipart_chunksize=1024 * 25, use_threads=True)

    fileName = 'geometry.csm'
    buildS3Client().upload_file(Bucket=Config.MESH_BUCKET,
                         Filename=geoFile,
                         Key='users/{0}/{1}/{2}'.format(keys['userId'], surfaceMeshId, fileName),
                         Callback=prog.report,
                         Config=config)
    CompleteSurfaceMeshUpload(surfaceMeshId, fileName)

@refreshToken
def UploadSurfaceMesh(surfaceMeshId, meshFile):
    '''
    Upload surface mesh
    '''

    def getMeshName(meshFile, meshFormat):

        name = "surfaceMesh." + meshFormat

        if meshFile.endswith('.gz'):
            name += '.gz'
        elif meshFile.endswith('.bz2'):
            name += '.bz2'
        return name

    meshInfo = GetSurfaceMeshInfo(surfaceMeshId)
    print(meshInfo)
    fileName = getMeshName(meshFile, meshInfo['format'])

    if not os.path.exists(meshFile):
        print('mesh file {0} does not Exist!'.format(meshFile))
        raise FileDoesNotExist(meshFile)

    fileSize = os.path.getsize(meshFile)
    prog = UploadProgress(fileSize)
    config = TransferConfig(multipart_threshold=1024 * 25, max_concurrency=10,
                            multipart_chunksize=1024 * 25, use_threads=True)

    buildS3Client().upload_file(Bucket=Config.MESH_BUCKET,
                         Filename=meshFile,
                         Key='users/{0}/{1}/{2}'.format(keys['userId'], surfaceMeshId, fileName),
                         Callback=prog.report,
                         Config=config)
    CompleteSurfaceMeshUpload(meshInfo['id'], fileName)


def DownloadSurfaceFile(id, filename):
    prefix = id
    os.makedirs(prefix, exist_ok=True)
    DownloadFiles(os.path.join(prefix, filename), localPrefix=prefix)


def DownloadLogs(id):
    DownloadSurfaceFile(id, 'logs/flow360_surface_mesh.user.log')


def WaitOnMesh(meshId, timeout=86400, sleepSeconds=10):
    startTime = time.time()
    while time.time() - startTime < timeout:
        try:
            info = GetSurfaceMeshInfo(meshId)
            if info['status'] in ['deleted', 'error', 'preerror', 'unknownError', 'processed']:
                return info['meshStatus']
        except Exception as e:
            print('Warning : {0}'.format(str(e)))

        time.sleep(sleepSeconds)

