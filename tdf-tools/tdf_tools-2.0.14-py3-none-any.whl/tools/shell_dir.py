import os
from tdf_tools.tools.print import Print
from ruamel import yaml


class ShellDir:
    __curDir = os.getcwd()
    # __curDir = "/Users/imwcl/Desktop/2dfire/埋点/flutter_reset_module"
    # __curDir = "/Users/xujian/Documents/2022_2dfire/flutter/package_tools/tdf_test/flutter_reset_module"

    # 目录校验，确保只能在壳下执行tdf_tools
    def dirInvalidate():
        try:
            with open("pubspec.yaml", encoding="utf-8") as f:
                doc = yaml.round_trip_load(f)
                if isinstance(doc, dict) and doc.__contains__("flutter"):
                    if (
                        isinstance(doc["flutter"], dict)
                        and doc["flutter"].__contains__("module") is not True
                    ):
                        Print.error("当前不是壳工程目录，禁止执行tdf_tools命令")
                f.close()
        except IOError:
            Print.error("当前不是壳工程目录，禁止执行tdf_tools命令")

    def getShellDir() -> str:
        return ShellDir.__curDir

    # 进入到壳内
    def goInShellDir():
        if os.path.exists(ShellDir.__curDir):
            os.chdir(ShellDir.__curDir)
        else:
            Print.error(ShellDir.__curDir + "路径不存在")

    # 进入到壳的 libs
    def goInShellLibDir():
        path = ShellDir.__curDir + "/lib"
        if os.path.exists(path):
            os.chdir(path)
        else:
            Print.error(path + "路径不存在")

    # 获取指定模块的目录
    def getModuleDir(module: str) -> str:
        return ShellDir.__curDir + "/../.tdf_flutter/" + module

    # 进入到指定模块内
    def goInModuleDir(module: str):
        module_path = ShellDir.getModuleDir(module)
        if os.path.exists(module_path):
            os.chdir(module_path)
        else:
            Print.error(module_path + "路径不存在")

    # 获取指定模块的 lib 目录
    def getModuleLibDir(module: str) -> str:
        return ShellDir.__curDir + "/../.tdf_flutter/" + module + "/lib"

    # 进入到指定模块 Lib 内
    def goInModuleLibDir(module: str):
        module_path = ShellDir.getModuleLibDir(module)
        if os.path.exists(module_path):
            os.chdir(module_path)
        else:
            Print.error(module_path + "路径不存在")

    # 获取到指定模块 tdf_intl 路径
    def getInModuleIntlDir(module: str):
        return ShellDir.__curDir + "/../.tdf_flutter/" + module + "/lib/tdf_intl"

    # 进入到指定模块 tdf_intl 内
    def goInModuleIntlDir(module: str):
        module_path = ShellDir.getInModuleIntlDir(module)
        if os.path.exists(module_path):
            os.chdir(module_path)
        else:
            Print.error(module_path + "路径不存在")

    # 进入.tdf_flutter文件夹
    def getInTdfFlutterDir():
        return ShellDir.getShellDir() + "/../.tdf_flutter"

    # 进入.tdf_flutter文件夹
    def goInTdfFlutterDir():
        __path = ShellDir.getInTdfFlutterDir()
        if not os.path.exists(__path):
            os.mkdir(__path)
        os.chdir(__path)

    # 进入缓存文件目录
    def goTdfCacheDir():
        ShellDir.goInShellDir()
        if os.path.exists("tdf_cache"):
            os.chdir("tdf_cache")
        elif not os.path.exists("tdf_cache"):
            create = input("当前目录没有找到tdf_cache缓存文件夹，是否创建？(y/n):")
            if create == "y":
                os.mkdir("tdf_cache")
            else:
                Print.error("Oh,it's disappointing.")
                exit(1)

    # 获取模块名
    def getModuleNameFromYaml(yaml_path: str) -> str:
        with open(yaml_path, "r", encoding="utf-8") as rF:
            dic = yaml.round_trip_load(rF.read())
            if dic is not None and dic.__contains__("name"):
                shellModule = dic["name"]
                return shellModule
            else:
                Print.error("读取壳模块模块名失败，请确保壳模块的pubspec.yaml配置了name属性")
