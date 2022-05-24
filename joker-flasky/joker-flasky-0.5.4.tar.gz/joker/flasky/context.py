#!/usr/bin/env python3
# coding: utf-8

import os
import random

import yaml


class Rumor:
    __slots__ = ['attributes']

    def __init__(self, **attributes):
        self.attributes = attributes

    def __str__(self):
        return str(random.randrange(10000))

    def __getattr__(self, item):
        try:
            return self.attributes[item]
        except KeyError:
            return random.randrange(10000)


def load_contextmap(path):
    dir_ = os.path.split(path)[0]
    ctxmap = yaml.safe_load(open(path))
    extra = {}
    for key, val in ctxmap.items():
        if not isinstance(val, str):
            continue
        if val.endswith('.yml') or val.endswith('.yaml'):
            name, ext = val.rsplit('.', maxsplit=1)
            fn = (name or key) + '.' + ext
            p = os.path.join(dir_, fn)
            extra[key] = yaml.safe_load(open(p))
    ctxmap.update(extra)
    return ctxmap
