'''
Salty Configuration, meaning that a bunch of this code is stolen from Salt :V

Copyright (c) 2015 - 2022 Rob "N3X15" Nelson <nexisentertainment@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''
import codecs
import collections
import fnmatch
import os
import sys
from typing import Any, Dict, Optional, Union

import jinja2

from buildtools.bt_logging import NullIndenter, log
from buildtools.ext.salt.jinja_ext import salty_jinja_envs
from buildtools.os_utils import ensureDirExists


def delimget(cfg, key, default=None, delim='.'):
    parts = key.split(delim)
    try:
        value = cfg[parts[0]]
        if len(parts) == 1:
            return value
        for part in parts[1:]:
            value = value[part]
        return value
    except (KeyError, TypeError):
        return default

def delimset(cfg, key, value, delim='.'):
    parts = key.split(delim)
    try:
        if len(parts) == 1:
            cfg[parts[0]] = value
            return
        if parts[0] not in cfg:
            cfg[parts[0]] = collections.OrderedDict()
        L = cfg[parts[0]]
        for part in parts[1:-1]:
            if part not in L:
                L[part] = collections.OrderedDict()
            L = L[part]
        L[parts[-1]] = value
    except (KeyError, TypeError):
        return
def delimdel(cfg, key, delim='.'):
    parts = key.split(delim)
    try:
        if len(parts) == 1:
            del cfg[parts[0]]
            return
        if parts[0] not in cfg:
            return
        L = cfg[parts[0]]
        for part in parts[1:-1]:
            if part not in L:
                return
            L = L[part]
        del L[parts[-1]]
    except (KeyError, TypeError):
        return

def flattenDict(cfg, delim='/', ppath=[], out=None):
    if out is None:
        out = collections.OrderedDict()
    for key, value in cfg.items():
        cpath = ppath + [key]
        strpath = delim.join(cpath)
        if isinstance(value, dict):
            flattenDict(value, delim, cpath, out)
        elif isinstance(value, (list, set)):
            flattenList(value, delim, cpath, out)
        else:
            out[strpath] = value
    return out


def flattenList(cfg, delim='/', ppath=[], out=None):
    if out is None:
        out = collections.OrderedDict()
    for key, value in enumerate(cfg):
        cpath = ppath + [key]
        strpath = delim.join(cpath)
        if isinstance(value, dict):
            flattenDict(value, delim, cpath, out)
        elif isinstance(value, (list, set)):
            flattenList(value, delim, cpath, out)
        else:
            out[strpath] = value
    return out

def replace_var(input, varname, replacement):
    return input.replace('%%' + varname + '%%', replacement)


def replace_vars(input, var_replacements):
    for key, val in var_replacements.items():
        input = replace_var(input, key, val)
    return input


def dict_merge(a, b, path=None):
    "merges b into a"
    if path is None:
        path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                dict_merge(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass  # same leaf value
            else:
                # Old behavior: scream
                # raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
                # New behavior: Overwrite A with B.
                a[key] = b[key]
        else:
            a[key] = b[key]
    return a


class BaseConfig(dict):
    def __init__(self):
        self.cfg: Dict[str, Any] = {}
        self.delim: str = '.'

    def __contains__(self, key) -> bool:
        parts = key.split(self.delim)
        if len(parts) == 1:
            return self.cfg.__contains__(key)
        try:
            value = self.cfg[parts[0]]
            for part in parts[1:]:
                value = value[part]
            return True
        except (KeyError, TypeError):
            return False

    def __delitem__(self, key: str) -> None:
        delimdel(self.cfg, key, self.delim)

    def __iter__(self):
        return self.cfg.__iter__()

    def __getitem__(self, key) -> Any:
        return self.cfg.__getitem__(key)

    def __setitem__(self, key, value) -> None:
        return self.cfg.__setitem__(key, value)

    def get(self, key, default=None) -> Any:
        return delimget(self.cfg, key, default, self.delim)

    def set(self, key, value) -> None:
        delimset(self.cfg, key, value, self.delim)

    def has_key(self, key: str) -> bool:
        return self.__contains__(key)

    def strict_has_key(self, key: str) -> bool:
        return self.cfg.has_key(key)


class ConfigFile(BaseConfig):
    def __init__(self, filename: str = None, default: Dict[str, Any] = {}, template_dir: str=None, variables: Dict[str, Any]={}, verbose:bool=False, encoding: str='utf-8', skip_defaults: bool = False):
        super().__init__()
        self.encoding=encoding
        self.skip_defaults = skip_defaults
        env_vars = salty_jinja_envs()
        if template_dir is not None:
            env_vars['loader'] = jinja2.loaders.FileSystemLoader(template_dir, encoding=encoding)
        self.environment = jinja2.Environment(**env_vars)
        self.filename = filename
        self.actual_filename = filename if template_dir is None else os.path.join(template_dir, filename)
        self.template_dir = template_dir
        if filename is None:
            self.cfg = default
        else:
            self.Load(filename, merge=False, defaults=default, variables=variables, verbose=verbose)

    def Load(self, filename, merge=False, defaults=None, variables={}, verbose=False):
        lh = NullIndenter()
        if self.actual_filename is None:
            self.actual_filename = filename if self.template_dir is None else os.path.join(self.template_dir, filename)
        if verbose:
            lh = log.info("Loading %s...", filename)
        with lh:
            if not self.skip_defaults and not os.path.isfile(filename):
                if defaults is None:
                    if verbose: log.error('Failed to load %s.', filename)
                    return False
                else:
                    if verbose: log.warn('File not found, loading defaults.')
                    ensureDirExists(os.path.dirname(filename))
                    self.dump_to_file(filename, defaults)

            rendered = ''
            template: jinja2.Template = None
            #print(repr(self.template_dir))
            try:
                if self.template_dir is not None:
                    template = self.environment.get_template(os.path.basename(filename) if self.template_dir is None else filename)
                else:
                    with open(filename) as f:
                        template = self.environment.from_string(f.read())
                rendered = template.render(variables)
            except jinja2.exceptions.TemplateNotFound as tnf:
                if verbose:
                    log.warn('Jinja2 failed to load %s (TemplateNotFound). Failing over to plain string.', filename)
                    log.exception(tnf)
                with codecs.open(filename, 'r', encoding=self.encoding) as f:
                    rendered = f.read()
            #print(rendered)
            newcfg = self.load_from_string(rendered)
            if merge:
                self.cfg = dict_merge(self.cfg, newcfg)
            else:
                self.cfg = newcfg
        return True

    def Save(self, filename):
        self.dump_to_file(filename, self.cfg)

    def LoadFromFolder(self, path, pattern='*.yml', variables={}, verbose=False):
        'For conf.d/ stuff.'
        for root, _, files in os.walk(path):
            for filename in files:
                absfilename = os.path.join(root, filename)
                if fnmatch.fnmatch(absfilename, pattern):
                    self.Load(absfilename, merge=True, variables=variables, verbose=verbose)
        # for filename in glob.glob(os.path.join(path,pattern)):
        #    self.Load(filename, merge=True)

    def dump_to_file(self, filename, cfg):
        pass

    def load_from_string(self, string):
        return {}


class YAMLConfig(ConfigFile):
    _YAML_INSTANCE: 'ruamel.yaml.YAML' = None

    def __init__(self, filename=None, default={}, template_dir=None, variables={}, verbose=False, ordered_dicts=False, encoding='utf-8'):
        self._ordered_dicts=False
        super().__init__(filename, default, template_dir, variables, verbose, encoding)
        self._ordered_dicts=ordered_dicts

        self._YAML_INSTANCE = None

    @property
    def yaml(self) -> 'ruamel.yaml.YAML':
        from ruamel.yaml import YAML
        from ruamel.yaml.representer import RoundTripRepresenter

        class ODRepresenter(RoundTripRepresenter):
            pass

        if self._YAML_INSTANCE is None:
            self._YAML_INSTANCE = YAML(typ='safe', pure=True)
            self._YAML_INSTANCE.representer.add_representer(collections.OrderedDict, ODRepresenter.represent_dict)
        return self._YAML_INSTANCE

    def dump_to_file(self, filename, data):
        with codecs.open(filename, 'w', encoding=self.encoding) as f:
            self.yaml.dump(data, f)

    def load_from_string(self, string):
        return self.yaml.load(string)

class TOMLConfig(ConfigFile):

    def __init__(self, filename=None, default={}, template_dir='.', variables={}, verbose=False, encoding='utf-8'):
        super(TOMLConfig, self).__init__(filename, default, template_dir, variables, verbose, encoding)

    def dump_to_file(self, filename, data):
        import toml
        with open(filename, 'w', encoding=self.encoding) as f:
            f.write(toml.dumps(data))

    def load_from_string(self, string):
        import toml
        return toml.loads(string)


class Properties(object):
    def __init__(self):
        self.properties = {}

    def Load(self, filename, default=None, expand_vars={}):
        with log.info("Loading %s...", filename):
            if not os.path.isfile(filename):
                if default is None:
                    log.critical('File not found, exiting!')
                    log.info('To load defaults, specify default=<dict> to Properties.Load().')
                    sys.exit(1)
                else:
                    log.warn('File not found, loading defaults.')
                    with open(filename, 'w') as f:
                        self.dumpTo(default, f)

            with open(filename, 'r') as f:
                for line in f:
                    if line.strip() == '':
                        continue
                    # Ignore comments.
                    if line.strip().startswith('#'):
                        continue

                    key, value = line.strip().split('=', 1)
                    if key in self.properties:
                        log.warn('Key "%s" already exists, overwriting!', key)
                    value = replace_vars(value, expand_vars)
                    self.properties[key] = value

            if default is None:
                return
            for k, v in default.items():
                if k not in self.properties:
                    self.properties[k] = v
                    log.info('Added default property %s = %s', k, v)

    def Save(self, filename):
        with log.info("Saving %s...", filename):
            with open(filename, 'w') as f:
                Properties.dumpTo(self.properties, f)

    @classmethod
    def dumpTo(cls, properties, f):
        for k, v in sorted(properties.items()):
            f.write("{}={}\n".format(k, v))

    def __getitem__(self, key):
        return self.properties.__getitem__(key)

    def __setitem__(self, key, value):
        return self.properties.__setitem__(key, value)
