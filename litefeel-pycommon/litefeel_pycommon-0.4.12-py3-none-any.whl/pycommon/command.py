import shlex
import subprocess
import sys
from tkinter.messagebox import RETRY
from typing import Iterable


def call_binary(cmd: str) -> tuple[bytes, bool]:
    if sys.platform == "win32":
        args = cmd
    else:
        # linux must split arguments
        args = shlex.split(cmd)
    try:
        data = subprocess.check_output(args)
        return data, True
    except subprocess.CalledProcessError as callerr:
        print(f"cmd = {cmd}, callerr.output = {callerr.output}", file=sys.stderr)
        return b"", False
    except IOError as ioerr:
        print(f"cmd = {cmd}, ioerr = {ioerr}", file=sys.stderr)
        return b"", False


# return (output, isOk)
def call(
    cmd: str, printOutput: bool = False, encoding: None | str | Iterable[str] = None
) -> tuple[str, bool]:
    data, isOk = call_binary(cmd)
    if not isOk:
        return "", False

    if encoding is None:
        encoding = "utf-8"
    isOk = False
    output = ""
    itor = (encoding,) if isinstance(encoding, str) else encoding
    for enc in itor:
        try:
            output = data.decode(enc)
            isOk = True
            break
        except UnicodeDecodeError:
            pass
    if isOk and printOutput:
        print(output)
    return output, isOk
