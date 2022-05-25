#!/usr/bin/env python3
# coding: utf-8

import re
import json

from bson.json_util import loads
import datetime


def fix_mongoshell_json(s: str):
    # https://stackoverflow.com/a/11886476/2925169
    s = re.sub(
        r':\s*ObjectId\s*\(\s*\"(\S+)\"\s*\)',
        r': {"$oid": "\1"}', s
    )
    s = re.sub(
        r':\s*ISODate\s*\(\s*(\S+)\s*\)',
        r': {"$date": \1}', s
    )
    return s


def loads_mongoshell_json(s: str):
    return loads(fix_mongoshell_json(s))


def inplace_fix_mongoshell_jsonfile(path: str) -> bool:
    now = datetime.datetime.now()
    raw = open(path).read()
    fixed = fix_mongoshell_json(raw)
    if raw == fixed:
        return False
    try:
        json.loads(fixed)
    except json.JSONDecodeError:
        return False
    with open(path + f'.{now:%Y%m%d-%H%M%S}.bak', 'w') as fout:
        fout.write(raw)
    with open(path, 'w') as fout:
        fout.write(fixed)
    return True


def main():
    import sys
    inplace_fix_mongoshell_jsonfile(sys.argv[1])


if __name__ == '__main__':
    main()
