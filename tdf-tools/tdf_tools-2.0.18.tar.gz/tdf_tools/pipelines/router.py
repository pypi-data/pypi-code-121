from hashlib import md5
from io import TextIOWrapper
import os
import shutil
import sys
from tdf_tools.tools.config.initial_json_config import InitialJsonConfig
from tdf_tools.tools.config.module_json_config import ModuleItemType, ModuleJsonConfig
from tdf_tools.tools.platform_tools import PlatformTools
from tdf_tools.tools.print import Print
from tdf_tools.tools.shell_dir import ShellDir


class PackageNode:
    def __init__(self):
        self.packageName = ""
        # 存储的路径都是相对于shellPath的路径，所以在进入前需要先执行os.chdir(shellPath)
        self.packagePath = ""
        self.isRemote = False


class RouterNode:
    def __init__(self):
        self.package = ""
        self.routerPath = ""
        self.filePath = ""
        self.note = ""
        self.pageWidget = ""
        self.isMainPage = False


class Router:
    """
    路由相关命令：tdf_tools router -h 查看详情
    """

    def __init__(self):
        self.__packagesList: list[PackageNode] = []
        # 备份壳模块路径
        self.__shellPath = ShellDir.getShellDir()
        # 文档数据
        self.__macDownDataList: list[RouterNode] = []
        # 业务入口页列表
        self.__mainPageData: list[RouterNode] = []

        self.__entryPagePath = "tdf-flutter://2dfire.com/business/entry"
        self.__entryPageNote = "flutter entry"
        self.__entryPageWidget = "TZRouterBusinessEntryPage"

    def start(self):
        """
        tdf_tools router start：会以交互式进行路由操作，对指定的模块执行路由生成和路由注册逻辑
        """
        ShellDir.dirInvalidate()
        businessModuleList = self.__router_businessModuleList()

        Print.str("检测到以下模块可执行路由脚本：")
        Print.str(businessModuleList)
        while True:
            module_name = input("请输入需要执行路由脚本的模块名(input ! 退出，all 整合所有路由文件到壳里)：")
            if module_name == "!" or module_name == "！":
                exit(0)
            elif module_name == "all":
                self.__fetch__packagesList()
                self.__integrate_shell()
                Print.title("壳模块路由整合完成")
                exit(0)
            elif module_name in businessModuleList:
                self.__generateRouter(module_name)
                self.__integrate_shell()
                Print.title(module_name + "模块路由生成完成")
                exit(0)

    def module(self, name: str):
        """
        tdf_tools router module [module_name]：对指定的模块执行路由生成和路由注册逻辑
        """
        ShellDir.dirInvalidate()
        businessModuleList = self.__router_businessModuleList()
        if name in businessModuleList:
            self.__generateRouter(name)
            self.__integrate_shell()
            Print.title(name + "模块路由生成完成")
            exit(0)
        else:
            Print.error("没找到指定模块：" + name)

    def integrate(self):
        """
        tdf_tools router integrate：对壳进行路由整合
        """
        ShellDir.dirInvalidate()
        self.__fetch__packagesList()
        self.__integrate_shell()
        Print.title("壳模块路由整合完成")
        exit(0)

    # 生成指定模块的方法
    def __generateRouter(self, targetModule):
        # 遍历壳应用.packages下的所有package,将所有tdf开头的模块都添加入packagesList中
        self.__fetch__packagesList()
        # 生成指定注解描述文件
        self.__generator_router_des(targetModule)

    # 遍历壳应用.packages下的所有package,将所有tdf开头的模块都添加入packagesList中
    def __fetch__packagesList(self):
        ShellDir.goInShellDir()
        # 遍历壳应用.packages下的所有package,将所有tdf开头的模块都添加入packagesList中
        with open(".packages") as lines:
            for line in lines:
                ShellDir.goInShellDir()
                if line.startswith("# ") is False:
                    if line.find(":file") != -1:
                        remotePackage = self.__getRemoteCodePackagePath(line)
                        if remotePackage != None:
                            self.__packagesList.append(remotePackage)
                    else:
                        sourcePackage = self.__getSourceCodePackagePath(line)
                        if sourcePackage != None:
                            self.__packagesList.append(sourcePackage)

    # 整合壳的路由文件
    def __integrate_shell(self):
        # 整合所有路由文件到壳里
        self.__integrate_all_routing_files()

        # 生成路由 初始化文件
        self.__generate_router_init_files()

        # 生成路由入口文件
        self.__generate_router_entry_files()

        # 生成路由文档
        self.__generate_router_doc()

    # 生成注解描述文件
    def __generator_router_des(self, targetModule):
        Print.title(targetModule + " 模块生成注解描述文件")
        for item in self.__packagesList:
            if item.packageName == targetModule:
                if item.isRemote == False:
                    if self.__judgeHasBuildRunnerPackage(item.packagePath):
                        ShellDir.goInShellDir()
                        os.chdir(item.packagePath)
                        self.__generatorFunc()
                    else:
                        Print.str(
                            "请确保模块{0}已依赖build_runner和tdf_router_anno两个包，可参考其他模块进行依赖配置❌".format(
                                targetModule
                            )
                        )
                else:
                    Print.str("检测到模块{0}当前是远程依赖，无法生成路由描述文件❌".format(targetModule))

    # 整合所有路由文件到壳里
    def __integrate_all_routing_files(self):
        Print.title("整合所有路由文件到壳里")
        ShellDir.goInShellDir()
        os.chdir("lib")
        if os.path.exists("tz_router"):
            shutil.rmtree(r"tz_router")
        os.mkdir("tz_router")
        os.chdir("tz_router")
        os.mkdir("group")

        for packageItem in self.__packagesList:
            # 存在路由描述文件才进行遍历
            ShellDir.goInShellDir()
            if self.__hasRouterDartFile(packageItem.packagePath):
                os.chdir(self.__shellPath + "/lib/tz_router/group/")
                os.mkdir(packageItem.packageName)
                os.chdir(packageItem.packageName)
                f = open("router_map.dart", "w+")
                self.__defaultImportCreator(f, "'package:tdf_router/tdf_router.dart';")

                ShellDir.goInShellDir()
                os.chdir(packageItem.packagePath + "/lib/")

                nowaPath = os.popen(PlatformTools.pwd_cmd()).read().split("\n")[0]

                routerAliasFileList = []
                routerFileList = []
                for root, _, files in os.walk(nowaPath):
                    for file in files:
                        src_file = os.path.join(root, file)
                        if src_file.endswith(".tdf_router.dart"):
                            itemModuleName = packageItem.packageName
                            if PlatformTools.is_windows():
                                temp = src_file.split("\lib\\")[1]
                                itemFilePath = temp.replace("\\", "/")
                            else:
                                itemFilePath = src_file.split("/lib/")[1]
                            itemFileAlias = (
                                "tdf_router_"
                                + md5(itemFilePath.encode()).hexdigest()[8:-8]
                            )

                            self.__importDataCreator(
                                f, itemModuleName, itemFilePath, itemFileAlias
                            )
                            routerAliasFileList.append(itemFileAlias)
                            routerFileList.append(src_file)
                if len(routerAliasFileList) > 0:
                    Print.stage(
                        "模块{:>30}  检测到  {:>3}  个路由".format(
                            packageItem.packageName, len(routerAliasFileList)
                        )
                    )
                    self.__groupRouterClassCreator(
                        f, packageItem.packageName, routerAliasFileList
                    )
                    if PlatformTools.is_windows():
                        self.__addInWindowDownData(routerFileList)
                    else:
                        self.__addInMacDownData(routerFileList)

                f.close()

    # 生成路由 初始化文件
    def __generate_router_init_files(self):
        Print.title("生成路由初始化文件")
        ShellDir.goInShellDir()
        os.chdir("lib/tz_router")

        initF = open("init.dart", "w+")

        # 生成初始化init文件
        if os.path.exists("group") == False:
            os.mkdir("group")
        os.chdir("group")
        nowaPath = os.popen(PlatformTools.pwd_cmd()).read().split("\n")[0]
        self.__defaultImportCreator(initF, "'package:tdf_router/tdf_router.dart';")
        # 添加flutter业务入口页面import
        self.__defaultImportCreator(initF, "'entry/tz_router_entry_page.dart';")
        mapList = []
        for root, dirs, files in os.walk(nowaPath):
            for file in files:
                src_file = os.path.join(root, file)
                if src_file.find("init.dart") != -1:
                    continue
                if PlatformTools.is_windows():
                    tmpItemFilePath = src_file.split("tz_router")[1]
                    itemFilePath = tmpItemFilePath.replace("\\", "/")
                else:
                    itemFilePath = src_file.split("tz_router")[1]
                itemFileAlias = (
                    "router_map_" + md5(itemFilePath.encode()).hexdigest()[8:-8]
                )
                importContent = 'import ".{0}" as {1};\n'.format(
                    itemFilePath, itemFileAlias
                )
                initF.write(importContent)
                mapList.append(itemFileAlias)

        initF.write(
            """

        class TZRouterManager {{
            static combineMap() {{
                Map<String, TDFPageBuilder> map = Map();
                {0}
                return map;
            }}
        }}
        """.format(
                self.__mapListCombineCreater(mapList)
            )
        )

        initF.close()

    # 生成路由入口文件
    def __generate_router_entry_files(self):
        Print.title("生成路由入口文件")
        ShellDir.goInShellDir()
        os.chdir("lib/tz_router")
        # os.chdir(shellPath + "/lib/tz_router")
        if os.path.exists("entry") == False:
            os.mkdir("entry")

        os.chdir("entry")

        file_name = "tz_router_entry_page.dart"
        entryPageF = open(file_name, "w+")

        self.__defaultImportCreator(entryPageF, "'package:flutter/material.dart';")
        self.__defaultImportCreator(entryPageF, "'package:tdf_router/tdf_router.dart';")
        self.__defaultImportCreator(
            entryPageF, "'package:tdf_router_anno/router/router_anno.dart';"
        )
        self.__defaultImportCreator(
            entryPageF, "'package:tdf_base_utils/tdf_base_utils.dart';"
        )
        self.__defaultImportCreator(
            entryPageF, "'package:tdf_widgets/tdf_common_btn/tdf_btn.dart';"
        )
        self.__defaultImportCreator(
            entryPageF, "'package:tdf_widgets/title_bar/tdf_title_bar.dart';"
        )
        entryPageF.write(
            """

@TZRouter(path: '{0}', note: '{1}')
class {2} extends StatefulWidget {{
    final Map params;

    {2}(this.params);

    @override
    _{2}State createState() => _{2}State();
}}

class _{2}State extends State<{2}> {{
    final TextEditingController routerController = new TextEditingController();
    final TextEditingController controller = new TextEditingController();
    final Map<String, String> pageMap = {{
    {3}
    }};

    @override
    Widget build(BuildContext context) {{
        TDFScreen.init(context);
        return Scaffold(
            backgroundColor: Color(0xffffffff),
            appBar: TDFTitleBar(
                titleContent: \"{4}\",
                backType: TDFTitleBackWidgetType.DEFAULT_BACK,
            ),
            body: SingleChildScrollView(
                child: Column(
                    children: _getButtonList(),
                ),
            ),
        );
    }}

    List<Widget> _getButtonList() {{
        List<Widget> list = [];
        list.add(_routerJumpWidget());
        list.add(Padding(
        padding: EdgeInsets.only(top: 20.w),
        child: TDFButton(
            content: \"根据路由跳转\",
            bgColor: 0xff0088ff,
            contentColor: 0xffffffff,
            onClick: () {{
            FocusScope.of(context).requestFocus(FocusNode());
            TDFRouter.open(routerController.text);
            }},
        ),
        ));
        list.add(_searchWidget());

        List<Widget> wrapEntrylist = [];
        pageMap.forEach((key, value) {{
        if (key.contains(controller.text)) {{
            wrapEntrylist.add(GestureDetector(
                onTap: () {{
                FocusScope.of(context).requestFocus(FocusNode());
                TDFRouter.open(value);
                }},
                child: ClipRRect(
                borderRadius: BorderRadius.all(Radius.circular(3.w)),
                child: Container(
                    color: Colors.blue,
                    padding: EdgeInsets.only(
                        left: 7.w, right: 7.w, top: 4.w, bottom: 4.w),
                    child: Text(
                    key,
                    style: TextStyle(fontSize: 13.w),
                    ),
                ),
                )));
        }}
        }});
        list.add(SizedBox(
        height: 20.w,
        ));
        list.add(Wrap(
        spacing: 15.w,
        runSpacing: 10.w,
        children: wrapEntrylist,
        ));
        return list;
    }}

    Widget _routerJumpWidget() {{
        return TextField(
        controller: routerController,
        autofocus: false,
        decoration: InputDecoration(hintText: "输入页面路由"),
        onChanged: (value) {{
            setState(() {{}});
            }},
        );
    }}

    Widget _searchWidget() {{
        return TextField(
            controller: controller,
            autofocus: false,
            decoration: InputDecoration(hintText: "筛选"),
            onChanged: (value) {{
                setState(() {{}});
            }},
        );
    }}
    
}}
        """.format(
                self.__entryPagePath,
                self.__entryPageNote,
                self.__entryPageWidget,
                self.__mainPageDataCreator(),
                self.__entryPageNote,
            )
        )
        entryPageF.close()
        os.system("dart format {0}".format(file_name))

    # 生成路由文档
    def __generate_router_doc(self):
        Print.title("生成路由文档")
        ShellDir.goInShellDir()
        if os.path.exists("路由文档") == True:
            shutil.rmtree(r"路由文档")
        os.mkdir("路由文档")
        os.chdir("路由文档")

        f = open("document.md", "w+")

        ShellDir.goInShellDir()
        # os.chdir(shellPath)
        curDir = ShellDir.getShellDir()
        for root, dirs, files in os.walk(curDir):
            for file in files:
                src_file = os.path.join(root, file)
                if src_file.find("pubspec.yaml") != -1:
                    if PlatformTools.is_windows():
                        with open("pubspec.yaml", "rb") as lines:
                            for line in lines:
                                if line.find(bytes("name: ", encoding="utf8")) != -1:
                                    f.write(
                                        "## Flutter壳应用（{0}）路由表\n".format(
                                            line.split(
                                                bytes("name: ", encoding="utf8")
                                            )[1].split(bytes("\n", encoding="utf8"))[0]
                                        )
                                    )
                                break
                    else:
                        with open("pubspec.yaml") as lines:
                            for line in lines:
                                if line.find("name: ") != -1:
                                    f.write(
                                        "## Flutter壳应用（{0}）路由表\n".format(
                                            line.split("name: ")[1].split("\n")[0]
                                        )
                                    )
                                break

        f.write(
            '<table><thead><tr><th>{0}</th><th style = "min-width:150px !important">{1}</th><th>{2}</th><th>{3}</th><th>{4}</th></tr></thead>'.format(
                "组件名", "描述", "路由path", "类名", "文件路径"
            )
        )
        f.write("<tbody>")

        currentPackage = ""
        for item in self.__macDownDataList:
            if currentPackage == item.package:
                f.write(
                    "<tr><th>{0}</th><th>{1}</th><th>{2}</th><th>{3}</th><th>{4}</th></tr>\n".format(
                        "", item.note, item.routerPath, item.pageWidget, item.filePath
                    )
                )
            else:
                currentPackage = item.package
                f.write(
                    "<tr><th>{0}</th><th>{1}</th><th>{2}</th><th>{3}</th><th>{4}</th></tr>\n".format(
                        item.package,
                        item.note,
                        item.routerPath,
                        item.pageWidget,
                        item.filePath,
                    )
                )

        f.write("</tbody></table>")

        f.close()

    # 获取远程代码路径
    def __getRemoteCodePackagePath(self, line: str) -> PackageNode:
        packageName = line.split(":file://")[0]
        packagePath = line.split(":file://")[1].replace("%25", "%")
        if packageName.find("tdf") != -1:
            packageNode = PackageNode()
            packageNode.packageName = packageName
            if PlatformTools.is_windows():
                packageNode.packagePath = packagePath[1 : len(packagePath) - 5]
            else:
                packageNode.packagePath = packagePath[0 : len(packagePath) - 5]
            packageNode.isRemote = True
            return packageNode

    def __getSourceCodePackagePath(self, line: str) -> PackageNode:
        packageName = line.split(":")[0]
        packagePath = line.split(":")[1].replace("%25", "%")
        if packageName.find("tdf") != -1:
            packageNode = PackageNode()
            packageNode.packageName = packageName
            packageNode.packagePath = packagePath[0 : len(packagePath) - 5]
            packageNode.isRemote = False
            return packageNode

    # 判断业务组件下是否有依赖必须的build_runner和tdf_router_anno两个模块
    def __judgeHasBuildRunnerPackage(self, dirPath: str) -> bool:
        hasBuildRunner = False
        hasRouterAnno = False
        os.chdir(dirPath)
        if os.path.exists(".packages"):
            with open(".packages") as lines:
                for line in lines:
                    if line.find("build_runner") != -1:
                        hasBuildRunner = True
                    if line.find("tdf_router_anno") != -1:
                        hasRouterAnno = True
        return hasBuildRunner and hasRouterAnno

    # 生成代码
    def __generatorFunc(self):
        os.system("flutter packages pub run build_runner clean")
        os.system(
            "flutter packages pub run build_runner build --delete-conflicting-outputs"
        )

    # 判断指定目录下是否存在.tdf_router.dart结尾的文件
    def __hasRouterDartFile(self, dirPath):
        os.chdir(dirPath)
        nowaPath = os.popen(PlatformTools.pwd_cmd()).read().split("\n")[0]
        for root, dirs, files in os.walk(nowaPath):
            for file in files:
                src_file = os.path.join(root, file)
                if src_file.endswith(".tdf_router.dart"):
                    return True
        return False

    def __defaultImportCreator(self, mFileWriter, content):
        mFileWriter.write("import {0}\n".format(content))

    # 生成import数据
    def __importDataCreator(
        self, mFileWriter, itemModuleName, mFilePath, itemFileAlias
    ):
        mFileWriter.write(
            'import "package:{0}/{1}" as {2};\n'.format(
                itemModuleName, mFilePath, itemFileAlias
            )
        )

    # 路由map类生成器
    def __groupRouterClassCreator(self, mFileWriter: TextIOWrapper, moduleName, list):
        content = """
    routerMap() {{
        Map<String, TDFPageBuilder> map = Map();
        {1}
        return map;
    }}
    """
        mFileWriter.write(content.format(moduleName, self.__mapAddListCreator(list)))

    def __mapAddListCreator(self, list):
        content = ""
        for item in list:
            content += """map.putIfAbsent({0}.getRouterPath(), () =>  (String pageName, Map params, String _) => {1}.getPageWidget(params));
        """.format(
                item, item
            )
        return content

    def __addInWindowDownData(self, routerFileList):
        bytesTemp = bytes("\n", encoding="utf8")
        for fileItem in routerFileList:
            result = fileItem
            if len(fileItem) > 260:
                temp = "\\\\?\\"
                temp2 = fileItem
                result = temp + fileItem
            with open(result, "rb") as lines:
                node = RouterNode()
                for line in lines:
                    if line.find(bytes(" //#package#//", encoding="utf8")) != -1:
                        node.package = line.split(
                            bytes("//#package#//", encoding="utf8")
                        )[1].split(bytesTemp)[0]
                    if line.find(bytes("//#routerPath#//", encoding="utf8")) != -1:
                        node.routerPath = line.split(
                            bytes("//#routerPath#//", encoding="utf8")
                        )[1].split(bytesTemp)[0]
                    if line.find(bytes("//#filePath#//", encoding="utf8")) != -1:
                        node.filePath = line.split(
                            bytes("//#filePath#//", encoding="utf8")
                        )[1].split(bytesTemp)[0]
                    if line.find(bytes("//#note#//", encoding="utf8")) != -1:
                        node.note = str(
                            line.split(bytes("//#note#//", encoding="utf8"))[1].split(
                                bytesTemp
                            )[0],
                            encoding="utf8",
                        )
                    if line.find(bytes("//#pageWidget#//", encoding="utf8")) != -1:
                        node.pageWidget = line.split(
                            bytes("//#pageWidget#//", encoding="utf8")
                        )[1].split(bytesTemp)[0]
                    if line.find(bytes("//#isMainPage#//", encoding="utf8")) != -1:
                        node.isMainPage = (
                            line.split(bytes("//#isMainPage#//", encoding="utf8"))[
                                1
                            ].split(bytesTemp)[0]
                            == "true"
                        )
                self.__macDownDataList.append(node)
                if node.isMainPage == True:
                    self.__mainPageData.append(node)

    def __addInMacDownData(self, routerFileList):
        for fileItem in routerFileList:
            with open(fileItem) as lines:
                node = RouterNode()
                for line in lines:
                    if line.find("//#package#//") != -1:
                        node.package = line.split("//#package#//")[1].split("\n")[0]
                    if line.find("//#routerPath#//") != -1:
                        node.routerPath = line.split("//#routerPath#//")[1].split("\n")[
                            0
                        ]
                    if line.find("//#filePath#//") != -1:
                        node.filePath = line.split("//#filePath#//")[1].split("\n")[0]
                    if line.find("//#note#//") != -1:
                        node.note = line.split("//#note#//")[1].split("\n")[0]
                    if line.find("//#pageWidget#//") != -1:
                        node.pageWidget = line.split("//#pageWidget#//")[1].split("\n")[
                            0
                        ]
                    if line.find("//#isMainPage#//") != -1:
                        node.isMainPage = (
                            line.split("//#isMainPage#//")[1].split("\n")[0] == "true"
                        )
                self.__macDownDataList.append(node)
                if node.isMainPage == True:
                    self.__mainPageData.append(node)

    def __mapListCombineCreater(self, list):
        content = ""
        for item in list:
            content += "map.addAll({0}.routerMap());\n".format(item)
        content += 'map.putIfAbsent("{0}", () => (String pageName, Map params, String _) => {1}(params));'.format(
            self.__entryPagePath, self.__entryPageWidget
        )
        return content

    def __mainPageDataCreator(self):
        content = ""
        for item in self.__mainPageData:
            if item.isMainPage:
                content += '"{0}":"{1}",\n'.format(item.note, item.routerPath)
        return content

    def __router_businessModuleList(self):
        __module_config = ModuleJsonConfig()
        businessModuleList = []
        for item in InitialJsonConfig().moduleNameList:
            cofig_item = __module_config.get_item(item)
            if (
                cofig_item.type == ModuleItemType.Lib
                or cofig_item.type == ModuleItemType.Module
            ):
                businessModuleList.append(item)
        return businessModuleList
