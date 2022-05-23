

import os
from tdf_tools.tools.config.initial_json_config import InitialJsonConfig
from tdf_tools.tools.shell_dir import ShellDir


class VsCodeManager(object):
    def openFlutterProject(self):
        ShellDir.goInShellDir()
        os.chdir(os.path.abspath(r".."))

        config = InitialJsonConfig()
        shellName = config.shellName
        os.system('code -n')
        os.system('code -a .tdf_flutter -a {0}'.format(shellName))
