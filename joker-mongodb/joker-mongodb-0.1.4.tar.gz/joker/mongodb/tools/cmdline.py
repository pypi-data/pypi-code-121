#!/usr/bin/env python3
# coding: utf-8

import argparse

from volkanic.cmdline import CommandOptionDict


def _add_hyphens(parts: list) -> list:
    if not parts:
        return parts
    key = str(parts[0])
    if not key.startswith('-'):
        prefix = '--' if len(key) > 1 else '-'
        key = prefix + key
    return [key] + parts[1:]


class CommandOptionDictMongoish(CommandOptionDict):
    @classmethod
    def _explode(cls, key, val):
        parts = super()._explode(key, val)
        parts = _add_hyphens(parts)
        if len(parts) != 2:
            return parts
        key, val = parts
        if key.startswith('--'):
            return [f'{key}={val}']


class ArgumentParserMongoish(argparse.ArgumentParser):
    def add_argument_mongoi_host(self):
        self.add_argument('-H', '--host', help='host as in MongoInterface')

    def add_arguments_host_port(self, hostname='127.0.0.1'):
        add = self.add_argument
        add('-H', '--hostname', default=hostname, help='hostname')
        add('-p', '--port', type=int, default=27017, help='port number')

    def add_argument_db_name(self):
        self.add_argument('-d', '--db-name', help='database name')

    def add_argument_coll_name(self):
        self.add_argument('-c', '--coll-name', help='collection name')
