import sys
from tdf_tools.pipelines.module import Module
from tdf_tools.pipelines.translate import Translate
from tdf_tools.pipelines.router import Router
from tdf_tools.pipelines.package import Package

from tdf_tools.pipelines.git import Git
from tdf_tools.pipelines.upgrade import Upgrade


class Pipeline:
    """
    二维火 Flutter 脚手架工具，包含项目构建，依赖分析，git等功能。。
    """

    def __init__(self):
        self.module = Module()
        self.translate = Translate()
        self.package = Package()
        self.router = Router()

    def upgrade(self):
        """
        tdf_tools upgrade：升级插件到最新版本
        """
        Upgrade().run()

    def git(self, *kwargs, **kwargs1):
        """
        tdf_tools git【git 命令】：批量操作 git 命令, 例如 tdf_tools git push
        """
        Git(sys.argv[2:]).run()
