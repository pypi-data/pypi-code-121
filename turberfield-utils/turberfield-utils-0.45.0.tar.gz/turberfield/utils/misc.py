#!/usr/bin/env python3
#   encoding: UTF-8

# This file is part of turberfield.
#
# Turberfield is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Turberfield is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with turberfield.  If not, see <http://www.gnu.org/licenses/>.

from collections import defaultdict
import configparser
import json
import logging
import logging.handlers
import pathlib

import pkg_resources

_recordFactory = logging.getLogRecordFactory()


class SavesAsDict:

    @classmethod
    def from_json(cls, data):
        return cls(**json.loads(data))

    def __json__(self):
        return json.dumps(vars(self), indent=0, ensure_ascii=False, sort_keys=False)

class SavesAsList:

    @classmethod
    def from_json(cls, data):
        return cls(json.loads(data))

    def __json__(self):
        return json.dumps(self, indent=0, ensure_ascii=False, sort_keys=False)

def config_parser(*sections, **defaults):
    rv = configparser.ConfigParser(
        defaults=defaults,
        allow_no_value=True,
        interpolation=configparser.ExtendedInterpolation(),
        converters={"path": pathlib.Path}
    )

    if sections:
        rv.read_string("\n".join(sections))
    return rv

def clone_config_section(cfg, name, guid, **kwargs):
    yield ""
    yield "[{0}]".format(guid)

    if name in cfg.sections():
        defaultKeys = set(cfg[cfg.default_section].keys())
        keys = (i for i in cfg[name] if i not in defaultKeys)
        yield from (
            "{key} = ${{{name}:{key}}}".format(name=name, key=key)
            for key in keys
        )

    yield from (
        "{key} = {val}".format(key=key, val=val)
        for key, val in kwargs.items()
    )

def reference_config_section(cfg, name, *args, **kwargs):
    if name in cfg.sections():
        yield from (
            "{key} = ${{{name}:{val}}}".format(key=key, name=name, val=val)
            for key, val in kwargs.items()
        )

def group_by_type(items):
    rv = defaultdict(list)
    for i in items:
        rv[type(i)].append(i)
    return rv

def gather_installed(key, log=None):
    for i in pkg_resources.iter_entry_points(key):
        try:
            ep = i.resolve()
        except Exception as e:
            if log is not None:
                log.warning(getattr(e, "args", e) or e)
        else:
            yield (i.name, ep)

def log_setup(args, name="turberfield", loop=None):
    log = logging.getLogger(name)

    log.setLevel(int(args.log_level))
    logging.getLogger("asyncio").setLevel(int(args.log_level))

    formatter = logging.Formatter(
        "{asctime}|{levelname:>8}|{name}| {message}",
        style="{",
    )
    ch = logging.StreamHandler()

    if args.log_path is None:
        ch.setLevel(int(args.log_level))
    else:
        fh = logging.handlers.WatchedFileHandler(args.log_path)
        fh.setLevel(int(args.log_level))
        fh.setFormatter(formatter)
        log.addHandler(fh)
        ch.setLevel(logging.WARNING)

    if loop is not None and args.log_level == logging.DEBUG:
        try:
            loop.set_debug(True)
        except AttributeError:
            log.info("Upgrade to Python 3.4.2 for asyncio debug mode")
        else:
            log.info("Event loop debug mode is {}".format(loop.get_debug()))
    ch.setFormatter(formatter)
    log.addHandler(ch)
    return name

class ConfiguredSettings:

    config_parser = staticmethod(config_parser)
    clone_config_section = staticmethod(clone_config_section)
    reference_config_section = staticmethod(reference_config_section)

    @classmethod
    def check_config(cls, cfg):
        """Check the consistency of a mapping object. """
        return cfg

    def __init__(self, *args, **kwargs):
        self.settings = self.check_config(kwargs.pop("cfg"))
        super().__init__(*args, **kwargs)

class Singleton:

    @classmethod
    def instance(cls):
        return getattr(cls, "_instance", None)

    def __new__(cls, *args, **kwargs):
        if cls.instance() is None:
            cls._instance = super().__new__(cls)
        return cls.instance()
