# vim:set ts=4 sw=4 et nowrap syntax=python ff=unix:
#
# Copyright 2020 Mark Crewson <mark@crewson.net>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
A configuration file parser.
"""

import os
import os.path
import platform
import re

from .baseobject import BaseObject, NonStdlibError
from .string_conversion import convert_to_bool, convert_to_list

##############################################################################


class ConfigError (NonStdlibError):
    """Base exception class for Config exceptions"""
    pass


class InvalidCommandlineArgument (ConfigError):
    pass


class InvalidConfigParameter (ConfigError):
    pass

##############################################################################


class Config (BaseObject):

    # Platform-specific config file locations
    XDG_CONFIG_HOME = 'XDG_CONFIG_HOME'
    XDG_FALLBACK_PATH = '~/.config'
    WINDOWS_APPDATA = 'APPDATA'
    WINDOWS_FALLBACK_PATH = '~\\AppData\\Roaming'
    DARWIN_FALLBACK_PATH = '~/Library/Application Support'

    SECTION_REX = re.compile(r'^\[(.*?)\]')
    KEYVALUE_REX = re.compile(r'^([^=]+)=(.*)$')
    SUBST_REX = re.compile(r'\${([\w:]+)}')
    VARSEC_REX = re.compile('^([a-z]+)::(.*)')

    options = {'base_config_dict':              None,
               'error_on_invalid_config_param': (False, convert_to_bool),
               'skipped_sections':              ([], convert_to_list),
               'censored_params':               None,
               }

    def __init__(self, filenames=[], **kw):
        """constructor"""
        super(Config, self).__init__(**kw)
        self._parse_options(Config.options, kw)

        if type(filenames) != list:
            filenames = [filenames, ]
        self.filenames = filenames
        self.conf = dict()
        self.cmd_conf = dict()

        if self.filenames:
            self._load_config_files()
        else:
            if self.base_config_dict is None:
                self.conf = dict(DEFAULT=dict())
            else:
                self.conf = dict(DEFAULT=dict(self.base_config_dict))

    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except LookupError:
            return default

    def get_sections(self):
        sections = list(self.conf)
        sections.sort()
        return sections

    def section(self, section):
        return self.conf[section]

    def dump_config(self, file):
        sections = self.conf.keys()
        for sec in sections:
            if type(self.conf[sec]) != dict:
                continue
            file.write('[%s]\n' % sec)
            params = self.conf[sec].keys()
            for param in params:
                if self.censored_params is not None and '{}::{}'.format(sec, param) in self.censored_params:
                    file.write('%s = xxxxxxx\n' % (param))
                else:
                    file.write('%s = %s\n' % (param, self.conf[sec][param]))
            file.write('\n')

    def read_nonconfig_section(self, section_name, concat_all_config_files=False):
        rev_filenames = self.filenames
        rev_filenames.reverse()
        found_section = False
        section_lines = []
        for filename in rev_filenames:
            config_filename = self._find_config_file(filename)
            if config_filename is None:
                continue

            fp = open(config_filename, 'r')
            lines = fp.readlines()
            fp.close()

            linecount = 0
            num_lines = len(lines)

            # find the section_name
            while linecount < num_lines:
                line = lines[linecount].strip()
                linecount += 1
                if line == '[%s]' % section_name:
                    found_section = True
                    break
            if not found_section:
                continue

            # read the lines until the next section or eof
            while linecount < num_lines:
                line = lines[linecount].strip()
                linecount += 1
                if line and line[0] == '[' and line[-1] == ']':
                    break
                section_lines.append(line)
            linecount += 1

            if found_section and concat_all_config_files is False:
                return section_lines

        return section_lines

    def _load_config_files(self):
        if self.base_config_dict is None:
            self.conf = dict(DEFAULT=dict())
        else:
            self.conf = dict(DEFAULT=dict(self.base_config_dict))
        for filename in self.filenames:
            configFilename = self._find_config_file(filename)
            if configFilename is None:
                continue

            fp = open(configFilename, 'r')
            lines = fp.readlines()
            fp.close()

            config_lines = []
            linecount = 0
            while linecount < len(lines):
                line = re.sub('#.*$', '', lines[linecount]).strip()
                if not line:
                    linecount += 1
                    continue
                while line[-1] == '\\':
                    line = line[:-1] + lines[linecount+1].strip()
                    linecount += 1
                config_lines.append(line)
                linecount += 1

            section = 'DEFAULT'
            in_skipped_section = False
            for line in config_lines:
                section_mo = Config.SECTION_REX.match(line)
                if section_mo:
                    section = section_mo.group(1)
                    if section in self.skipped_sections:
                        in_skipped_section = True
                    else:
                        in_skipped_section = False
                        self.conf[section] = dict()
                    continue

                if in_skipped_section is True:
                    continue

                if Config.KEYVALUE_REX.match(line):
                    key, value = line.split('=', 1)
                    key = key.rstrip()
                    value = value.lstrip()

                    value = os.path.expanduser(os.path.expandvars(value))

                    # Check for variable substitution
                    # This allows you to stick things like "${key}" or "${section::key}"
                    # into the config file.
                    subst = Config.SUBST_REX.search(value)
                    while subst:
                        var = subst.group(1)
                        # Work around the use of ${} for other purposes (for now)
                        varsec = Config.VARSEC_REX.match(var)
                        try:
                            if varsec:
                                prefix = self.conf[varsec.group(1)][varsec.group(2)]
                            else:
                                prefix = self.conf[section][var]
                        except KeyError:
                            prefix = ""
                        # If not subst was found, check for an environment variable
                        if not prefix:
                            try:
                                prefix = os.environ[var]
                            except KeyError:
                                pass
                        value = re.sub(r'\${%s}' % var, prefix, value)
                        subst = Config.SUBST_REX.search(value)

                    self.conf[section][key] = value

                elif self.error_on_invalid_config_param is True:
                    raise InvalidConfigParameter("Invalid config parameter: %s" % line)

                # else ignore any invalid lines

    def _find_config_file(self, filename):
        if filename.startswith("/"):
            if os.path.exists(filename):
                return filename
        else:
            for path in self._default_config_paths():
                fullname = os.path.expandvars(os.path.expanduser(os.path.join(path, filename)))
                if os.path.exists(fullname):
                    return fullname
        return None

    def _default_config_paths(self, system=None):
        paths = ['.']
        if system is None:
            system = platform.system()
        if system == 'Windows':
            paths.append(self.WINDOWS_FALLBACK_PATH)
            if self.WINDOWS_APPDATA in os.environ:
                paths.append(os.environ[self.WINDOWS_APPDATA])
        else:
            # Unix-Like
            if self.XDG_CONFIG_HOME in os.environ:
                paths.append(os.environ[self.XDG_CONFIG_HOME])
            paths.append(self.XDG_FALLBACK_PATH)

            if system == 'Darwin':
                # Mac-specific path
                paths.append(self.DARWIN_FALLBACK_PATH)

            paths.append('/usr/local/etc')
            paths.append('/etc')

        return paths

    def __getitem__(self, key):
        if key in self.cmd_conf:
            return self.cmd_conf[key]
        else:
            if key.find('::') >= 0:
                section, key = key.split('::', 1)
                if not section:
                    section = 'DEFAULT'
            else:
                section = 'DEFAULT'
            return self.conf[section][key]


##############################################################################

if __name__ == "__main__":
    pass

##############################################################################
# THE END
