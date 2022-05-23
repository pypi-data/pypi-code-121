import re


def strcompile(exp):
    if isinstance(exp, str):
        return re.compile(exp)
    if isinstance(exp, re.Pattern):
        return exp


def extgroup(exp, target, asdict=False):
    regex = strcompile(exp)
    if g := regex.search(target):
        if asdict:
            return g.groupdict()
        return g.group
    # raise ValueError(f"{exp} not matched on {target}")

