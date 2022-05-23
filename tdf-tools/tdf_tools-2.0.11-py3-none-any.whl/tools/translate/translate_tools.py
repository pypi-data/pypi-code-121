import json
import os
from tdf_tools.tools.config.initial_json_config import InitialJsonConfig
from tdf_tools.tools.config.module_json_config import ModuleJsonConfig, ModuleItemType
from tdf_tools.tools.platform_tools import PlatformTools
from tdf_tools.tools.print import Print
from tdf_tools.tools.regular_tool import RegularTool
from tdf_tools.tools.shell_dir import ShellDir
from googletrans import Translator

from tdf_tools.tools.translate.translate_lint import TranslateLint


class TranslateTools:
    def __init__(self):
        self.__i18nList = ["zh-ch", "en", "th", "zh-tw"]

    # 交互式 国际化
    def translate(self):
        businessModuleList = self.__businessModuleList()

        Print.str("检测到以下模块可执行国际化脚本：")
        Print.str(businessModuleList)
        while True:
            targetModule = input("请输入需要执行国际化脚本的模块名(input ! 退出，all 所有模块执行)：")
            if targetModule == "!" or targetModule == "！":
                exit(0)
            elif targetModule == "all":
                for module in businessModuleList:
                    self.translate_module(module)
                exit(0)
            else:
                self.translate_module(targetModule)
                exit(0)

    # 指定 模块国际化
    def translate_module(self, name):
        businessModuleList = self.__businessModuleList()
        if name in businessModuleList:
            Print.title(name + " 模块国际化脚本开始执行")
            self.__generateTranslate(name)
            Print.title(name + " 模块国际化执行完成，生成 tdf_intl 相关文件")
        else:
            Print.error(name + " 模块不在开发列表中")

    # 可以进行国际化的列表
    def __businessModuleList(self) -> list:
        return TranslateLint().businessModuleList()

    # 入口
    def __generateTranslate(self, targetModule):
        ShellDir.goInShellLibDir()
        if not os.path.exists("tdf_intl"):
            os.mkdir("tdf_intl")

        # 进入tdf_intl目录
        # tdf_intl文件夹下包含i18n文件夹，其中存放4个dart文件，分别对应四种语言
        # tdf_intl文件夹下还包含一个origin.txt文件，用于存放需要转化的文案，每个文案为一行
        ShellDir.goInModuleLibDir(targetModule)
        if not os.path.exists("tdf_intl"):
            os.mkdir("tdf_intl")
        os.chdir("tdf_intl")
        tdfIntlDir = PlatformTools.curPath()
        # 如果没有i18n文件夹则生成
        self.__generate_i18n_files(tdfIntlDir, targetModule)

        # 检查是否有未使用 intl 的中文字符串
        self.__check_unintl_strs(targetModule)

        # 检查是否有 import 错误的文件
        self.__check_err_intl_import(targetModule)

        # 是否更新 i18n.json 文件
        self.__check_need_update_json(tdfIntlDir, targetModule)

        # 通过 i18n.json 生成各个翻译后的 dart 文件
        self.__generate_translate_dart_file(tdfIntlDir, targetModule)

    # 生成 i18n 相关的文件
    def __generate_i18n_files(self, tdfIntlDir, targetModule):
        Print.title("开始生成 i18n 相关的文件")
        if not os.path.exists("i18n"):
            os.mkdir("i18n")

        if not os.path.exists("i18n.json"):
            Print.str("生成" + "i18n.json 文件")
            initF = open(tdfIntlDir + "/i18n.json", "w+", encoding="utf-8")
            initF.write("{}")
            initF.close()

            for targetFileNameSuffix in self.__i18nList:
                os.chdir(tdfIntlDir + "/i18n")
                targetFileName = (
                    targetModule
                    + "_"
                    + targetFileNameSuffix.replace("-", "_")
                    + ".dart"
                )

                if not os.path.exists(targetFileName):
                    Print.str("生成" + targetFileName + " 文件")
                    newI18nFile = open(targetFileName, "w+")
                    newI18nFile.write(
                        "Map<String, String> "
                        + targetFileNameSuffix.replace("-", "")
                        + "Map = {\n};"
                    )
                    newI18nFile.close()

    # 检查是否有错误导入的 import
    def __check_err_intl_import(self, targetModule):
        Print.title("检查是否有错误导入的 import")
        lint = TranslateLint()
        result = lint.get_lint_module_result(targetModule)
        right_import = lint.get_module_import_str(targetModule)
        if len(result.imports) > 0:
            err_imports = []
            for i in result.imports:
                err_imports += i.import_strs
            Print.line()
            Print.str(err_imports)
            Print.line()
            input_str = input("检查到有以上 import 错误，是否自动替换 ？(Y 为确认)：")
            if input_str == "Y" or input_str == "y":
                for i in result.imports:
                    Print.title("开始替换 import 的文件：" + i.file_path.split("/")[-1])
                    read_file = open(i.file_path, "r", encoding="utf-8")
                    file_content = read_file.read()
                    for str in i.import_strs:
                        Print.str("文件：" + i.file_path.split("/")[-1] + "开始替换 import")
                        file_content = RegularTool.replace_intl_imports(
                            file_content, right_import
                        )
                    read_file.close()
                    with open(i.file_path, "w+", encoding="utf-8") as originF:
                        originF.write(file_content)
                        originF.close()
                    os.system("dart format {0}".format(i.file_path))

    # 检查是否有未使用 intl 的中文字符串
    def __check_unintl_strs(self, targetModule):
        lint = TranslateLint()
        right_import = lint.get_module_import_str(targetModule)
        Print.title("检查是否有未使用 intl 的中文字符串")
        result = lint.get_lint_module_result(targetModule)
        if len(result.un_intls) > 0:
            un_intls = []
            for i in result.un_intls:
                un_intls += i.un_intl_strs
            Print.line()
            Print.str(un_intls)
            Print.line()
            input_str = input("检查到有以上中文字符串没使用 intl，是否自动加上 .intl？(Y 为确认)：")
            if input_str == "Y" or input_str == "y":
                for i in result.un_intls:
                    Print.title("开始替换的文件：" + i.file_path.split("/")[-1])
                    read_file = open(i.file_path, "r", encoding="utf-8")
                    file_content = read_file.read()
                    # 添加 import
                    if not file_content.__contains__(right_import):
                        file_content = right_import + "\n" + file_content

                    # 替换 intl
                    for str in i.un_intl_strs:
                        Print.str(
                            "文件："
                            + i.file_path.split("/")[-1]
                            + " "
                            + str
                            + " 添加 intl 后缀"
                        )

                    # 删除其他干扰项
                    file_content = RegularTool.delete_remark(file_content)
                    file_content = RegularTool.delete_router(file_content)
                    file_content = RegularTool.delete_deprecated(file_content)
                    file_content = RegularTool.replace_chinese_str(file_content, str)
                    read_file.close()
                    with open(i.file_path, "w+", encoding="utf-8") as originF:
                        originF.write(file_content)
                        originF.close()
                    os.system("dart format {0}".format(i.file_path))

    # 检查是否更新 i18n.json 文件
    def __check_need_update_json(self, tdfIntlDir, targetModule):
        Print.title("检查是否更新 i18n.json 文件")
        result = TranslateLint().get_lint_module_result(targetModule)
        if len(result.intl_strs) > 0 or len(result.un_intls) > 0:
            un_intls = result.intl_strs
            for i in result.un_intls:
                un_intls += i.un_intl_strs
            un_intls = list(set(un_intls))
            # 找出 un_intls 和 result.intl_json 不同的元素
            un_intls = list(set(un_intls) ^ set(result.intl_json))
            if len(un_intls) <= 0:
                return
            Print.line()
            Print.str(un_intls)
            Print.line()
            input_str = input("检查到有以上国际化字符串没加入到 i18n.json，是否自动加入？(Y 为确认)：")
            if input_str == "Y" or input_str == "y":
                read_file = open(tdfIntlDir + "/i18n.json", "r", encoding="utf-8")
                json_str: str = read_file.read()
                json_data: dict = json.loads(json_str)
                read_file.close()
                with open(tdfIntlDir + "/i18n.json", "w+", encoding="utf-8") as originF:
                    for i in un_intls:
                        i = eval(repr(i).replace("\\\\", "\\"))
                        if not i in json_data.keys():
                            json_data[i] = i
                    json_str = json.dumps(
                        json_data, ensure_ascii=False, indent=4, sort_keys=True
                    )
                    originF.write(json_str)
                    originF.close()
                Print.title("i18n.json 更新成功")

    # 通过 i18n.json 生成各个翻译后的 dart 文件
    def __generate_translate_dart_file(self, tdfIntlDir: str, targetModule: str):
        Print.title("开始通过 i18n.json 生成各个翻译后的 dart 文件")
        with open(tdfIntlDir + "/i18n.json", "r", encoding="utf-8") as originF:
            json_str = originF.read()
            json_data = json.loads(json_str)

            # 遍历i18n目录下的四个存放语言的dart文件
            for targetFileNameSuffix in self.__i18nList:
                os.chdir(tdfIntlDir + "/i18n")
                Print.line()
                targetFileName = (
                    targetModule
                    + "_"
                    + targetFileNameSuffix.replace("-", "_")
                    + ".dart"
                )

                paramsJson = self.__getTargetFileParamsJson(
                    targetFileName, targetFileNameSuffix.replace("-", "") + "Map"
                )

                os.chdir(tdfIntlDir + "/i18n")

                for item in json_data:
                    if len(paramsJson) > 0 and item in paramsJson:
                        continue
                    if targetFileNameSuffix.find("zh-ch") != -1:
                        paramsJson[r"{0}".format(item)] = r"{0}".format(json_data[item])
                    elif targetFileNameSuffix.find("zh-tw") != -1:
                        paramsJson[r"{0}".format(item)] = r"{0}".format(
                            self.__tdf_translate(json_data[item], targetFileNameSuffix)
                        )
                with open(targetFileName, "a", encoding="utf-8") as targetFile:
                    targetFile.seek(0)  # 定位
                    targetFile.truncate()  # 清空文件
                    targetFile.write(
                        r"Map<String, String> {0}Map = {1};".format(
                            targetFileNameSuffix.replace("-", ""),
                            json.dumps(paramsJson, ensure_ascii=False, sort_keys=True),
                        )
                    )
                os.system("dart format {0}".format(targetFileName))

            originF.close()
            self.__generateManagerClass(targetModule)

    def __generateManagerClass(self, moduleName):
        Print.str("生成" + moduleName + "_i18n.dart" + " 文件")
        # 生成manager类
        ShellDir.goInModuleIntlDir(moduleName)

        with open(moduleName + "_i18n.dart", "w+", encoding="utf-8") as managerF:
            managerF.truncate()
            managerF.write(
                """
import 'package:{0}/tdf_intl/i18n/{0}_th.dart';
import 'package:{0}/tdf_intl/i18n/{0}_en.dart';
import 'package:{0}/tdf_intl/i18n/{0}_zh_ch.dart';
import 'package:{0}/tdf_intl/i18n/{0}_zh_tw.dart';
// ignore: implementation_imports
import 'package:tdf_base_utils/src/data/language_data.dart';

class {1}I18n {{

static Map<String, Map<String, String>>? i18nMap;
static Map<String, Map<String, String>> getInstance() {{
    if (i18nMap == null) {{
    i18nMap = Map();
    i18nMap!["zh-ch"] = zhchMap;
    i18nMap!["zh-tw"] = zhtwMap;
    i18nMap!["en"] = enMap;
    i18nMap!["th"] = thMap;
    }}
    return i18nMap!;
}}
}}

extension {1}IntlStringExtension on String {{
    String get intl => {1}I18n.getInstance()[TDFLanguage.getLanguage()]?[this] ??
        {1}I18n.getInstance()[TDFLanguage.getDefaultLanguage()]
        ?[this] ??
        this;
}}

    """.format(
                    moduleName, self.__getManagerClassName(moduleName)
                )
            )

    def __getManagerClassName(self, moduleName):
        strList = moduleName.split("_")
        result = ""
        for item in strList:
            result = result + item.capitalize()
        return result

    def __getTargetFileParamsJson(self, targetFileName, mapName):
        with open(targetFileName, "r", encoding="utf-8") as readF:
            try:
                Print.str("解析{0}文件内json数据".format(targetFileName))
                fileData = readF.read()
                fileJsonData = self.__correctJsonData(fileData, mapName)
                jsonData = json.loads(fileJsonData, strict=False)
                readF.close()
                return jsonData
            except Exception as e:
                readF.close()
                Print.str(e)
                exit(-1)

    def __correctJsonData(self, content, mapName):
        return (
            str(content.replace("Map<String, String> {0} =".format(mapName), ""))
            .replace("\n", "")
            .strip(",};")
            .__add__("}")
        )

    def __tdf_translate(self, content, dest_lan):
        try:
            translator = Translator()
            text = translator.translate(content, src="zh-cn", dest=dest_lan).text
            return text
        except ValueError:
            Print.str("{0} 翻译失败".format(content))
            return ""
