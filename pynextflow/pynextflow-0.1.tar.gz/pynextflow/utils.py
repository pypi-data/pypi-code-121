import re
from typing import List
import pickle as pckle


def _indent(value: str, tabs: int) -> str:
    return "\n".join(["    " * (0 if i == 0 else tabs) + str(v) for i, v in enumerate(str(value).split('\n'))])


def _strip_indent(s: str) -> str:
    pattern = re.compile(r'^[ \t]*(?=\S)', re.MULTILINE)
    indent = min(len(spaces) for spaces in pattern.findall(s))

    if not indent:
        return s

    return re.sub(re.compile(r'^[ \t]{%s}' % indent, re.MULTILINE), '', s).strip()


def _join_lines(lines: List[str], indent: int = 0) -> str:
    return "\n".join([f"{'    ' * (0 if i == 0 else indent)}{v}" for i, v in enumerate(lines)])


def pickle(obj, filename):
    with open(filename, "wb") as fd:
        pckle.dump(obj, fd)


def unpickle(filename):
    with open(filename, "rb") as fd:
        return pckle.load(fd)
