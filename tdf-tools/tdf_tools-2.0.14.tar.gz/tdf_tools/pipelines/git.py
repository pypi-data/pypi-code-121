from tdf_tools.tools.config.initial_json_config import InitialJsonConfig
from tdf_tools.tools.cmd import Cmd
from tdf_tools.tools.print import Print
from tdf_tools.tools.shell_dir import ShellDir


class Git:
    """
    tdf_tools git【git 命令】：批量操作 git 命令, 例如 tdf_tools git push
    """

    def __init__(self, arg: list):
        self.__arg = ["git"] + arg

    def run(self):
        ShellDir.dirInvalidate()
        self.__batch_run_git()

    def __batch_run_git(self):
        for module in InitialJsonConfig().moduleNameList:
            ShellDir.goInModuleDir(module)
            Print.title("开始操作" + module + "模块：" + " ".join(self.__arg))
            Cmd.runAndPrint(self.__arg, shell=False)
