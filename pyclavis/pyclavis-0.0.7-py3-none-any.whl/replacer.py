import os
import re
from collections import ChainMap


def split_col(s):
    p = s.find(":")
    if p >= 0:
        return s[:p], s[p + 1 :]
    return [s]


def replace_str(text_str, val_dicts):

    cm = ChainMap(*val_dicts)

    pattern = r"{([^}]*)}"

    regex = re.compile(pattern)

    matches = list(regex.finditer(text_str))

    found_keys = {}
    found_defaults = {}

    for m in matches:
        val = m.groups()[-1]
        keydefval = split_col(val)

        found_keys[keydefval[0]] = val
        if len(keydefval) > 1:
            found_defaults[keydefval[0]] = keydefval[1]

    for key, replpatrn in found_keys.items():

        defval = found_defaults[key] if key in found_defaults else "{" + key + "}"
        realval = cm.get(key, defval)

        text_str = text_str.replace("{" + replpatrn + "}", realval)

    return text_str
