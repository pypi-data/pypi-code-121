import hashlib
import math
import os
import json
import sys
import uuid
from os.path import basename

import flow360client.versionCheck
import flow360client.mesh as mesh
import flow360client.surfaceMesh
from flow360client.meshUtils import validateMeshAndMeshJson
import flow360client.case as case
from flow360client.authentication import authentication_api, getSupportedUsers
from flow360client.config import Config
from flow360client.httputils import FileDoesNotExist, flow360ApiPost
from flow360client.fun3d_to_flow360 import translate_boundaries
from flow360client.httputils import FileDoesNotExist
from flow360client.s3utils import getUserCredential
from flow360client.studio import UploadStudioItem, NewStudioItem
from flow360client.task import NewTask, GetTask, WaitOnTask
from flow360client.IOutils import readJsonFileOrDict
from flow360client.generator.case import generateCaseJson

def NewCase(meshId, config, caseName=None, tags=[],
            priority='high', parentId=None):
    if isinstance(config, str) and caseName is None:
        caseName = os.path.basename(config).split('.')[0]

    config = readJsonFileOrDict(config)

    assert isinstance(config, dict)
    assert caseName is not None
    resp = case.SubmitCase(caseName, tags, meshId, priority, json.dumps(config), parentId)
    return resp['caseId']

def NewCaseListWithPhase(meshId, config, caseName=None, tags=[],
                         priority='high', parentId=None, phaseCount=1):
    if isinstance(config, str):
        if not os.path.exists(config):
            print('config file {0} does not Exist!'.format(config), flush=True)
            raise FileDoesNotExist(config)
        if caseName is None:
            caseName = os.path.basename(config).split('.')[0]
        with open(config) as fh:
            config = json.load(fh)
    assert isinstance(config, dict)
    assert caseName is not None
    assert phaseCount >= 1
    caseIds = []
    totalSteps = config['timeStepping']['maxPhysicalSteps']
    phaseSteps = math.ceil(totalSteps / phaseCount)
    index = 1

    while totalSteps > 0:
        config['timeStepping']['maxPhysicalSteps'] = min(totalSteps, phaseSteps)
        resp = case.SubmitCase(f'{caseName}_{index}', tags, meshId, priority, json.dumps(config), parentId)
        caseIds.append(resp['caseId'])
        totalSteps = totalSteps - phaseSteps
        parentId = resp['caseId']
        index = index + 1
    return caseIds

def NewMesh(fname, noSlipWalls=None, meshName=None, tags=[],
            fmat=None, endianness=None, solverVersion=None, meshJson=None):
    if not os.path.exists(fname):
        print('mesh file {0} does not Exist!'.format(fname), flush=True)
        raise FileDoesNotExist(fname)
    if meshJson is not None:
        meshJson = readJsonFileOrDict(meshJson)
    if meshName is None:
        meshName = os.path.splitext(basename(fname))[0]

    if fmat is None:
        if fname.endswith('.ugrid') or fname.endswith('.ugrid.gz') or \
                fname.endswith('.ugrid.bz2'):
            fmat = 'aflr3'
        elif fname.endswith('.cgns') or fname.endswith('.cgns.gz') or \
                fname.endswith('.cgns.bz2'):
            fmat = 'cgns'
        else:
            raise RuntimeError('Unknown format for file {}'.format(fname))

    if endianness is None:
        try:
            if fname.find('.b8.') != -1:
                endianness = 'big'

            elif fname.find('.lb8.') != -1:
                endianness = 'little'
            else:
                endianness = ''
        except:
            raise RuntimeError('Unknown endianness for file {}'.format(fname))

    if noSlipWalls is None and meshJson is None:
        raise RuntimeError('Both noSlipWals or meshJson are none')

    if noSlipWalls is not None and meshJson is not None:
        noSlipWalls = None
        print('noSlipWalls will be override by meshJson')

    if noSlipWalls is not None:
        validateMeshAndMeshJson(fname, { "boundaries": {"noSlipWalls": noSlipWalls }}, solverVersion)
        resp = mesh.AddMesh(meshName, noSlipWalls, tags, fmat, endianness, solverVersion)
    else:
        if isinstance(meshJson, str):
            if not os.path.exists(meshJson):
                print('meshJson file {0} does not Exist!'.format(meshJson), flush=True)
                raise FileDoesNotExist(meshJson)
            meshJson = json.load(open(meshJson))
        validateMeshAndMeshJson(fname, meshJson, solverVersion)
        resp = mesh.AddMeshWithJson(meshName, meshJson, tags, fmat, endianness, solverVersion)

    meshId = resp['meshId']
    mesh.UploadMesh(meshId, fname)
    print()
    return meshId


def NewMeshFromSurface(surfaceMeshId, config, meshName=None, tags=[], solverVersion=None):
    if isinstance(config, str):
        if not os.path.exists(config):
            print('config file {0} does not Exist!'.format(config), flush=True)
            raise FileDoesNotExist(config)
        if meshName is None:
            meshName = os.path.basename(config).split('.')[0]
        with open(config) as configFile:
            config = json.load(configFile)
    assert isinstance(config, dict)
    assert meshName is not None
    resp = mesh.GenerateMeshFromSurface(meshName, config, surfaceMeshId, tags, solverVersion)
    return resp['meshId']

def NewSurfaceMesh(fileName, surfaceMeshName=None, tags=[], solverVersion=None):
    if not os.path.exists(fileName):
        print('mesh file {0} does not Exist!'.format(fileName), flush=True)
        raise FileDoesNotExist(fileName)
    if surfaceMeshName is None:
        surfaceMeshName = os.path.splitext(basename(fileName))[0]
    format = getFileExtention(fileName)[1:]
    resp = surfaceMesh.AddSurfaceMesh(surfaceMeshName, tags, solverVersion, format)

    surfaceMeshId = resp['id']
    surfaceMesh.UploadSurfaceMesh(surfaceMeshId, fileName)
    print()
    return surfaceMeshId


def NewSurfaceMeshFromGeometry(fileName, geometryToSurfaceMeshJson, surfaceMeshName=None, tags=[], solverVersion=None):
    if not os.path.exists(fileName):
        print('mesh file {0} does not Exist!'.format(fileName), flush=True)
        raise FileDoesNotExist(fileName)
    if surfaceMeshName is None:
        surfaceMeshName = os.path.splitext(basename(fileName))[0]

    if getFileExtention(fileName) == '.csm':
        pass
    else:
        raise RuntimeError('Unknown format for file {}. Supported: .csm'.format(fileName))
    if isinstance(geometryToSurfaceMeshJson, str):
        if not os.path.exists(geometryToSurfaceMeshJson):
            print('geometryToSurfaceMeshJson file {0} does not Exist!'.format(geometryToSurfaceMeshJson), flush=True)
            raise FileDoesNotExist(geometryToSurfaceMeshJson)
        with open(geometryToSurfaceMeshJson) as jsonFile:
            geometryToSurfaceMeshJson = json.load(jsonFile)

    resp = surfaceMesh.GenerateSurfaceMeshFromGeometry(surfaceMeshName, geometryToSurfaceMeshJson, tags, solverVersion)

    surfaceMeshId = resp['id']
    surfaceMesh.UploadGeometry(surfaceMeshId, fileName)
    print()
    return surfaceMeshId


def NewMeshWithTransform(fname, meshName=None, tags=[], solverVersion=None):
    if not meshName:
        meshName = 'Flow360Mesh'
    with open(fname) as file:
        globalJson = json.load(file)
    transformsJson = globalJson["transforms"]
    meshFile = globalJson["mesh"]
    dirName = os.path.dirname(os.path.abspath(fname))
    transformingTasks = []

    sourceFiles = globalJson["sources"]
    fileToStudioItem = {}
    print("uploading source files")
    for filename in sourceFiles:

        item = UploadStudioItem(uuid.uuid1(), os.path.join(dirName, filename))
        print(item)
        fileToStudioItem[filename] = item


    for transformConfigFile in transformsJson:
        with open(os.path.join(dirName, transformConfigFile), 'r') as file:
            transformConfig = json.load(file)
            taskParam = json.dumps(transformConfig)
        filename = transformConfig['inputMesh']
        if filename in fileToStudioItem.keys():


            item = fileToStudioItem[filename]

            newItem = NewStudioItem({
                'status': "processing",
                'parentId': item['itemId'],
                's3Path': transformConfig['outputMesh']
            })

            task = {
                'taskParam': taskParam,
                'taskType': 'transform',
                'objectId': newItem['itemId'],
                'solverVersion': solverVersion
            }

            task = NewTask(task)
            print(task)
            transformingTasks.append(task)
        else:
            raise RuntimeError(f'the required file is not uploaded: \r {transformConfig["inputMesh"]}')

    transformingSize = len(transformingTasks)
    transformedSize = 0

    while transformedSize < transformingSize:
        for task in transformingTasks:
            status = WaitOnTask(task['taskId'])
            if status == 'success':
                transformedSize = transformedSize + 1
            elif status == 'error':
                raise RuntimeError(f'transformed failed for {task["objectId"]}: \r {task["taskParam"]}')
            sys.stdout.write(f'\r transformed {transformedSize} / {transformingSize}')
            sys.stdout.flush()

    # merge the files.
    parentIds = [x['objectId'] for x in transformingTasks] + [x['itemId'] for x in fileToStudioItem.values()]

    print(f"\r transformed {transformedSize} / {transformingSize}")
    print("\rstart merge process...")
    mergeJson = globalJson["merge"]
    item = {
        'status': "processing",
        'parentId': ','.join(parentIds),
        's3Path': f'{meshName}.meshmerged.json'
    }
    item = NewStudioItem(item)
    with open(os.path.join(dirName, mergeJson), 'r') as file:
        taskParam = file.read()
    task = {
        'taskType': "merge",
        'taskParam': taskParam,
        'objectId': item['itemId'],
        'solverVersion': solverVersion,
    }
    task = NewTask(task)

    print(f'merge.task:{task}')
    status = WaitOnTask(task['taskId'])
    if status == 'error':
        raise RuntimeError(f'merge failed: \r {task["taskParam"]}')
    with open(os.path.join(dirName, meshFile), 'r') as file:
        meshParam = file.read()

    mesh = {
        'meshName': f'{meshName}.meshmerged.json',
        'meshTags': tags,
        'meshFormat': '',
        'meshSize': 0,
        'meshParams': meshParam,
        'meshStatus': 'uploading',
        'solverVersion': solverVersion,
        'meshCompression': 'tar.gz'
    }

    finalMesh = flow360ApiPost("mesh", data=mesh)
    try:
        mesh = flow360ApiPost(f'studio/item/{item["itemId"]}/copyToMesh/{finalMesh["meshId"]}')
    except Exception as inst:
        print(inst.args)
    print("start mesh process on backend")
    print(finalMesh)
    return finalMesh


def noSlipWallsFromMapbc(mapbcFile):
    assert mapbcFile.endswith('.mapbc') == True
    if not os.path.exists(mapbcFile):
        print('mapbc file {0} does not exist'.format(mapbcFile))
        raise RuntimeError('FileNotFound')
    with open(mapbcFile, 'r') as f:
        mapbc = f.read()
    bc, noslipWalls = translate_boundaries(mapbc)
    return noslipWalls

def GetAccessAccount():
    return getUserCredential()['email']

def ChooseAccount():
    flow360dir = os.path.expanduser('~/.flow360')
    if os.path.exists('{0}/{1}'.format(flow360dir, 'email')) and \
            os.path.exists('{0}/{1}'.format(flow360dir, 'passwd')):
        with open(os.path.join(flow360dir, 'email'), 'r') as f:
            email = f.read()
        with open(os.path.join(flow360dir, 'passwd'), 'r') as f:
            password = f.read()
        try:
            supportedUsers = getSupportedUsers(email, password)
            for index, supUser in enumerate(supportedUsers):
                print('{:d} : {:s}'.format(index, str(supUser)))
            
            if len(supportedUsers) == 0:
                print("No supported users are available under the current user.")
                return
            while True:
                try:
                    choosedIndex = int(input('choose the index number of the user you want to support [0 - {:d}]: '.format(len(supportedUsers)-1)))
                    if choosedIndex>=0 and choosedIndex<len(supportedUsers):
                        break
                    else:
                        print('The input integer exceeds the limit, please input an integer again')
                        continue
                except ValueError:
                    print('Invalid input type, please input an integer value:')
                    continue
                
            Config.user['accessIdentityId'] = supportedUsers[choosedIndex]['identity']
            Config.user['accessEmail'] = supportedUsers[choosedIndex]['email']
            Config.user['accessUserId'] = getUserCredential()['userId']

            print('The following account is chosen for support purpose:')
            print('\t Email: {:s}'.format(supportedUsers[choosedIndex]['email']))

        except:
            raise Exception('Error: Failed to choose account for support with existing user:', email)
    else:
        raise Exception('Error: Can not find the credentials under .flow360 at home.')
        

def getFileExtention(fileName):
    _, ext = os.path.splitext(fileName)
    return ext
