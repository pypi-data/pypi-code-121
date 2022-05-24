import json
import os
from typing import Tuple
from tdf_tools.tools.print import Print
from tdf_tools.tools.shell_dir import ShellDir


class InitialJsonConfig:
    def __init__(self):
        config = self.__getInitialConfig()
        self.featureBranch = config[0]
        self.shellName = config[1]
        self.moduleNameList = config[2]

    # 获取环境配置文件
    def __getInitialConfig(self) -> Tuple:
        ShellDir.goInShellDir()
        if os.path.exists("tdf_cache") is not True:
            Print.error("读取项目环境配置文件initial_config.json失败")
        os.chdir("tdf_cache")

        jsonData = dict
        with open("initial_config.json", "r", encoding="utf-8") as rf:
            jsonData = json.loads(rf.read())
            rf.close()
            if (
                isinstance(jsonData, dict)
                and jsonData.__contains__("featureBranch")
                and jsonData.__contains__("shellName")
                and jsonData.__contains__("moduleNameList")
            ):
                return (
                    jsonData["featureBranch"],
                    jsonData["shellName"],
                    jsonData["moduleNameList"],
                )
            else:
                Print.error("读取项目环境配置文件initial_config.json失败")
