from tdf_tools.tools.cli.project_cli import ProjectCLI
from tdf_tools.tools.config.config import CLIJsonConfig
from tdf_tools.tools.print import Print
from tdf_tools.tools.shell_dir import ShellDir
from tdf_tools.tools.vscode.vscode import VsCodeManager


class Module:
    """
    模块相关工具： tdf_tools module -h 查看详情
    """

    def __init__(self):
        self.__cli = ProjectCLI()
        self.__vscodeManager = VsCodeManager()

    def init(self):
        """
        项目初始化
        """
        ShellDir.dirInvalidate()
        self.__cli.initial()

    def deps(self):
        """
        修改initial_config.json文件后，执行该命令，更新依赖
        """
        ShellDir.dirInvalidate()
        self.__cli.cliDeps()

    def open(self):
        """
        打开vscode，同时将所有模块添加入vscode中
        """
        ShellDir.dirInvalidate()
        self.__vscodeManager.openFlutterProject()

    def module_update(self):
        """
        更新存储项目git信息的json文件
        """
        ShellDir.dirInvalidate()
        CLIJsonConfig.updateModuleConfig()
