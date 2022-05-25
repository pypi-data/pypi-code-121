# -*- coding: utf-8 -*-
"""
解析ctl文件

@Time    : 2021/2/9 9:53
@Author  : modabao
"""

from typing import Callable, Dict

import numpy as np
import pandas as pd


class CTL(object):
    def __init__(self, ctl_path):
        self.path = ctl_path
        self.dset = None
        self.title = None
        self.options = None
        self.undef = None
        self.pdef = None
        self.xdef = None
        self.ydef = None
        self.zdef = None
        self.tdef = None
        self.vars = None
        self.attribute_metadata = []
        self.parse()

    def parse(self):
        works: Dict[str, Callable[[list[str], int], int]] = {
            'dset': self.parse_dset,
            'title': self.parse_title,
            'options': self.parse_options,
            'undef': self.parse_undef,
            'pdef': self.parse_pdef,
            'xdef': self.parse_xzdef,
            'ydef': self.parse_ydef,
            'zdef': self.parse_xzdef,
            'tdef': self.parse_tdef,
            'vars': self.parse_vars,
            '@': self.parse_attribute_metadata
        }
        with open(self.path) as f:
            lines: list[str] = f.readlines()
        lines_total = len(lines)
        n = -1
        while (n := n + 1) < lines_total:
            line: str = lines[n]
            # if this line (is empty) or (starts with '*'), skip
            if (not line) or line.startswith('*'):
                continue
            name = line.split()[0].lower()
            n = works[name](lines, n)
        self.attribute_metadata = pd.DataFrame(
            self.attribute_metadata, columns=['varname', 'attribute_type', 'attribute_name', 'attribute_value']
        )

    def parse_dset(self, lines, n):
        line = lines[n]
        self.dset = line[5:].strip()
        return n

    def parse_options(self, lines, n):
        line = lines[n]
        self.options = line[8:].split()
        return n

    def parse_undef(self, lines, n):
        line = lines[n]
        self.undef = float(line[6:])
        return n

    def parse_title(self, lines, n):
        line = lines[n]
        self.title = line[6:].strip()
        return n

    def parse_pdef(self, lines, n):
        line = lines[n]
        words = line[5:].split()
        if (proj := words[2]) == 'lcc':
            isize, jsize = int(words[0]), int(words[1])
            latref, lonref, iref, jref, Struelat, Ntruelat, slon, dx, dy = [float(_) for _ in words[3:]]
            pdef = {
                'proj': proj,
                'isize': isize,
                'jsize': jsize,
                'latref': latref,
                'lonref': lonref,
                'iref': iref,
                'jref': jref,
                'Struelat': Struelat,
                'Ntruelat': Ntruelat,
                'slon': slon,
                'dx': dx,
                'dy': dy
            }
        else:
            raise Exception(f'{proj} of pdef is not yet supported')
        self.pdef = pdef
        return n

    def parse_xzdef(self, lines, n):
        words = lines[n].lower().split()
        name = words[0][0]
        mapping = words[2]
        if mapping == 'linear':
            xzdef = parse_xyzdef_linear(words[1:])
        else:  # mapping == 'levels'
            xzdef, n = parse_xyzdef_levels(lines, n)
        self.__dict__[name + 'def'] = xzdef
        return n

    def parse_ydef(self, lines, n):
        words = lines[n].split()[1:]
        mapping = words[1]
        if mapping == 'linear':
            ydef = parse_xyzdef_linear(words)
        elif mapping == 'levels':
            ydef, n = parse_xyzdef_levels(lines, n)
        else:
            raise Exception(f'{mapping} of ydef is not yet supported')
        self.ydef = ydef
        return n

    def parse_tdef(self, lines, n):
        words = lines[n][5:].lower().split()
        assert words[1] == 'linear'
        tdef = {
            'num': int(words[0]),
            'start': words[2],
            'increment': words[3]
        }
        self.tdef = tdef
        return n

    def parse_vars(self, lines, n):
        varnum = int(lines[n][5:])
        n = n + 1
        vars_ = [line.rstrip().split(maxsplit=3) for line in lines[n: n + varnum]]
        vars_ = pd.DataFrame(vars_, columns=['varname', 'levs', 'units', 'description'])
        vars_['levs'] = vars_['levs'].astype(int)
        vars_ = vars_.set_index('varname')
        n = n + varnum
        assert lines[n].lower().startswith('endvar')
        self.vars = vars_
        return n

    def parse_attribute_metadata(self, lines, n):
        self.attribute_metadata.append(lines[n][1:].split(maxsplit=3))
        return n


def parse_xyzdef_linear(words):
    xyzdef = {
        'num': int(words[0]),
        'mapping': 'linear',
        'start': float(words[2]),
        'increment': float(words[3])
    }
    return xyzdef


def parse_xyzdef_levels(lines, n):
    words = lines[n][5:].split()
    num = int(words[0])
    values = words[2:]
    while len(values) < num:
        values.extend(lines[(n := n + 1)].split())
    xyzdef = {
        'num': num,
        'mapping': 'levels',
        'values': np.fromiter(values, dtype=np.float32)
    }
    return xyzdef, n
