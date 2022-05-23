import sys
from typing import IO, Any

from colorama import Style, init

_isInited = False

if not _isInited:
    _isInited = True
    init()


def printx(*values: Any, sep: str = ' ', end: str = '\n', file: IO[str] = sys.stdout, flush: bool = False, colorList: list[Any] | None):
    '''color 数组参数 colorama.Fore / colorama.Back / colorama.Style 的常量'''
    if colorList:
        set(*colorList)
    print(*values, sep=sep, end=end, file=file, flush=flush)
    clear()


def getStr(value: Any, *colorList: Any):
    if colorList:
        value = ''.join(colorList) + str(value) + Style.RESET_ALL
    return value


def set(*colorList: Any):
    content = ''.join(colorList)
    if content:
        sys.stdout.write(content)
        sys.stderr.write(content)


def clear():
    sys.stdout.write(Style.RESET_ALL)
    sys.stderr.write(Style.RESET_ALL)
