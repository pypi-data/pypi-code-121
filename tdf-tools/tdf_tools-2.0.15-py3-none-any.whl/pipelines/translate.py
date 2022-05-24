from tdf_tools.tools.shell_dir import ShellDir
from tdf_tools.tools.translate.translate_lint import TranslateLint
from tdf_tools.tools.translate.translate_tools import TranslateTools


class Translate:
    """
    国际化相关：tdf_tools translate -h 查看详情
    """

    def __init__(self) -> None:
        self.lint = TranslateLint()

    def start(self):
        """
        国际化相关：通过交互式的方式处理国际化
        """
        ShellDir.dirInvalidate()
        TranslateTools().translate()

    def module(self, name):
        """
        国际化相关：指定模块进行国际化
        """
        ShellDir.dirInvalidate()
        TranslateTools().translate_module(name)
        exit(0)
