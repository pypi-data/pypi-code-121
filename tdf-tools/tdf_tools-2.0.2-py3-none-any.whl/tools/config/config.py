import json
import os
import shutil

from tdf_tools.tools.gitlab.python_gitlab_api import GitlabAPI
from tdf_tools.tools.shell_dir import ShellDir


class CLIJsonConfig:
    # 写入项目环境配置文件
    def saveInConfig(featureBranch: str, shellModule: str, moduleList: list):
        ShellDir.goInShellDir()
        if os.path.exists("tdf_cache") is not True:
            os.mkdir("tdf_cache")
        os.chdir("tdf_cache")

        with open("initial_config.json", "w", encoding="utf-8") as wf:
            initialDic = dict()
            initialDic["featureBranch"] = featureBranch
            initialDic["shellName"] = shellModule
            initialDic["moduleNameList"] = moduleList
            wf.write(json.dumps(initialDic, indent=2))
            wf.close()

    # 获取模块信息配置文件
    def getModuleConfig():
        ShellDir.goInShellDir()
        if os.path.exists("tdf_cache") is not True:
            os.mkdir("tdf_cache")
        os.chdir("tdf_cache")

        # 不存在，则拉取
        jsonData = dict
        if os.path.exists("module_config.json") is not True:
            CLIJsonConfig.__initModuleConfigJson()

        with open("module_config.json", "r", encoding="utf-8") as rf:
            jsonData = json.loads(rf.read())
            rf.close()
            return jsonData

    # 初始化模块信息配置json文件
    def __initModuleConfigJson():
        gitlabApi = GitlabAPI()
        moduleJson = gitlabApi.getModuleConfigJson()

        with open("module_config.json", "w+", encoding="utf-8") as wF:
            wF.write(json.dumps(moduleJson, indent=2))
            wF.close()

    # 更新flutter模块配置信息
    def updateModuleConfig():
        ShellDir.goTdfCacheDir()
        if os.path.exists("module_config.json"):
            os.remove("module_config.json")

        if os.path.exists("flutter_module_config"):
            shutil.rmtree(r"flutter_module_config")

        os.system(
            "git clone git@git.2dfire.net:app/flutter/tools/flutter_module_config.git"
        )
        os.chdir("flutter_module_config")
        # 请求更新gitlab上的模块配置信息
        CLIJsonConfig.requestUpdateGitlabModuleConfig()

        ShellDir.goTdfCacheDir()
        if os.path.exists("flutter_module_config"):
            shutil.rmtree(r"flutter_module_config")

        CLIJsonConfig.__initModuleConfigJson()

    # 更新模块配置信息
    def requestUpdateGitlabModuleConfig():
        FLUTTER_GROUP_ID = "1398"  # Flutter仓库组

        HPP_FLUTTER_GROUP_ID = "1489"  # 火拼拼的Flutter仓库组
        FLUTTER_REPOSITORY_GROUP_IDS = [FLUTTER_GROUP_ID, HPP_FLUTTER_GROUP_ID]

        # start
        projectInfo = dict()

        api = GitlabAPI()

        for groupId in FLUTTER_REPOSITORY_GROUP_IDS:
            groupProjectList = api.get_all_projects_in_group(groupId)
            for project in groupProjectList:
                tup = api.getContent(project.id, project.name)
                if tup[0] == True:
                    print(
                        "{0}, {1}, {2}, {3}".format(
                            tup[1],
                            project.id,
                            project.ssh_url_to_repo,
                            project.namespace["name"],
                        )
                    )
                    projectInfo[tup[1]] = dict()
                    projectInfo[tup[1]]["id"] = project.id
                    projectInfo[tup[1]]["git"] = project.ssh_url_to_repo
                    projectInfo[tup[1]]["type"] = project.namespace["name"]

        ShellDir.goTdfCacheDir()
        os.chdir("flutter_module_config")
        file = "module_config.json"
        if os.path.exists(file):
            os.remove(file)
        f = open(file, "w+")
        f.write(json.dumps(projectInfo, indent=2))
        f.close()

        os.system("git add .")
        os.system("git commit -m '更新模块git信息配置文件'")
        os.system("git push")
