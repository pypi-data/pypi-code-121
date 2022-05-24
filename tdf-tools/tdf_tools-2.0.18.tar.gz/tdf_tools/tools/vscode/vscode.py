import os
from tdf_tools.tools.config.initial_json_config import InitialJsonConfig
from tdf_tools.tools.print import Print
from tdf_tools.tools.shell_dir import ShellDir


class VsCodeManager(object):
    def openFlutterProject(self):
        tdf_flutter_path = ShellDir.getInTdfFlutterDir()
        shell_path = ShellDir.getShellDir()

        os.system("code -n")
        os.system("code -a {0} -a {1}".format(tdf_flutter_path, shell_path))
