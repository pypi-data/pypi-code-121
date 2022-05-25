# -*- coding: utf-8 -*-
# <Lettuce - Behaviour Driven Development for python>
# Copyright (C) <2010-2012>  Gabriel Falcão <gabriel@nacaolivre.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
import time
import unicodedata

# py3: mod
import six

def utf8_string(s):
    if six.PY2:
        if isinstance(s, str):
            s = s.decode("utf-8")
    if six.PY3:
        if isinstance(s, bytes):
            s = s.decode('utf-8')
    return s


def escape_if_necessary(what):
    # py3: mod
    if six.PY2:
        what = unicode(what)
    if six.PY3:
        if isinstance(what, bytes):
            what = what.decode('utf-8')
    if len(what) is 1:
        what = u"[%s]" % what

    return what


def get_stripped_lines(string, ignore_lines_starting_with=''):
    """Split lines at newline char, then return the array of stripped lines"""
    # used e.g. to separate out all the steps in a scenario
    # py3: mod
    if six.PY2:
        string = unicode(string)
        lines = [unicode(l.strip()) for l in string.splitlines()]
    if six.PY3:
        if isinstance(string, bytes):
            string = string.decode('utf-8')
        lines = [l.strip() for l in string.splitlines()]
    if ignore_lines_starting_with:
        filter_func = lambda x: x and not x.startswith(
            ignore_lines_starting_with)
    else:
        # by using an "identity" filter function, blank lines
        # will not be included in the returned list
        filter_func = lambda x: x
    # py3: mod
    lines = list(filter(filter_func, lines))

    return lines


def split_wisely(string, sep, strip=False):
    if six.PY2:
        string = unicode(string)
    if six.PY3:
        if isinstance(string, bytes):
            string = string.decode('utf-8')
    if strip:
        string = string.strip()
    else:
        string = string.strip("\n")


    # py3: mod
    if six.PY2:
        sep = unicode(sep)
    if six.PY3:
        if isinstance(sep, bytes):
            sep = sep.decode('utf-8')

    regex = re.compile(escape_if_necessary(sep),  re.UNICODE | re.M | re.I)

    items = filter(lambda x: x, regex.split(string))
    if strip:
        items = [i.strip() for i in items]
    else:
        items = [i.strip("\n") for i in items]

    if six.PY2:
        return [unicode(i) for i in items]
    if six.PY3:
        return [i if isinstance(i, str) else i.decode('utf-8') for i in items]




def wise_startswith(string, seed):
    if six.PY2:
        string = unicode(string).strip()
        seed = unicode(seed)
    if six.PY3:
        if isinstance(string, bytes):
            string = string.decode('utf-8')
        string = string.strip()
    if six.PY3:
        if isinstance(seed, bytes):
            seed = seed.decode('utf-8')
    regex = six.u("^%s") % re.escape(seed)
    return bool(re.search(regex, string, re.I))


def remove_it(string, what):
    if six.PY2:
        return unicode(re.sub(unicode(what), "", unicode(string)).strip())
    if six.PY3:
        if isinstance(string, bytes):
            string = string.decode('utf-8')
        if isinstance(what, bytes):
            what = what.decode('utf-8')
        rs = re.sub(what, "", string).strip()
        if isinstance(rs, bytes):
            rs = rs.decode('utf-8')
        return rs

def column_width(string):
    l = 0
    if six.PY2:
        rs = unicode(string)
    if six.PY3:
        if isinstance(string, bytes):
            rs = string.decode('utf-8')
        else:
            rs = string
    if isinstance(rs, int):
        rs = str(rs)
    for c in rs:
        if unicodedata.east_asian_width(c) in "WF":
            l += 2
        else:
            l += 1
    return l


def rfill(string, times, char=u" ", append=u""):
    if six.PY2:
        string = unicode(string)
    if six.PY3:
        if isinstance(string, bytes):
            string = string.decode('utf-8')
    if isinstance(string, int):
        string = str(string)
    missing = times - column_width(string)
    for x in range(missing):
        string += char
    if six.PY2:
        return unicode(string) + unicode(append)
    if six.PY3:
        if isinstance(string, bytes):
            string = string.decode('utf-8')
        if isinstance(append, bytes):
            append = append.decode('utf-8')
        return string + append


def getlen(string):
    if six.PY2:
        return column_width(unicode(string)) + 1
    if six.PY3:
        if isinstance(string, bytes):
            string = string.decode('utf-8')
        return column_width(string) + 1


def dicts_to_string(dicts, order):
    '''
    Makes dictionary ready for comparison to strings
    '''

    if six.PY2:
        escape = "#{%s}" % unicode(time.time())
    if six.PY3:
        escape = "#{%s}" % str(time.time())

    def enline(line):
        if six.PY2:
            return unicode(line).replace("|", escape)
        if six.PY3:
            if isinstance(line, bytes):
                line = line.decode('utf-8')
            return line.replace("|", escape)

    def deline(line):
        return line.replace(escape, '\\|')

    keys_and_sizes = dict([(k, getlen(k)) for k in dicts[0].keys()])
    for key in keys_and_sizes:
        for data in dicts:
            current_size = keys_and_sizes[key]
            if six.PY2:
                value = unicode(data.get(key, ''))

            if six.PY3:
                value = data.get(key, '')
                if isinstance(value, bytes):
                    value = value.decode('utf-8')

            size = getlen(value)
            if size > current_size:
                keys_and_sizes[key] = size

    names = []
    for key in order:
        size = keys_and_sizes[key]
        name = u" %s" % rfill(key, size)
        names.append(enline(name))

    table = [u"|%s|" % "|".join(names)]
    for data in dicts:
        names = []
        for key in order:
            value = data.get(key, '')
            size = keys_and_sizes[key]
            names.append(enline(u" %s" % rfill(value, size)))

        table.append(u"|%s|" % "|".join(names))

    return deline(u"\n".join(table) + u"\n")


def parse_hashes(lines, json_format=None):

    if six.PY2:
        escape = "#{%s}" % unicode(time.time())
    if six.PY3:
        escape = "#{%s}" % str(time.time())
    def enline(line):
        if six.PY2:
            return unicode(line.replace("\\|", escape)).strip()
        if six.PY3:
            rs = line.replace("\\|", escape)
            if isinstance(rs, bytes):
                rs = rs.decode('utf-8')
            return rs.strip()

    def deline(line):
        return line.replace(escape, '|')

    def discard_comments(lines):
        return [line for line in lines if not line.startswith('#')]

    lines = discard_comments(lines)
    lines = list(map(enline, lines))

    keys = []
    hashes = []
    if lines:
        first_line = lines.pop(0)
        keys = split_wisely(first_line, u"|", True)
        keys = list(map(deline, keys))

        for line in lines:
            values = split_wisely(line, u"|", True)
            values = list(map(deline, values))
            hashes.append(dict(zip(keys, values)))

    return keys, hashes

def json_to_string(json_list, order):
    '''
    This is for aesthetic reasons, it will get the width of the largest column and
    rfill the rest with spaces
    '''
    if six.PY2:
        escape = "#{%s}" % unicode(time.time())
    if six.PY3:
        escape = "#{%s}" % str(time.time())

    def enline(line):
        if six.PY2:
            return unicode(line).replace("|", escape)
        if six.PY3:
            if isinstance(line, bytes):
                line = line.decode('utf-8')
            return line.replace("|", escape)

    def deline(line):
        return line.replace(escape, '\\|')

    nu_keys_and_sizes = list([[list(k.keys())[0], getlen(list(k.keys())[0])] for k in json_list])
    maxlen = 0
    for key_list in nu_keys_and_sizes:
        current_size = key_list[1]
        counter = 0
        temp_list = list(json_list[counter].values())[0]
        temp_maxlen = len(temp_list)
        if temp_maxlen > maxlen:
            maxlen = temp_maxlen
        for data in temp_list:
            if six.PY2:
                value = unicode(data)
            if six.PY3:
                if isinstance(data, bytes):
                    value = data.decode('utf-8')
                else:
                    value = data

            size = getlen(value)
            if size > current_size:
                key_list[1] = size
        counter += 1
    names = []
    idx = 0
    for key in nu_keys_and_sizes:
        size = key[1]
        name = u" %s" % rfill(key[0], size)
        names.append(enline(name))

    table = [u"|%s|" % "|".join(names)]

    for idx in six.moves.xrange(maxlen):
        names = []
        for data, key in zip(json_list, nu_keys_and_sizes):
            try:
                value = list(data.values())[0][idx]
            except IndexError:
                value = ''
            size = key[1]
            names.append(enline(u" %s" % rfill(value, size)))
        table.append(u"|%s|" % "|".join(names))

    return deline(u"\n".join(table) + u"\n")


def parse_as_json(lines):
    '''
        Parse lines into json objects
    '''
    if six.PY2:
        escape = "#{%s}" % unicode(time.time())
    if six.PY3:
        escape = "#{%s}" % str(time.time())

    def enline(line):
        if six.PY2:
            return unicode(line.replace("\\|", escape)).strip()
        if six.PY3:
            rs = line.replace("\\|", escape)
            if isinstance(rs, bytes):
                rs = rs.decode('utf-8')
            return rs.strip()

    def deline(line):
        return line.replace(escape, '|')

    def discard_comments(lines):
        return [line for line in lines if not line.startswith('#')]
    lines = discard_comments(lines)
    lines = list(map(enline, lines))
    non_unique_keys = []
    json_map = []
    if lines:
        first_line = lines.pop(0)
        non_unique_keys = split_wisely(first_line, u"|", True)
        non_unique_keys = list(map(deline, non_unique_keys))
        rng_idx = len(non_unique_keys)
        json_map = list(non_unique_keys)
        for idx in six.moves.xrange(rng_idx):
            json_map[idx] = dict([(non_unique_keys[idx], [])])
        for line in lines:
            values = split_wisely(line, u"|", True)
            values = list(map(deline, values))

            for idx in six.moves.xrange(rng_idx):
                list(json_map[idx].values())[0].append(values[idx])
    return non_unique_keys, json_map


def parse_multiline(lines):
    multilines = []
    in_multiline = False
    for line in lines:
        if line == '"""':
            in_multiline = not in_multiline
        elif in_multiline:
            if line.startswith('"'):
                line = line[1:]
            if line.endswith('"'):
                line = line[:-1]
            multilines.append(line)
    return u'\n'.join(multilines)
