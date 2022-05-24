from tdf_tools.tools.dependencies_analysis import DependencyAnalysis
from tdf_tools.tools.package.seal_off_package_utils import changeVersionAndDependencies, createAndPushTag, tagInfoObj
from tdf_tools.tools.print import Print
from tdf_tools.tools.shell_dir import ShellDir


class Package:
    """
    封包工具相关：tdf_tools package -h 查看详情
    """

    def __init__(self):
        self.analysis = DependencyAnalysis()

    def map(self):
        """
        tdf_tools package map：以二维数组形式输出模块的依赖顺序，每一item列表代表可同时打tag的模块
        """
        ShellDir.dirInvalidate()
        json = self.analysis.generate()
        exit(json)

    def tagInfo(self):
        """
        tdf_tools package tagInfo：输出一个json，每一节点包含一个模块，
        内部包含：remote：远程最新版本号；
        current：模块内配置的版本号；
        upgrade：对比自增后的版本号；
        sort：模块打tag顺序，sort相同即代表可同时打tag
        """
        ShellDir.dirInvalidate()
        tagInfoObj()

    def prepareTagTask(self, jsonData: str):
        """
        tdf_tools package prepareTagTask：修改yaml中的tag号和所有的依赖，该命令可看成是做打tag前的准备工作，把依赖规范化
        """
        ShellDir.dirInvalidate()
        changeVersionAndDependencies(jsonData)

    def tag(self, modules: str):
        """
        tdf_tools package tag：批量tag操作，参数通过逗号隔开，不要有空格。如tdf_tools tag tdf_widgets
        """
        ShellDir.dirInvalidate()
        createAndPushTag(modules.split(','))
