"""Module with functions for 'config' subpackage."""


# TODO - check if some arg name not more times - would be overwritten
# TODO - add frozen and dict_values in __init__
# TODO - Remove one loop over vars (from propagate_base_config_map and do the logic in meta loop)
# TODO - Redefine base_config_map and properties list on class, not in objects in meta

from __future__ import annotations
from typing import Any, TypeVar, Union
from types import UnionType
from copy import deepcopy
import argparse
import sys

from typing_extensions import get_args
from ..property import init_my_properties, MyProperty  # pylint: disable=unused-import
from .. import misc
from .. import types

ConfigType = TypeVar("ConfigType", bound="Config")


class ConfigMeta(type):
    """Config metaclass changing init function.

    Main reason is for being able to define own __init__ but
    still has functionality from parent __init__ that is necessary. With this meta, there is no need
    to use super().__init__ by user.

    As user, you probably will not need it.
    """

    def __init__(cls, name, bases, dct) -> None:
        """Wrap subclass object __init__ to provide Config functionality."""
        type.__init__(cls, name, bases, dct)

        # Avoid base classes here and wrap only user class init
        if name == "Config" and not bases:
            return

        def add_parent__init__(
            self,
            *a,
            dict_values=None,
            frozen=None,
            **kw,
        ):

            self.base_config_map = {}
            self.myproperties_list = []
            self.properties_list = []

            # Call user defined init
            cls._original__init__(self, *a, **kw)

            init_my_properties(self)

            for i, j in vars(type(self)).items():
                if isinstance(j, property):
                    self.properties_list.append(i)

            self.propagate_base_config_map()

            # Update values from dict param in init
            if dict_values:
                for i, j in dict_values.items():
                    setattr(self, i, j)

            if frozen is None:
                self.frozen = True
            else:
                self.frozen = frozen

        cls._original__init__ = cls.__init__
        cls.__init__ = add_parent__init__  # type: ignore

    def __getitem__(cls, key):
        """To be able to access attributes also on class for example for documentation."""
        return getattr(cls, key)


class Config(metaclass=ConfigMeta):  # type: ignore
    """Main config class.

    You can find working examples in module docstrings.
    """

    # Usually this config is created from someone else that user using this config. Therefore new attributes
    # should not be created. It is possible to force it (raise error). It is possible to set frozen to False
    # to enable creating new instances.
    frozen = False

    # You can access attribute from subconfig as well as from main config object, there is proxy mapping
    # config dict. If attribute not found on defined object, it will search through this proxy. It's
    # poppulated automatically in metaclass during init
    base_config_map = {}

    def __init__(self) -> None:
        """Can be overwritten by user and don't need to be called with super().

        Mainly for linting and type hints.
        """
        self.myproperties_list = []
        self.properties_list = []

    def __new__(cls, *args, **kwargs):
        """Just controll that class is subclassed and not instantiated."""
        if cls is Config:
            raise TypeError("Config is not supposed to be instantiated only to be subclassed.")
        return object.__new__(cls, *args, **kwargs)

    def __deepcopy__(self, memo):
        """Provide copy functionality."""
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for i, j in self.__dict__.items():
            if isinstance(j, staticmethod):
                atr = j.__func__
            else:
                atr = j
            setattr(result, i, deepcopy(atr, memo))
        return result

    def __getattr__(self, name: str):
        """Controll logic if attribute from other subcongif is used."""
        try:
            return getattr(self.base_config_map[name], name)

        except KeyError:

            if name not in [
                "_pytestfixturefunction",
                "__wrapped__",
                "pytest_mock_example_attribute_that_shouldnt_exist",
                "__bases__",
                "__test__",
            ]:

                raise AttributeError(f"Variable {name} not found in config.") from None

    def __setattr__(self, name: str, value: Any) -> None:
        """Setup new config values. Define logic when setting attributes from other subconfig class."""
        setter_name = name[1:] if name.startswith("_") else name

        if (
            not self.frozen
            or name == "frozen"
            or name
            in [
                *self.myproperties_list,
                *self.properties_list,
                *vars(self),
            ]
        ):
            object.__setattr__(self, name, value)

        elif setter_name in self.base_config_map:
            setattr(
                self.base_config_map[setter_name],
                name,
                value,
            )

        else:
            raise AttributeError(
                f"Object {str(self)} is frozen. New attributes cannot be set and attribute '{name}' "
                "not found. Maybe you misspelled name. If you really need to change the value, set "
                "attribute frozen to false."
            )

    def __getitem__(self, key):
        """To be able to be able to use same syntax as if using dictionary."""
        return getattr(self, key)

    def __setitem__(self, key, value):
        """To be able to be able to use same syntax as if using dictionary."""
        setattr(self, key, value)

    def __call__(self, *args: Any, **kwds) -> None:
        """Just to be sure to not be used in unexpected way."""
        raise TypeError("Class is not supposed to be called. Just inherit it to create custom config.")

    def propagate_base_config_map(self) -> None:
        """Provide transfering arguments from base or from sub configs.

        Config class has subconfigs. It is possible to access subconfigs attributes from main config or from
        any other level because of this function.
        """
        for k, i in vars(self).items():
            if hasattr(i, "myproperties_list"):
                for j in i.myproperties_list:
                    self.base_config_map[j] = i

            elif hasattr(i, "properties_list"):
                for j in i.properties_list:
                    self.base_config_map[j] = i

            # i is iterated subconfig and self is higher level config
            if isinstance(i, Config):
                i.propagate_base_config_map()  #  type: ignore
                self.base_config_map.update(i.base_config_map)
                i.base_config_map.update(self.base_config_map)

    def copy(self: ConfigType) -> ConfigType:
        """Create deep copy of config and all it's attributes.

        Returns:
            ConfigType: Deep copy.
        """
        return deepcopy(self)

    def update(self, content: dict) -> None:
        """Bulk update with dict values.

        Args:
            content (dict): E.g {"arg_1": "value"}

        Raises:
            AttributeError: If some arg not found in config.
        """
        for i, j in content.items():
            if hasattr(self, i):
                setattr(self, i, j)
            else:
                raise AttributeError(f"Config has no attribute {i}")

    def reset(self) -> None:
        """Reset config to it's default values."""
        copy = type(self)()

        for i in vars(copy).keys():
            setattr(self, i, copy[i])

        for i in copy.myproperties_list:
            setattr(self, i, copy[i])

        for i in copy.properties_list:
            setattr(self, i, copy[i])

    def get_dict(self) -> dict:
        """Get flat dictionary with it's values.

        Returns:
            dict: Flat config dict.
        """
        normal_vars = {
            key: value
            for key, value in vars(self).items()
            if not key.startswith("__")
            and not callable(value)
            and not hasattr(value, "myproperties_list")
            and key not in ["myproperties_list", "properties_list", "frozen", "base_config_map"]
        }

        property_vars = {
            # Values from myproperties
            **{key: getattr(self, key) for key in self.myproperties_list},
            # Values from properties
            **{key: getattr(self, key) for key in self.properties_list},
        }

        normal_vars = {
            i: j for i, j in normal_vars.items() if not (i.startswith("_") and i[1:] in property_vars)
        }

        dict_of_values = {**normal_vars, **property_vars}

        # From sub configs
        for i in vars(self).values():
            if hasattr(i, "myproperties_list"):
                subconfig_dict = i.get_dict()
                dict_of_values.update(subconfig_dict)

        return dict_of_values

    def with_argparse(self, about: str | None = None) -> None:
        """Parse sys.argv flags and update the config.

        For using with CLI. When using `with_argparse` method.

        1) Create parser and add all arguments with help
        2) Parse users' sys args and update config ::

            config.with_argparse()

        Now you can use in terminal like. ::

            python my_file.py --config_arg config_value

        Only basic types like int, float, str, list, dict, set are possible as eval for using type like numpy
        array or pandas DataFrame could be security leak.

        Args:
            about (str, optional): Description used in --help. Defaults to None.

        Raises:
            SystemExit: If arg that do not exists in config.

        Note:
            If using boolean, you must specify the value. Just occurrence, e.g. --my_arg is not True.
        """
        if len(sys.argv) <= 1 or misc.GLOBAL_VARS.jupyter:
            return

        # Add settings from command line if used
        parser = argparse.ArgumentParser(usage=about)

        config_dict = self.get_dict()

        for i in config_dict.keys():
            try:
                help_str = type(self)[i].__doc__
            except AttributeError:
                help_str = type(self.base_config_map[i])[i].__doc__

            parser.add_argument(f"--{i}", help=help_str)

        try:
            parsed_args = parser.parse_known_args()
        except SystemExit as err:
            if err.code == 0:
                sys.exit(0)

            raise SystemExit(
                f"Config args parsing failed. Used args {sys.argv}. Check if args and values are correct "
                "format. Each argument must have just one value. Use double quotes if spaces in string. "
                "For dict e.g. \"{'key': 666}\". If using bool, there has to be True or False."
            ) from err

        if parsed_args[1]:
            raise RuntimeError(
                f"Config args parsing failed on unknown args: {parsed_args[1]}."
                "It may happen if variable not exists in config."
            )

        # Non empty command line args
        parser_args_dict = {}

        # All variables are parsed as strings
        # If it should not be string, infer type
        for i, j in parsed_args[0].__dict__.items():

            if j is None:
                continue

            try:
                used_type = type(self)[i].allowed_types
            except AttributeError:
                used_type = type(self.base_config_map[i])[i].allowed_types

            if used_type is not str:
                try:
                    # May fail if for example Litera["string1", "string2"]
                    parser_args_dict[i] = types.str_to_infer_type(j)
                except ValueError:
                    parser_args_dict[i] = j
                except Exception:
                    # UnionType stands for new Union | syntax
                    if type(used_type) in [type(Union[str, float]), UnionType] and str in get_args(used_type):
                        parser_args_dict[i] = j
                    else:
                        raise RuntimeError(
                            f"Type not inferred error. Config option {i} type was not inferred and it cannot "
                            "be a string. Only literal_eval is used in type inferring from CLI parsing. "
                            "If you need more complex types like numpy array, try to use it directly from "
                            "python."
                        )
            else:
                parser_args_dict[i] = j

        self.update(parser_args_dict)
