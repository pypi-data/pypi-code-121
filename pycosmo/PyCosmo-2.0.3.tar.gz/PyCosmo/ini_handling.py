# This file is part of PyCosmo, a multipurpose cosmology calculation tool in Python.
#
# Copyright (C) 2013-2021 ETH Zurich, Institute for Particle and Astrophysics and SIS
# ID.
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this
# program.  If not, see <http://www.gnu.org/licenses/>.


import os


from configparser import ConfigParser


class Bunch:
    def __init__(self, dict_=None):
        if dict_ is None:
            dict_ = {}
        self.__dict__["_dict"] = dict_

        for section_name, options in dict_.items():
            if isinstance(options, dict):
                options = Bunch(options)
            setattr(self, section_name, options)

    def __setattr__(self, name, value):
        if name == "_dict":
            self.__dict__[name] = value
            return
        self.__dict__["_dict"][name] = value

    __setitem__ = __setattr__

    def __delitem__(self, name):
        if name in self._dict:
            del self._dict[name]
            del self.__dict__[name]
            return
        raise KeyError

    __delattr__ = __delitem__

    def __getstate__(self):
        # does default opearation, but still needed so that __setstate__ is
        # used also
        return self.__dict__

    def __setstate__(self, dd):
        # Default implementation but needed,because _not implementing __setstate__ would
        # forward to __getattr__. In __getattr__ self._dict is required which does not
        # exist at this time point during unpickling.  So it would call __getattr__
        # again to lookup "_dict" which results in infinite recursion!
        self.__dict__.update(dd)

    def __getattr__(self, name):
        if name in self._dict:
            return self._dict[name]
        # forward methods:
        return getattr(self._dict, name)

    def __getitem__(self, name):
        return self._dict[name]

    def __iter__(self):
        return iter(self._dict)

    def __dir__(self):
        return self._dict.keys()

    def as_dict(self):
        result = {}
        for key, value in self._dict.items():
            if isinstance(value, Bunch):
                value = value.as_dict()
            result[key] = value
        return result

    def __str__(self):
        return self._to_str(indent="")

    def _to_str(self, indent):
        lines = []
        for key, value in self.items():
            line = ""
            if isinstance(value, Bunch):
                line += "\n"
                line += "[{}]".format(key)
                lines.append(line)
                lines.append(value._to_str(indent + "    "))
            else:
                line += "{} = {}".format(key, value)
                lines.append(line)
        return "\n".join(lines).strip()


def load_ini(path):
    c = ConfigParser()
    c.optionxform = str

    assert os.path.isfile(path), path
    c.read(path)

    data = {}

    for section in c.sections():
        data[section] = {}
        for option in c.options(section):
            value = c.get(section, option)
            data[section][option] = best_convert(value)

    return Bunch(data)


def best_convert(txt):
    if not txt.strip():
        return None
    if txt.lower().strip() == "false":
        return False
    if txt.lower().strip() == "true":
        return True
    for t in (int, float, eval):
        try:
            return t(txt)
        except (ValueError, TypeError, NameError, SyntaxError):
            continue
    return txt
