#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# 模块重写脚本

import os
from ruamel import yaml
from tdf_tools.tools.dependencies_analysis import DependencyAnalysis
from tdf_tools.tools.print import Print
from tdf_tools.tools.module.module_tools import ModuleTools
from tdf_tools.tools.shell_dir import ShellDir


class ModuleDependenciesRewriteUtil:
    def __init__(self):
        Print.debug("开始进行依赖重写")
        self.moduleJsonData = ModuleTools.getModuleJsonData()
        self.moduleNameList = ModuleTools.getModuleNameList()
        self.initJsonData = ModuleTools.getInitJsonData()

    # 分析lock文件，获取所有的packages
    def _analysisLock(self):
        os.chdir(self.__moduleGenPath)
        # 分析前先执行pub upgrade
        os.popen("flutter pub upgrade").read()

        # 读取lock内容
        with open("pubspec.lock", encoding="utf-8") as f:
            doc = yaml.round_trip_load(f)
            if isinstance(doc, dict) and doc.__contains__("packages"):
                f.close()
                return doc["packages"]

    # 是否是壳模块
    def _isShellModule(self):
        return self.moduleJsonData[self.__moduleName]["type"] == "app"

    # 确认哪些依赖需要重写
    def _confirmRewriteDependencies(self, isShell):
        if isShell:  # 壳模块重写所有配置的依赖
            for item in self.moduleNameList:
                if item != self.__moduleName:  # 壳自己不加入重写列表
                    self.__needRewriteDependencies.append(item)
        else:  # 如果不是壳模块，则进行lock文件内的package列表和开发模块匹配，匹配上则添加到override列表
            for package in self.__moduleDependenciesMap:
                for module in self.moduleNameList:
                    if package == module:
                        self.__needRewriteDependencies.append(module)

        Print.stage("{0}中以下依赖将被override".format(self.__moduleName))
        Print.debug(self.__needRewriteDependencies)

    def _addOverrideDependencies(self):
        mDict = dict()
        for item in self.__needRewriteDependencies:
            mDict[item] = {"path": "../{0}/".format(item)}

        return mDict

    # 添加dependency_overrides

    def _rewriteDependencies(self, isShell):
        os.chdir(self.__moduleGenPath)
        with open("pubspec.yaml", encoding="utf-8") as f:
            doc = yaml.round_trip_load(f)
            if isinstance(doc, dict):
                self._confirmRewriteDependencies(isShell)
                if (
                    doc.__contains__("dependency_overrides")
                    and doc["dependency_overrides"] is not None
                ):
                    doc["dependency_overrides"] = None

                # 重写依赖
                overrideDict = dict()
                for item in self.__needRewriteDependencies:
                    if isShell:
                        overrideDict[item] = {
                            "path": "../.tdf_flutter/{0}/".format(item)
                        }
                    else:
                        overrideDict[item] = {"path": "../{0}/".format(item)}
                if len(self.__needRewriteDependencies) > 0:
                    doc["dependency_overrides"] = overrideDict

                with open("pubspec.yaml", "w+", encoding="utf-8") as reW:
                    yaml.round_trip_dump(
                        doc,
                        reW,
                        default_flow_style=False,
                        encoding="utf-8",
                        allow_unicode=True,
                    )
                    reW.close()
                    # 依赖重写完，执行pub upgrade更新lock文件
                    os.popen("flutter pub upgrade").read()
                    Print.debug("lock文件已更新")
            f.close()

    # 添加dependency_overrides，如果已存在模块的override，则不修改

    def _rewriteDependenciesIfUpdate(self, isShell):
        os.chdir(self.__moduleGenPath)
        with open("pubspec.yaml", encoding="utf-8") as f:
            doc = yaml.round_trip_load(f)
            if isinstance(doc, dict):
                self._confirmRewriteDependencies(isShell)

                global existUpdate
                existUpdate = False

                # 删除不存在于重写依赖列表中的key
                if (
                    doc.__contains__("dependency_overrides")
                    and doc["dependency_overrides"] is not None
                    and isinstance(doc["dependency_overrides"], dict)
                ):
                    keyList = list(doc["dependency_overrides"].keys())
                    for item in keyList:
                        if item not in self.__needRewriteDependencies:
                            Print.debug("${0}依赖被删除".format(item))
                            existUpdate = True
                            del doc["dependency_overrides"][item]

                if doc.__contains__("dependency_overrides"):
                    overrideDict = doc["dependency_overrides"]
                    if overrideDict is None:
                        overrideDict = dict()
                else:
                    overrideDict = dict()
                for item in self.__needRewriteDependencies:
                    if (
                        doc.__contains__("dependency_overrides")
                        and doc["dependency_overrides"] is not None
                        and isinstance(doc["dependency_overrides"], dict)
                        and doc["dependency_overrides"].get(item, -1) != -1
                    ):
                        Print.debug("${0}依赖已存在（不予修改）".format(item))
                    else:
                        Print.debug("${0}依赖不存在（添加）".format(item))
                        existUpdate = True
                        if isShell:
                            overrideDict[item] = {
                                "path": "../.tdf_flutter/{0}/".format(item)
                            }
                        else:
                            overrideDict[item] = {"path": "../{0}/".format(item)}
                doc["dependency_overrides"] = overrideDict
                if existUpdate:
                    with open("pubspec.yaml", "w+", encoding="utf-8") as reW:
                        yaml.round_trip_dump(
                            doc,
                            reW,
                            default_flow_style=False,
                            encoding="utf-8",
                            allow_unicode=True,
                        )
                        reW.close()
                        # 依赖重写完，执行pub upgrade更新lock文件
                        os.popen("flutter pub upgrade").read()
                        Print.debug("lock文件已更新")
                else:
                    Print.debug("yaml无更新")

            f.close()

    # 重写依赖 本地依赖

    def rewrite(self, reWriteOnlyChange=False):
        for module in self.moduleNameList:
            Print.title("模块{0}依赖分析..".format(module))
            ShellDir.goInTdfFlutterDir()
            os.chdir(module)
            self.__moduleGenPath = os.getcwd()
            # 这一步会生成lock文件
            self.__moduleDependenciesMap = self._analysisLock()

        Print.title("壳依赖分析..")
        ShellDir.goInShellDir()
        self.__moduleGenPath = os.getcwd()
        self.__moduleDependenciesMap = self._analysisLock()

        # 分析依赖树，从下至上之行upgrade
        dependencyAnalysis = DependencyAnalysis()
        dependencyList = dependencyAnalysis.getDependencyOrder()

        moduleLength = len(dependencyList)
        for module in dependencyList[: moduleLength - 1]:
            self.__moduleName = module
            ShellDir.goInTdfFlutterDir()
            os.chdir(module)
            self.__moduleGenPath = os.getcwd()
            self.__moduleDependenciesMap = self._analysisLock()
            self.__needRewriteDependencies = []
            if reWriteOnlyChange:
                self._rewriteDependenciesIfUpdate(isShell=False)
            else:
                self._rewriteDependencies(isShell=False)
        ShellDir.goInShellDir()
        self.__moduleName = self.initJsonData["shellName"]
        self.__moduleGenPath = os.getcwd()
        self.__moduleDependenciesMap = self._analysisLock()
        self.__needRewriteDependencies = []
        if reWriteOnlyChange:
            self._rewriteDependenciesIfUpdate(isShell=True)
        else:
            self._rewriteDependencies(isShell=True)
