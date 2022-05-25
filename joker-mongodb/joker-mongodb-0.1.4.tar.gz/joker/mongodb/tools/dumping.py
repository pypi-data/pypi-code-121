#!/usr/bin/env python3
# coding: utf-8


from typing import List
from joker.mongodb.tools.cmdline import CommandOptionDictMongoish

import re
from pymongo.database import Database
from joker.mongodb import utils


def find_excluding_coll_names(db: Database, regexes: List[str]) -> list:
    for coll_name in db.list_collection_names():
        ns = f'{db.name}.{coll_name}'
        for pat in regexes:
            if re.search(pat, ns):
                yield coll_name


def dump(params: dict):
    cod = CommandOptionDictMongoish(params)
    cod.executable = 'mongodump'
    cod.run(dry=True)


def smart_dump(db: Database, outpath: str, excl_regexes: List[str]):
    excl_coll_names = find_excluding_coll_names(db, excl_regexes)
    params = {
        'gzip': True, 'out': outpath, 'db': db.name,
        'excludeCollection': tuple(excl_coll_names),
    }
    cfg = utils.infer_params(db.client)
    keys = ['host', 'port', 'username', 'password']
    for key in keys:
        val = cfg.get(key)
        if val:
            params[key] = val
    return params
    # dump(params)
