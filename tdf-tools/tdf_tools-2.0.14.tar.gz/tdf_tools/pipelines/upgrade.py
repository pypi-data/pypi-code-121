import os
from tdf_tools.tools.print import Print


class Upgrade:
    def run(self, arg=[]):
        os.system("python3 -m pip install --upgrade tdf-tools --user")
        exit(0)
