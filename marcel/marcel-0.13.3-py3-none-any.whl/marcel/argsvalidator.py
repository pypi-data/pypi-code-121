# This file is part of Marcel.
# 
# Marcel is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or at your
# option) any later version.
# 
# Marcel is distributed ax the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Marcel.  If not, see <https://www.gnu.org/licenses/>.


import marcel.exception
import marcel.functionwrapper

# A marcel op has arguments. An argument is one of:
#    - An optional flag with no value
#    - An optional flag with one value
#    - An optional flag with either an optional value
#    - An anonymous value: not preceded by a flag
# Constraints on groups of flags:
#     - At most one must be specified
#     - Exactly one must be specified
# Additional constraints can be checked by the op.


VALUE_NONE = 1
VALUE_ONE = 2
VALUE_OPTIONAL = 3
NO_DEFAULT = object()


class ArgsError(marcel.exception.KillCommandException):

    def __init__(self, op_name, message):
        super().__init__(f'Operator {op_name}: {message}')


class Arg:

    def __init__(self, name, convert):
        assert name is not None
        self.name = name
        self.convert = (lambda x: x) if convert is None else convert

    def __repr__(self):
        return self.name


class Flag(Arg):

    def __init__(self, name, convert, short, long, value):
        super().__init__(name, convert)
        assert short is not None or long is not None
        assert short is None or len(short) == 2 and Flag.plausible(short)
        assert long is None or len(long) >= 3 and Flag.plausible(long)
        assert value in (VALUE_NONE, VALUE_ONE, VALUE_OPTIONAL)
        self.short = short
        self.long = long
        self.value = value

    def __repr__(self):
        return self.short if self.short else self.long

    @staticmethod
    def plausible(x):
        if type(x) is not str:
            return False
        if len(x) < 2:
            return False
        if len(x) == 2:
            return x[0] == '-' and x[1] != '-'
        return x[:2] == '--' and x[2] != '-'


class Anon(Arg):

    def __init__(self, name, convert, default):
        super().__init__(name, convert)
        self.default = default


class AnonList(Arg):

    def __init__(self, name, convert):
        super().__init__(name, convert)


class ArgsValidator:

    def __init__(self, op_name, env):
        self.op_name = op_name
        self.env = env
        self.flag_args = []
        self.anon_args = []
        self.anon_list_arg = None
        self.at_most_one_names = []
        self.exactly_one_names = []
        self.specification_checked = False
        # A hack to sneak the op currently being validated to function()
        self.current_op = None

    def add_flag_no_value(self, name, short, long):
        self.flag_args.append(Flag(name, None, short, long, VALUE_NONE))

    def add_flag_one_value(self, name, short, long, convert=None):
        self.flag_args.append(Flag(name, convert, short, long, VALUE_ONE))

    def add_flag_optional_value(self, name, short, long, convert=None):
        self.flag_args.append(Flag(name, convert, short, long, VALUE_OPTIONAL))

    def add_anon(self, name, default=NO_DEFAULT, convert=None):
        self.anon_args.append(Anon(name, convert, default))

    def add_anon_list(self, name, convert=None):
        self.anon_list_arg = AnonList(name, convert)

    def at_most_one(self, *names):
        name_set = set()
        for name in names:
            assert (name in [flag.name for flag in self.flag_args] or
                    name in [anon.name for anon in self.anon_args]), name
            name_set.add(name)
        assert len(names) == len(name_set)
        self.at_most_one_names.append(name_set)

    def exactly_one(self, *names):
        name_set = set()
        for name in names:
            assert (name in [flag.name for flag in self.flag_args] or
                    name in [anon.name for anon in self.anon_args]), name
            name_set.add(name)
        assert len(names) == len(name_set)
        self.exactly_one_names.append(name_set)

    def check_specification(self):
        # Make sure each flag is unique
        flags = set()
        for flag in self.flag_args:
            if flag.short:
                assert flag.short not in flags
                flags.add(flag.short)
            if flag.long:
                assert flag.long not in flags
                flags.add(flag.long)
        # Arg names must be unique
        names = set()
        for flag in self.flag_args:
            assert flag.name not in names
            names.add(flag.name)
        for anon in self.anon_args:
            assert anon.name not in names
            names.add(anon.name)
        # A VALUE_OPTIONAL flag is incompatible with anon args
        if len(self.anon_args) > 0 or self.anon_list_arg is not None:
            for flag in self.flag_args:
                assert flag.value != VALUE_OPTIONAL
        # Anons that don't have default values are required and must precede those that do have defaults.
        no_default = True
        for anon in self.anon_args:
            if no_default and anon.default is not NO_DEFAULT:
                no_default = False
            assert no_default == (anon.default is NO_DEFAULT)
        # Anons before the terminal list of anons are required. (Otherwise we can't tell where the list begins.)
        if self.anon_list_arg is not None:
            for anon in self.anon_args:
                assert anon.default == NO_DEFAULT
        self.specification_checked = True

    def validate(self, args, op):
        assert self.specification_checked
        self.current_op = op
        args_iterator = iter(args)
        flags = {}  # arg name -> value
        anon = {}  # arg name -> value
        anon_list = []
        current_flag_arg = None
        flag_ok = len(self.flag_args) > 0
        try:
            while True:
                arg = next(args_iterator)
                flag_arg = self.find_flag(arg)
                if flag_arg:
                    # Flag
                    if flag_ok:
                        if flag_arg.name not in flags:
                            flags[flag_arg.name] = True
                            current_flag_arg = flag_arg
                        else:
                            raise ArgsError(self.op_name, f'{arg} specified more than once.')
                    else:
                        raise ArgsError(self.op_name, 'Flags must all appear before the first anonymous arg')
                elif Flag.plausible(arg) and flag_ok:
                    # Unknown flag
                    raise ArgsError(self.op_name, f'Unknown flag {arg}')
                else:
                    # Flag value or anon
                    if current_flag_arg is None or current_flag_arg.value == VALUE_NONE:
                        if len(anon) >= len(self.anon_args):
                            # Anon list
                            if self.anon_list_arg:
                                anon_list.append(self.anon_list_arg.convert(arg))
                            else:
                                raise ArgsError(self.op_name, f'Too many anonymous args.')
                        else:
                            # Anon
                            anon_arg = self.anon_args[len(anon)]
                            anon[anon_arg.name] = anon_arg.convert(arg)
                        flag_ok = False
                    else:
                        # Flag value
                        flags[current_flag_arg.name] = current_flag_arg.convert(arg)
                        current_flag_arg = None
        except StopIteration:
            pass
        except Exception as e:
            if current_flag_arg:
                raise ArgsError(self.op_name, f'flag {current_flag_arg}: {e}')
            else:
                raise ArgsError(self.op_name, f'{e}')
        # Check that all flags are known, and check that values were supplied exactly when permitted or required.
        for flag_name, value in flags.items():
            flag_arg = self.find_by_name(flag_name)
            if flag_arg is None:
                raise ArgsError(self.op_name, f'{flag_arg} is not a valid flag.')
            if flag_arg.value == VALUE_ONE and value is True:
                raise ArgsError(self.op_name, f'{flag_arg} requires a value.')
            if flag_arg.value == VALUE_NONE and value is not True:
                raise ArgsError(self.op_name, f'{flag_arg} must not provide a value.')
        # Check mutual exclusion
        names = list(flags.keys())
        names.extend(anon.keys())
        for group in self.at_most_one_names:
            if len(group.intersection(names)) > 1:
                description = '{' + ', '.join([str(self.find_by_name(name)) for name in group]) + '}'
                raise ArgsError(self.op_name, f'Cannot specify more than one of {description}')
        # Check exactly-one args
        for group in self.exactly_one_names:
            if len(group.intersection(names)) != 1:
                description = '{' + ', '.join([str(self.find_by_name(name)) for name in group]) + '}'
                raise ArgsError(self.op_name, f'Must specify exactly one of {description}')
        # Fill in defaults for unspecified anon args. Also check that required anons have been specified.
        assert len(anon) <= len(self.anon_args)
        while len(anon) < len(self.anon_args):
            anon_arg = self.anon_args[len(anon)]
            if anon_arg.default == NO_DEFAULT:
                raise ArgsError(self.op_name, f'No value specified for {anon_arg.name}.')
            anon[anon_arg.name] = anon_arg.default
        # If there is an anon list, include it
        if self.anon_list_arg:
            anon[self.anon_list_arg.name] = anon_list
        op.__dict__.update(flags)
        op.__dict__.update(anon)

    def find_flag(self, x):
        if type(x) is str:
            for flag in self.flag_args:
                if flag.short == x or flag.long == x:
                    return flag
        return None

    def find_by_name(self, name):
        for flag in self.flag_args:
            if flag.name == name:
                return flag
        for anon in self.anon_args:
            if anon.name == name:
                return anon
        return None

    def function(self, source):
        f = marcel.functionwrapper.FunctionWrapper(source=source, globals=self.env.namespace)
        f.set_op(self.current_op)
        f.check_validity()
        return f
