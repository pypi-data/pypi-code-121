import json
import os
from tdf_tools.tools.config.initial_json_config import InitialJsonConfig
from tdf_tools.tools.config.module_json_config import ModuleItemType, ModuleJsonConfig
from tdf_tools.tools.regular_tool import RegularTool
from tdf_tools.tools.shell_dir import ShellDir
from tdf_tools.tools.print import Print


class TranslateLintItil:
    def __init__(self, file_path: str, un_intl_strs: list[str]):
        # 未国际化文件路径
        self.file_path = file_path
        # 文件中没有国际化的字符串
        self.un_intl_strs = un_intl_strs


class TranslateLintImport:
    def __init__(self, file_path: str, import_strs: list[str]):
        # import 错误的文件路径
        self.file_path = file_path
        # import 错误的字符串
        self.import_strs = import_strs


class TranslateLintResult:
    def __init__(
        self,
        un_intls: list[TranslateLintItil],
        intl_strs: list[str],
        intl_json: list[str],
        imports: list[TranslateLintImport],
    ):
        # 没有使用 .intl 修饰的中文字符串
        self.un_intls = un_intls
        # 使用 .intl 修饰的中文字符串
        self.intl_strs = intl_strs
        # i18n.json 中没用到的国际化字符串
        self.intl_json = intl_json
        # 不符合规范的 import
        self.imports = imports


class TranslateLint:
    """
    国际化相关：检测源码中是否还有没国际化的文案
    """

    def start(self):
        """
        以交互的方式选择需要 lint 的模块
        """
        businessModuleList = self.businessModuleList()
        Print.str("检测到以下模块可执行国际化lint：")
        Print.str(businessModuleList)
        inputStr = input("请输入需要执行 lint 的模块名(input ! 退出, all 全选)：")
        if inputStr == "!" or inputStr == "！":
            exit(0)
        elif inputStr == "all":
            self.__lint_all()
            exit(0)
        elif inputStr in businessModuleList:
            self.module(inputStr)
            exit(0)

    def module(self, name: str):
        """
        指定模块 lint
        """
        result = self.get_lint_module_result(name)
        if self.__lint_result(result):
            Print.stage(name + " 模块国际化 lint 通过")
        else:
            Print.error(name + " 模块国际化 lint 失败")

    def path(self, path: str):
        """
        指定模块路径 lint，路径为 lib 路径
        """
        result = self.__lint_intl_path(path)
        if self.__lint_result(result):
            Print.title(path + " 路径国际化 lint 通过")
        else:
            Print.error(path + " 路径国际化lint 失败")

    def get_lint_module_result(self, module_name: str) -> TranslateLintResult:
        print("\n")
        Print.title(module_name + " 模块国际化 lint 开始执行")
        target_path = ShellDir.getModuleLibDir(module_name)
        if os.path.exists(target_path):
            return self.__lint_intl_path(target_path)
        else:
            Print.error(target_path + "路径不存在")

    def __lint_all(self):
        results = []
        pass_result = True
        for module in self.businessModuleList():
            result = self.get_lint_module_result(module)
            results.append(result)
            if not self.__lint_result(result):
                pass_result = False
                Print.error(module + " 模块国际化 lint 失败", shouldExit=False)
            else:
                Print.title(module + " 模块国际化 lint 成功")

        if pass_result:
            print("\n")
            Print.title("国际化 lint 通过")
        else:
            Print.error("国际化 lint 失败")

    # 指定路径 lint，path 的必须是 lib 文件
    def __lint_intl_path(self, path: str) -> TranslateLintResult:
        # 没有使用 .intl 修饰的中文字符串
        un_intls = []
        # 使用 .intl 修饰的中文字符串
        intl_strs = []
        # 所有的 dart 文件路径
        dart_files = []

        # 不符合的 imports
        imports = []
        module_name = ShellDir.getModuleNameFromYaml(path + "/../pubspec.yaml")
        right_import = self.get_module_import_str(module_name)

        i18n_json: dict = self.__get_i18n_json(path)
        Print.stage("lint 路径：" + path)
        for root, __, files in os.walk(path):
            for file in files:
                # 过滤掉 tdf_intl 目录下的 dart 文件
                if (
                    file.endswith(".dart")
                    and not root.__contains__("/tdf_intl/")
                    and not file.endswith(".tdf_router.dart")
                ):
                    dart_files.append(root + "/" + file)
        for file in dart_files:
            f = open(file)
            file_content = f.read()
            file_content = RegularTool.delete_remark(file_content)
            # 所有的 intl import
            all_imports = RegularTool.find_intl_imports(file_content)
            # 错误的 intl import
            err_imports = list(filter(lambda x: x != right_import, all_imports))
            if len(err_imports) > 0:
                un_import = TranslateLintImport(file, err_imports)
                imports.append(un_import)

            # lines = file_content.splitlines()
            # file_content = "".join(lines)
            file_content = RegularTool.delete_track(file_content)
            file_content = RegularTool.delete_router(file_content)
            file_content = RegularTool.delete_deprecated(file_content)
            # 寻找加上 .intl 的文案，并删除掉，以免影响 下面的操作
            _intl_strs = RegularTool.find_intl_str(file_content)
            intl_strs += _intl_strs
            file_content = RegularTool.delete_intl_str(file_content)
            # 寻找没有国际化的 文案
            _un_intl_strs = RegularTool.find_chinese_str(file_content)
            if len(_un_intl_strs) > 0:
                un_intl = TranslateLintItil(file, _un_intl_strs)
                un_intls.append(un_intl)
            f.close()

        # intl_strs 去重
        intl_strs = list(set(intl_strs))
        new_intl_strs = []
        # 对比加上 .intl 的文案 和 i18n_json里面的差异
        i18n_json_keys = list(i18n_json.keys())
        for key in intl_strs:
            key = eval(repr(key).replace("\\\\", "\\"))
            if key in i18n_json_keys:
                i18n_json_keys.remove(key)
            else:
                new_intl_strs.append(key)

        return TranslateLintResult(un_intls, new_intl_strs, i18n_json_keys, imports)

    # 获取 i8n.json 的数据
    def __get_i18n_json(self, path: str) -> dict[str:str]:
        target_path = path + "/tdf_intl/i18n.json"
        if os.path.exists(target_path):
            with open(target_path, "r", encoding="utf-8") as json_file:
                json_str = json_file.read()
                json_dict = json.loads(json_str)
                return json_dict
        else:
            return {}

    # 校验 lint 的结果
    def __lint_result(self, result: TranslateLintResult) -> bool:

        if len(result.intl_json) > 0:
            Print.warning("i18n.json 中有以下字符串没有使用到：")
            Print.str(result.intl_json)

        if len(result.intl_strs) > 0:
            Print.warning("以下 .intl 修饰的字符串没有添加到 i18n.json 中：")
            Print.str(result.intl_strs)

        if len(result.un_intls) > 0:
            Print.warning("以下文件中有没国际化的中的字符串：")
            for i in result.un_intls:
                file_name = i.file_path.split(r"/")[-1]
                Print.title(file_name + " 文件中有以下未国际化的字符串：")
                Print.str(i.un_intl_strs)

        if len(result.imports) > 0:
            Print.warning("以下文件中有没不符合规范的 import ：")
            for i in result.imports:
                file_name = i.file_path.split(r"/")[-1]
                Print.title(file_name + " 文件中有以下未国际化的字符串：")
                Print.str(i.import_strs)

        return (
            len(result.un_intls) == 0
            and len(result.intl_json) == 0
            and len(result.intl_strs) == 0
            and len(result.imports) == 0
        )

    # 获取模块正确的 import 语句
    def get_module_import_str(self, module_name: str) -> str:
        return "import 'package:{name}/tdf_intl/{name}_i18n.dart';".format(
            name=module_name
        )

    # 可以进行国际化的列表
    def businessModuleList(self) -> list:
        self.__initialConfig = InitialJsonConfig()
        self.__moduleConfig = ModuleJsonConfig()
        businessModuleList = []
        for item in self.__initialConfig.moduleNameList:
            moudle_item = self.__moduleConfig.get_item(item)
            if (
                moudle_item.type == ModuleItemType.Module
                or moudle_item.type == ModuleItemType.Lib
                or moudle_item.type == ModuleItemType.Plugin
            ):
                businessModuleList.append(item)
        return businessModuleList
