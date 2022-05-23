import json
from tdf_tools.tools.config.config import CLIJsonConfig
from tdf_tools.tools.shell_dir import ShellDir
from enum import Enum, unique


@unique
class ModuleItemType(Enum):
    App = 0
    Plugin = 1
    Module = 2
    Lib = 3


class ModuleItemConfig:
    def __init__(self, id: int, git: str, type: ModuleItemType) -> None:
        self.id = id
        self.git = git
        self.type = type


class ModuleJsonConfig:
    def __init__(self) -> None:
        self.__data = self.__getModuleJsonData()

    def get_item(self, module_name: str) -> ModuleItemConfig:
        item = self.__data[module_name]
        id = item["id"]
        git = item["git"]
        type_str = item["type"]
        type = ModuleItemType.App
        if type_str == "plugins":
            type = ModuleItemType.Plugin
        elif type_str == "modules":
            type = ModuleItemType.Module
        elif type_str == "libs":
            type = ModuleItemType.Lib
        return ModuleItemConfig(id, git, type)

    def __getModuleJsonData(self):  # 获取模块 git相关配置信息
        return CLIJsonConfig.getModuleConfig()
