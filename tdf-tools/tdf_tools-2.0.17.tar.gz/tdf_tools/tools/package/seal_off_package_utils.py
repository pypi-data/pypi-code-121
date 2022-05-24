#!/usr/bin/env python
# encoding=utf-8

import json
import os
import subprocess
import copy
from ruamel import yaml
import requests
from tdf_tools.tools.dependencies_analysis import DependencyAnalysis
from tdf_tools.tools.config.initial_json_config import InitialJsonConfig
from tdf_tools.tools.shell_dir import ShellDir

PRIVATE_REPOSITORY_HOST = "http://10.1.85.141"

# 版本号自增 依赖修改

# 读取当前文件夹内的pubspec.yaml文件


def yamlLoad():
    # 读取pubsepc.yaml内容
    with open('pubspec.yaml', encoding='utf-8') as f:
        doc = yaml.round_trip_load(f)
        if (isinstance(doc, dict)):
            f.close()
            return doc

# 规范版本号


def strictVersion(version):
    if isinstance(version, str):
        tagList = version.split('.')
        if len(tagList) == 3 and int(tagList[1]) <= 9:
            if len(tagList[2]) == 2:
                return version
            elif len(tagList[2]) == 1:
                return version + '1'
            else:
                print('❌ tag号规范检测失败，请严格按照规范修改tag号,例：x.y.z, （0<=x, 0<=y<=9, 00<=z<=99）')
                exit(-1)
        else:
            print('❌ tag号规范检测失败，请严格按照规范修改tag号,例：x.y.z, （0<=x, 0<=y<=9, 00<=z<=99）')
            exit(-1)

# 获取已经发布过的远程仓库列表


def getRemoteRepositories():
    try:
        r = requests.get(
            PRIVATE_REPOSITORY_HOST + '/webapi/packages?size=1000')
        mDict = json.loads(r.text)
        mRepositoryMap = {}
        for item in mDict['data']['packages']:
            mRepositoryMap[item['name']] = item['latest']
        return mRepositoryMap
    except:
        print('❌ 读取私库内模块列表失败，请确保私库正常运行')
        exit(-1)

# 版本号自增, tagNumber = 1019


def addVersion(tagNumber, shouldAdd=True):
    try:
        if shouldAdd:
            tagNumber = tagNumber + 1
        upgradeTag = "{0}.{1}.{2}".format(int(
            tagNumber / 1000), int((tagNumber % 1000) / 100), "{:0>2d}".format(tagNumber % 100))
        print("对{0}进行自增,自增后为{1}".format(tagNumber - 1, upgradeTag))
        return upgradeTag
    except Exception as ex:
        print('❌ 版本号自增失败:{0}'.format(ex))
        exit(-1)

# 版本号比对


def getUpgradeVersion(currentVersion, remoteVersion):
    try:
        currentVersionList = currentVersion.split('.')
        currentVersionNumber = int(currentVersionList[0]) * 1000 + int(
            currentVersionList[1]) * 100 + int(currentVersionList[2])

        # 如果远端版本为空，则直接对当前版本进行自增操作即可
        if remoteVersion == None:
            return addVersion(currentVersionNumber)

        remoteVersionList = remoteVersion.split('.')
        remoteVersionNumber = int(remoteVersionList[0]) * 1000 + int(
            remoteVersionList[1]) * 100 + int(remoteVersionList[2])

        if currentVersionNumber > remoteVersionNumber:
            return addVersion(currentVersionNumber, shouldAdd=False)

        if currentVersionNumber > remoteVersionNumber:
            return addVersion(currentVersionNumber)
        else:
            return addVersion(remoteVersionNumber)
    except Exception as ex:
        print('❌ 版本号比对出现异常:{0}'.format(ex))
        exit(-1)


def tagInfoObj():

    analysis = DependencyAnalysis()
    treeJson = json.loads(analysis.generate())
    print(treeJson)

    remoteRepositoryMap = getRemoteRepositories()
    initJsonData = InitialJsonConfig()

    result = {}

    for item in initJsonData.moduleNameList:
        ShellDir.goInTdfFlutterDir()
        os.chdir(item)
        print("检测模块：{0}".format(item))

        yamlInfo = yamlLoad()
        if yamlInfo.__contains__('version') is not True:
            print("❌模块{0}yaml文件中没有检测到version版本号字段，请设置".format(item))
            exit(-1)

        current = strictVersion(yamlInfo['version'])

        remote = None
        if remoteRepositoryMap.__contains__(item):
            remote = remoteRepositoryMap[item]

        result[item] = {
            "remote": remote,
            "current": current,
            "upgrade": getUpgradeVersion(current, remote),
            'sort': 0
        }

    for item in result:
        for index in range(len(treeJson)):
            if treeJson[index].__contains__(item):
                result[item]['sort'] = index

    exit(json.dumps(result))


# 修改依赖
def changeVersionAndDependencies(jsonData):

    # 例："{\"tdf_presell\":{\"remote\":\"1.0.05\",\"current\":\"1.0.04\",\"upgrade\":\"1.0.06\",\"sort\":1},\"tdf_goods_videos_manager\":{\"remote\":\"1.0.06\",\"current\":\"1.0.05\",\"upgrade\":\"1.0.07\",\"sort\":1},\"tdf_widgets\":{\"remote\":\"1.0.12\",\"current\":\"1.0.12\",\"upgrade\":\"1.0.13\",\"sort\":0}}"
    # tempStr = "{\"tdf_presell\":{\"remote\":\"1.0.05\",\"current\":\"1.0.04\",\"upgrade\":\"1.0.06\",\"sort\":1},\"tdf_goods_videos_manager\":{\"remote\":\"1.0.06\",\"current\":\"1.0.05\",\"upgrade\":\"1.0.07\",\"sort\":1},\"tdf_widgets\":{\"remote\":\"1.0.12\",\"current\":\"1.0.12\",\"upgrade\":\"1.0.13\",\"sort\":0}}"
    # jsonData = json.loads(tempStr)

    initJsonData = InitialJsonConfig()
    for item in initJsonData.moduleNameList:
        ShellDir.goInTdfFlutterDir()
        os.chdir(item)
        print("\n修改模块版本号和依赖：{0}".format(item))

        yamlInfo = yamlLoad()
        # dependency_overrides依赖
        dependencyOverridesDict = dict
        # dependencies依赖
        dependencyDict = dict
        if yamlInfo.__contains__('dependency_overrides'):
            dependencyOverridesDict = copy.deepcopy(
                yamlInfo['dependency_overrides'])

        if yamlInfo.__contains__('dependencies'):
            dependencyDict = copy.deepcopy(
                yamlInfo['dependencies'])

        # dependencyOverridesDict不为空，才需要修改dependencyDict
        # 修改规则：1.dependency中没有，dependency_overrides中有，则添加为tdg依赖方式
        #         2.dependency中有，dependency_overrides中有，则覆盖为tag依赖方式
        if dependencyOverridesDict is not None and isinstance(dependencyOverridesDict, dict) and dependencyOverridesDict.__len__() > 0:
            for dependencyOverridesItem in dependencyOverridesDict:
                upwardReference = True
                if dependencyOverridesItem in dependencyDict:
                    if isinstance(dependencyDict[dependencyOverridesItem], dict) and 'version' in dependencyDict[dependencyOverridesItem]:
                        itemDict = dependencyDict[dependencyOverridesItem]
                        if isinstance(itemDict, dict) and 'version' in itemDict:
                            versionStr = itemDict["version"]
                            if isinstance(versionStr, str) and versionStr.__contains__('^'):
                                upwardReference = True

                print('--- 修改节点{0}的依赖 如下'.format(dependencyOverridesItem))

                dependencyDict[dependencyOverridesItem] = {
                    "hosted": {
                        "name": "{0}".format(dependencyOverridesItem),
                        "url": "http://10.1.85.141"
                    },
                    "version": "{0}{1}".format('^' if upwardReference else '', jsonData[item]['upgrade'])
                }
                # 输出修改后的节点信息
                print(json.dumps(dependencyDict[dependencyOverridesItem]))

            # 重写
            try:
                yamlInfo['version'] = jsonData[item]['upgrade']
                del yamlInfo['dependency_overrides']
                yamlInfo['dependencies'] = dependencyDict

                with open('pubspec.yaml', 'w+', encoding='utf-8') as reW:
                    yaml.round_trip_dump(
                        yamlInfo, reW, default_flow_style=False, encoding='utf-8', allow_unicode=True)
                    reW.close()
            except Exception as e:
                print('重写时出现异常，错误原因：{0}'.format(e))
                exit(-1)


def createAndPushTag(tagModuleList):
    initJsonData = InitialJsonConfig()

    for moduleName in tagModuleList:

        isExist = False
        for item in initJsonData.moduleNameList:
            if moduleName == item:
                isExist = True
                ShellDir.goInTdfFlutterDir()
                os.chdir(item)
                print("\n{0}模块开始执行tag操作...".format(item))

                # 在yaml中获version，作为tag
                yamlInfo = yamlLoad()
                tag = yamlInfo['version']
                print("获取tag号：{0}".format(tag))

                print('exec: git tag {0}'.format(tag))
                res = os.popen('git tag {0}'.format(tag)).read()
                print(res)

                print('exec: git push origin {0}'.format(tag))
                res = os.popen('git push origin {0}'.format(tag)).read()
                print(res)

        if isExist is False:
            print('模块{0}没有找到'.format())
            exit(-1)
