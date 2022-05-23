import os
import shutil
from tdf_tools.tools.cli.module_deps_rewrite import ModuleDependenciesRewriteUtil
from tdf_tools.tools.config.config import CLIJsonConfig
from tdf_tools.tools.config.initial_json_config import InitialJsonConfig
from tdf_tools.tools.cmd import Cmd
from tdf_tools.tools.gitlab.gitlab_utils import GitlabUtils
from tdf_tools.tools.gitlab.python_gitlab_api import GitlabAPI
from tdf_tools.tools.print import Print
from tdf_tools.tools.shell_dir import ShellDir


class ProjectCLI(object):
    def initial(self):
        ShellDir.goInShellDir()
        if os.path.exists("tdf_cache"):
            Print.debug("tdf_cache中已存在项目配置文件。继续执行init命令会将tdf_cache和.tdf_flutter删除。")
            if input("你确定要继续执行init命令吗？(y/n)") == "y":
                if input("真的确定了吗？(y/n)") == "y":
                    if input("最后一遍，真的吗，不后悔？(y/n)") == "y":
                        if os.path.exists("tdf_cache"):
                            shutil.rmtree(r"tdf_cache")
                        ShellDir.goInShellDir()
                        os.chdir(os.path.abspath(r".."))
                        if os.path.exists(".tdf_flutter"):
                            shutil.rmtree(r".tdf_flutter")
                        Print.error("d")
                    else:
                        Print.error("exit")
                else:
                    Print.error("exit")
            else:
                Print.error("exit")
        ShellDir.goInShellDir()
        self.initInitialJson()
        self.cliDeps()

    def initInitialJson(self):
        moduleJson = CLIJsonConfig.getModuleConfig()
        ShellDir.goInShellDir()

        featureBranch = Cmd.run("git rev-parse --abbrev-ref HEAD").replace("\n", "")

        shellModule = ShellDir.getModuleNameFromYaml("pubspec.yaml")

        # 初始化开发的模块列表
        moduleList = []
        while True:
            moduleName = input("输入需要开发的模块名:(添加:+name，删除:-name，完成输入:!):")
            if moduleName != "":
                if moduleName == "!" or moduleName == "！":
                    break
                if moduleJson.get(moduleName[1:], -1) != -1:
                    if moduleName[0] == "+":
                        moduleList.append(moduleName[1:])
                        print("模块{0}已添加".format(moduleName[1:]))
                    elif moduleName[0] == "-":
                        moduleList.remove(moduleName[1:])
                        print("模块{0}已移除".format(moduleName[1:]))
                else:
                    if moduleName[0] == "+":
                        print("未从仓库中找到模块{0}，添加失败".format(moduleName[1:]))
                    elif moduleName[0] == "-":
                        print("已添加模块列表中未找到模块{0}".format(moduleName[1:]))
                moduleList = list(dict.fromkeys(moduleList))

                print("已选模块列表：{0}".format(moduleList))

        # 写入项目环境配置文件
        CLIJsonConfig.saveInConfig(
            featureBranch=featureBranch, shellModule=shellModule, moduleList=moduleList
        )

    # deps
    def cliDeps(self):
        config = InitialJsonConfig()
        featureBranch = config.featureBranch
        moduleNameList = config.moduleNameList
        moduleJsonData = CLIJsonConfig.getModuleConfig()

        # 数据校验
        self.validateConfig(moduleNameList, moduleJsonData)

        gitlabUtils = GitlabUtils()

        gitlabApi = GitlabAPI()

        for module in moduleNameList:
            Print.title(module)
            ShellDir.goInTdfFlutterDir()
            gitlabUtils.clone(module, moduleJsonData[module]["git"])
            os.chdir(module)
            gitlabApi.createBranch(moduleJsonData[module]["id"], featureBranch)
            gitlabUtils.pull()
            gitlabUtils.checkout(featureBranch)
        # 依赖 重写
        reWrite = ModuleDependenciesRewriteUtil()
        reWrite.rewrite()

    # 校验配置是否正确，所有需要开发的库是否存在于模块配置json文件中
    def validateConfig(self, moduleNameList, moduleJsonData):
        if isinstance(moduleJsonData, dict):
            for module in moduleNameList:
                if module not in moduleJsonData.keys():
                    Print.error(
                        "配置的开发模块{0}没有找到git仓库信息。请确保 1. 模块名配置正确； 2. 执行 tdf_tools module-update 更新git信息配置文件".format(
                            module
                        )
                    )
