import subprocess
import os
from tdf_tools.tools.print import Print


class Cmd:
    def run(args, shell=True):
        subprocess_result = subprocess.Popen(args, shell=shell, stdout=subprocess.PIPE)
        subprocess_return = subprocess_result.stdout.read()
        return subprocess_return.decode("utf-8")

    def runAndPrint(args, shell=True) -> str:
        result = Cmd.run(args, shell=shell)
        Print.str(result)
        return result

    def system(cmd) -> int:
        return os.system(cmd)
