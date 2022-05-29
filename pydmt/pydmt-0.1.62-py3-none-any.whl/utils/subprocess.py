import subprocess
from typing import List

from pydmt.configs import ConfigOutput


def check_call(args: List[str]):
    if ConfigOutput.verbose:
        subprocess.check_call(args)
    else:
        subprocess.check_call(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
