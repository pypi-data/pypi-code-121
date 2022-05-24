#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# gitlab api

import gitlab
from ruamel import yaml
import json
import os
from tdf_tools.tools.print import Print


class GitlabAPI:

    __HOST = "https://git.2dfire.net"

    def __init__(self):
        private_token = self.__getPrivateToken()
        self.gl = gitlab.Gitlab(
            GitlabAPI.__HOST, private_token=private_token, api_version="4"
        )

    def get_all_projects_in_group(self, group_id):
        # 拿到顶层group
        print("读取groupId为{0}的仓库内所有项目...".format(group_id))
        group = self.gl.groups.get(group_id)
        projects = group.projects.list(include_subgroups=True, all=True)
        print("读取完成")
        return projects

    # 通过项目id获取yaml文件内容
    def getContent(self, project_id, project_name):
        project = self.gl.projects.get(project_id)
        try:
            print("读取模块：{0}".format(project_name))
            f = project.files.get(file_path="pubspec.yaml", ref="master")
            doc = yaml.round_trip_load(f.decode())
            print("写入配置文件")
            return (True, doc["name"], True)
        except Exception:
            print("没有yaml文件，不是flutter模块")
            return (False, "", False)

    # 获取module_config.json文件内容
    def getModuleConfigJson(self):
        project = self.gl.projects.get(6093)
        try:
            f = project.files.get(file_path="module_config.json", ref="master")
            return json.loads(f.decode())
        except Exception:
            Print.error("读取module_config.json失败")

    # 为project创建分支
    def createBranch(self, project_id, branch):
        project = self.gl.projects.get(project_id)
        try:
            project.branches.get(branch)
            Print.str("远端分支{0}已存在".format(branch))
        except Exception:
            Print.str("远程分支不存在，创建...")
            project.branches.create({"branch": branch, "ref": "master"})

    def createMR(self, project_id, source_branch, target_branch, title="default"):
        project = self.gl.projects.get(project_id)
        try:
            project.mergerequests.create(
                {
                    "source_branch": source_branch,
                    "target_branch": target_branch,
                    "assignee_id": 819,
                    "title": title,
                }
            )
        except Exception as e:
            Print.str("MR创建失败")
            Print.str(e)
            # sys.stdout.flush()

    def __getPrivateToken(self):
        token = ""
        tokenPath = os.path.abspath(
            os.path.join(os.path.expanduser("~"), ".tdf_tools_config")
        )

        if not os.path.exists(tokenPath):
            Print.warning("不存在~/.tdf_tools_config文件，请创建并配置相关必需属性如下：")
            inputStr = input("请输入需要你的 git_private_token：")
            if len(inputStr) > 0:
                f = open(tokenPath, "w+")
                f.write("git_private_token=" + inputStr)
                f.close()

        if os.path.exists(tokenPath):
            f = open(tokenPath)
            line = f.readline()
            while line:
                if line.__contains__("="):
                    key = line.split("=")[0]
                    value = line.split("=")[1]
                    if key == "git_private_token":
                        token = value.replace("\n", "")
                line = f.readline()

            f.close()
        else:
            Print.error("不存在~/.tdf_tools_config文件，请创建并配置相关必需属性如下", shouldExit=False)
            Print.error("git_private_token=***")
        return token
