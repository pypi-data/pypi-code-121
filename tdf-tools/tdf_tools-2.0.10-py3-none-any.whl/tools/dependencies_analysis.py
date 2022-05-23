# !/usr/bin/env python
# -*- coding: UTF-8 -*-

# 依赖分析【有向无环图，有向有环图】


import json
from mimetypes import init
import os
from ruamel import yaml
from tdf_tools.tools.print import Print
from tdf_tools.tools.shell_dir import ShellDir
from tdf_tools.tools.module.module_tools import ModuleTools


class DependencyNode:
    def __init__(self):
        self.nodeName = ""
        self.parent = []  # 父亲节点列表
        self.children = []  # 子孙节点列表
        self.isShell = False  # 是否是shell模块
        self.modulePath = ""  # 模块路径
        self.delete = False


class DependencyAnalysis:
    def __init__(self) -> None:
        self.__initJsonData__ = None
        self.__moduleNameList__ = None
        self.__shellName__ = None

    @property
    def __initJsonData(self):
        if self.__initJsonData__ is None:
            self.__initJsonData__ = ModuleTools.getInitJsonData()
        return self.__initJsonData__

    @property
    def __moduleNameList(self):
        if self.__moduleNameList__ is None:
            self.__moduleNameList__ = ModuleTools.getModuleNameList()
        return self.__moduleNameList__

    @property
    def __shellName(self):
        if self.__shellName__ is None:
            self.__shellName__ = self.__initJsonData["shellName"]
        return self.__shellName__

    # 分析lock文件，获取所有的packages
    def _analysisLock(self):
        # 读取lock内容
        with open("pubspec.lock", encoding="utf-8") as f:
            doc = yaml.round_trip_load(f)
            if isinstance(doc, dict) and doc.__contains__("packages"):
                f.close()
                return doc["packages"]

    # 生成依赖图
    def _generateDependenciesMap(self):
        for package in self.__moduleDependenciesMap:
            for module in self.__moduleNameList:
                if package == module:
                    # 到这一步表明当前这个模块属于开发模块且在当前模块的依赖模块列表中，是当前模块的子模块
                    self._mNodeDict[self.__moduleName].children.append(package)
                    self._mNodeDict[package].parent.append(self.__moduleName)

    # 返回二维数组，用于并发打tag
    def _generateDependenciesOrder(self):
        resList = []
        while self._existNode():
            itemList = []

            for item in self._mNodeDict:
                node = self._mNodeDict[item]
                if isinstance(node, DependencyNode):
                    if not node.delete:
                        if len(node.children) == 0:
                            itemList.append(node.nodeName)
                            node.delete = True

            deleteNodeList = []
            for item in self._mNodeDict:
                node = self._mNodeDict[item]
                if isinstance(node, DependencyNode):
                    if node.delete:
                        deleteNodeList.append(node.nodeName)

            for item in self._mNodeDict:
                node = self._mNodeDict[item]
                if isinstance(node, DependencyNode):
                    for deleteItem in deleteNodeList:
                        if node.children.__contains__(deleteItem):
                            node.children.remove(deleteItem)

            if len(itemList) == 0:
                break
            resList.append(itemList)
        return json.dumps(resList)

    # 返回一维数组，用于从下至上执行upgrade
    def _generateDependenciesOrderForUpgrade(self):
        resList = []
        while self._existNode():
            for item in self._mNodeDict:
                node = self._mNodeDict[item]
                if isinstance(node, DependencyNode):
                    if not node.delete:
                        if len(node.children) == 0:
                            resList.append(node.nodeName)
                            node.delete = True

            deleteNodeList = []
            for item in self._mNodeDict:
                node = self._mNodeDict[item]
                if isinstance(node, DependencyNode):
                    if node.delete:
                        deleteNodeList.append(node.nodeName)

            for item in self._mNodeDict:
                node = self._mNodeDict[item]
                if isinstance(node, DependencyNode):
                    for deleteItem in deleteNodeList:
                        if node.children.__contains__(deleteItem):
                            node.children.remove(deleteItem)

        print(resList)

        return resList

    def _existNode(self):
        for item in self._mNodeDict:
            node = self._mNodeDict[item]
            if isinstance(node, DependencyNode) and not node.delete:
                return True
        return False

    def _subChildCount(self, childName):
        for item in self._mNodeDict:
            node = self._mNodeDict[item]
            if isinstance(node, DependencyNode):
                if not node.delete:
                    if node.children.__contains__(childName):
                        node.children.remove(childName)

    def generate(self):

        self._mNodeDict = dict()
        # 初始化子模块的节点列表
        for module in self.__moduleNameList:
            node = DependencyNode()
            node.nodeName = module
            ShellDir.goInTdfFlutterDir()
            os.chdir(module)
            node.modulePath = os.getcwd()
            self._mNodeDict[module] = node
        # 初始化壳节点
        node = DependencyNode()
        node.nodeName = self.__shellName
        node.isShell = True
        ShellDir.goInShellDir()
        node.modulePath = os.getcwd()
        self._mNodeDict[node.nodeName] = node

        # 读取子模块lock文件
        for module in self.__moduleNameList:
            self.__moduleName = module
            # self.__moduleGenPath = projectModuleDir + "/" + module
            os.chdir(self._mNodeDict[module].modulePath)
            self.__moduleDependenciesMap = self._analysisLock()
            self._generateDependenciesMap()
        # 读取壳模块lock文件
        self.__moduleName = self.__shellName
        os.chdir(self._mNodeDict[self.__shellName].modulePath)
        self.__moduleDependenciesMap = self._analysisLock()
        self._generateDependenciesMap()

        return self._generateDependenciesOrder()

    def getDependencyOrder(self):

        self._mNodeDict = dict()
        # 初始化子模块的节点列表
        for module in self.__moduleNameList:
            node = DependencyNode()
            node.nodeName = module
            ShellDir.goInTdfFlutterDir()
            os.chdir(module)
            node.modulePath = os.getcwd()
            self._mNodeDict[module] = node
        # 初始化壳节点
        node = DependencyNode()
        node.nodeName = self.__shellName
        node.isShell = True
        ShellDir.goInShellDir()
        node.modulePath = os.getcwd()
        self._mNodeDict[node.nodeName] = node

        # 读取子模块lock文件
        for module in self.__moduleNameList:
            self.__moduleName = module
            # self.__moduleGenPath = projectModuleDir + "/" + module
            os.chdir(self._mNodeDict[module].modulePath)
            self.__moduleDependenciesMap = self._analysisLock()
            self._generateDependenciesMap()
        # 读取壳模块lock文件
        self.__moduleName = self.__shellName
        os.chdir(self._mNodeDict[self.__shellName].modulePath)
        self.__moduleDependenciesMap = self._analysisLock()
        self._generateDependenciesMap()

        return self._generateDependenciesOrderForUpgrade()
