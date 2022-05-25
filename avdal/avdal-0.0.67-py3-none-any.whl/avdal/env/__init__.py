import os
import re
from typing import List
from collections.abc import Mapping, MutableMapping

_envre = re.compile(r'''^(?:export\s*)?([_a-zA-Z][\w_]*)\s*=\s*(.*)$''')
_varexp = re.compile(r'''\{\{(.*?)\}\}''')
_varname = re.compile(r'''^\s*([\w_]+)\s*$''')
_include_re = re.compile(r'''^#include\s+(.*)\s*$''')


def _cast_bool(value):
    try:
        if int(value) == 1:
            return True
        return False
    except:
        pass

    if value.lower() in ["true", "yes", "on"]:
        return True
    elif value.lower() in ["false", "no", "off"]:
        return False

    raise ValueError("Invalid boolean value: {}".format(value))


class Environment(MutableMapping):
    def __init__(self, data: Mapping, prefix=None):
        self._data = dict(data)
        self.prefix = prefix
        self.prefixf = lambda x: x if not prefix else f"{prefix}_{x}"

    def _expand(self, value):
        if type(value) is not str:
            return value

        for var in _varexp.findall(value):
            match = _varname.match(var)
            if not match:
                raise Exception(f"[{var}]: invalid variable name")

            varname = match.group(1)
            if varname not in self:
                raise Exception(f"[{varname}]: unbounded variable")

            value = value.replace(f"{{{{{var}}}}}", self[varname])

        return value

    def union(self, other: Mapping):
        return Environment({**self, **other}, prefix=self.prefix)

    def get(self, key: str, default=None, nullable=False, mapper=None):
        if not mapper:
            def mapper(x): return x

        if mapper is bool:
            mapper = _cast_bool

        value = super().get(self.prefixf(key)) or self._data.get(key)

        if value is not None:
            return mapper(value)

        if default is None and not nullable:
            raise Exception(f"{key} not found. Declare it as environment variable or provide a default value.")

        return mapper(default)

    def __call__(self, key: str, default=None, nullable=False, cast=lambda x: x):
        return self.get(key, default, nullable, cast)

    def __setitem__(self, key, value):
        self._data[key] = self._expand(value)

    def __getitem__(self, key):
        return self._data[key]

    def __delitem__(self, key):
        del self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __repr__(self) -> str:
        return "{}({{{}}})".format(type(self).__name__, ', '.join(
            ('{!r}: {!r}'.format(key, value)
             for key, value in self._data.items())))


class DotEnv(Environment):
    def _load_env(self, env_file: str):
        env_file = os.path.abspath(env_file)

        if env_file in self.envs:
            return

        self.envs.add(env_file)

        if not os.path.isfile(env_file):
            return

        with open(env_file, "r") as f:
            for line in f.readlines():
                match = _include_re.match(line)
                if match is not None:
                    file = match.group(1).strip()
                    self._load_env(file)

                match = _envre.match(line)
                if match is not None:
                    key = match.group(1)
                    value = match.group(2).strip('"').strip("'")

                    self[key] = value

        return vars

    def __init__(self, *env_files, **kwargs):
        super(DotEnv, self).__init__({}, **kwargs)
        self.envs = set()

        for file in env_files:
            self._load_env(file)


def enrich_environ(*env_files, **kwargs):
    if len(env_files) == 0:
        env_files = [".env"]

    for key, value in DotEnv(*env_files, **kwargs).items():
        if key not in os.environ:
            os.environ[key] = value
