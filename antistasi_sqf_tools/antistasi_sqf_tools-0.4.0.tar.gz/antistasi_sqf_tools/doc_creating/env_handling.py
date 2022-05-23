"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import os
from enum import Enum
from typing import Mapping, Callable
from pathlib import Path

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


class EnvNames(Enum):
    CONFIG_PATH = ("_DOC_CREATION_CONFIG_PATH", str)

    @property
    def var_name(self) -> str:
        return self.value[0]

    @property
    def conversion_func(self) -> Callable:
        return self.value[1]

    def __str__(self) -> str:
        return str(self.value[0])


class EnvManager:

    def __init__(self, env_names: type[Enum] = EnvNames) -> None:
        self.env_names = env_names
        self.loaded_env_files = {}

    @property
    def all_env_names(self) -> Mapping[str, str]:
        return {k: v.var_name for k, v in self.env_names.__members__.items()}

    def add_config_path(self, config_path: Path) -> None:
        os.environ[self.env_names.CONFIG_PATH.var_name] = self.env_names.CONFIG_PATH.conversion_func(config_path)

    def load_env_file(self, env_file_path: Path) -> None:
        if env_file_path.is_file() is False:
            return {}
        dot_env = DotEnv(env_file_path)
        dot_env.set_as_environment_variables()
        self.loaded_env_files[env_file_path] = dot_env.dict()


    # region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
