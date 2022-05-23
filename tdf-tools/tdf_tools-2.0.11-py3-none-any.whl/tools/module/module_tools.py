import json
from tdf_tools.tools.print import Print
from tdf_tools.tools.shell_dir import ShellDir


class ModuleTools:
    # 获取项目初始化数据
    def getInitJsonData():
        ShellDir.goTdfCacheDir()
        with open("initial_config.json", "r", encoding="utf-8") as readF:
            fileData = readF.read()
            readF.close()
            return json.loads(fileData)

    def getModuleNameList():
        initJsonData = ModuleTools.getInitJsonData()
        if initJsonData.__contains__("moduleNameList") and isinstance(
            initJsonData["moduleNameList"], list
        ):
            moduleNameList = initJsonData["moduleNameList"]
            return moduleNameList
        else:
            Print.error("❌ 请配置moduleNameList的值,以数组形式")

    def getModuleJsonData():  # 获取模块 git相关配置信息
        ShellDir.goTdfCacheDir()
        with open("module_config.json", "r", encoding="utf-8") as readF:
            fileData = readF.read()
            readF.close()
            return json.loads(fileData)
