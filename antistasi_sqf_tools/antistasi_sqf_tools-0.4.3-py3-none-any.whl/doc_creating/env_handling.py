"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import os
from enum import Enum, Flag, auto, unique

from pathlib import Path
from typing import Optional
from collections.abc import Iterable, Mapping, Callable
from collections import UserList, defaultdict
from frozendict import frozendict
# * Third Party Imports --------------------------------------------------------------------------------->
from dotenv.main import DotEnv

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class EnvCategory(Flag):
    AUTO_CREATED = auto()
    OPTIONAL = auto()
    REQUIRED = auto()

    @property
    def verbose_name(self):
        return self.name.replace("_", " ").title()


BASE_ENV_SPECS = {}


class EnvSpec:
    var_name_prefix: str = "_DOC_CREATION"
    __slots__ = ("name", "conversion_func", "category", "description")

    def __init__(self, name: str, category: EnvCategory, conversion_func: Callable[[object], str] = str, description: str = None) -> None:
        self.name = name
        self.conversion_func = conversion_func
        self.category = category
        self.description = description or ""

    @property
    def var_name(self) -> str:
        return f"{self.var_name_prefix}_{self.name}"

    def set_env(self, value: object) -> None:
        value = self.conversion_func(value)
        os.environ[self.var_name] = value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, var_name={self.var_name!r}, category={self.category!r}, conversion_func={self.conversion_func!r}, description={self.description!r})"


def bool_to_env_str(in_bool: bool):
    return "1" if in_bool is True else "0"


config_path_spec = EnvSpec(name="CONFIG_PATH", category=EnvCategory.AUTO_CREATED, description=None)
BASE_ENV_SPECS[config_path_spec.name] = config_path_spec


github_token_spec = EnvSpec(name="GITHUB_TOKEN", category=EnvCategory.OPTIONAL, description=None)
BASE_ENV_SPECS[github_token_spec.name] = github_token_spec


local_repo_path_spec = EnvSpec(name="LOCAL_REPO_PATH", category=EnvCategory.AUTO_CREATED | EnvCategory.OPTIONAL, description=None)
BASE_ENV_SPECS[local_repo_path_spec.name] = local_repo_path_spec

is_release_spec = EnvSpec(name="IS_RELEASE", category=EnvCategory.AUTO_CREATED, conversion_func=lambda x: "1" if x is True else "0", description=None)
BASE_ENV_SPECS[is_release_spec.name] = is_release_spec

BASE_ENV_SPECS: frozendict[str, EnvSpec] = frozendict(**BASE_ENV_SPECS)


class EnvManager:

    def __init__(self, env_specs: Mapping[str, EnvSpec] = BASE_ENV_SPECS) -> None:
        self.env_specs = env_specs
        self.loaded_env_files = {}

    @ property
    def all_env_names(self) -> Mapping[str, str]:
        _out = {}

        for cat in EnvCategory.__members__.values():

            filtered_env_specs = [i for i in self.env_specs.values() if cat in i.category]
            if filtered_env_specs:
                _out[cat] = filtered_env_specs

        return _out

    def set_env(self, name: str, value: object, strict: bool = False) -> None:
        try:
            spec = self.env_specs[name.upper()]
            spec.set_env(value)
        except KeyError as e:
            if strict is True:
                raise e
            os.environ[name] = str(value)

    def load_env_file(self, env_file_path: Path) -> None:
        if env_file_path.is_file() is False:
            return {}
        dot_env = DotEnv(env_file_path)
        dot_env_dict = dot_env.dict()
        converter_dot_env_dict = {}
        relevant_specs = {name: spec for name, spec in self.env_specs.items() if EnvCategory.OPTIONAL in spec.category or EnvCategory.REQUIRED in spec.category}
        for k, v in dot_env_dict.items():
            try:
                spec = relevant_specs[k]
                spec.set_env(v)
                converter_dot_env_dict[spec.var_name] = v
            except KeyError:
                os.environ[k] = str(v)
                converter_dot_env_dict[k] = v

        self.loaded_env_files[env_file_path] = converter_dot_env_dict


    # region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
