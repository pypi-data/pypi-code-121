"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import os
from typing import TYPE_CHECKING, Any, Union, Optional
from pathlib import Path
from functools import cached_property
from configparser import ConfigParser, NoOptionError, NoSectionError

# * Type-Checking Imports --------------------------------------------------------------------------------->
if TYPE_CHECKING:
    from antistasi_sqf_tools.doc_creating.creator import Creator

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


CONFIG_FILE_NAME = "generate_config.ini"


def find_config_file(file_name: str, start_dir: Union[str, os.PathLike] = None) -> Optional[Path]:
    file_name = file_name.casefold()
    start_dir = Path.cwd() if start_dir is None else Path(start_dir).resolve()

    def find_in_dir(current_dir: Path, last_dir: Path = None) -> Optional[Path]:
        if last_dir is not None and last_dir == current_dir and len(current_dir.parts) == 1:
            raise FileNotFoundError(f"Unable to locate the file {file_name!r} in the folder {start_dir.as_posix()!r} or any of its parent folders.")

        for file in current_dir.iterdir():
            if file.is_file() is False:
                continue
            if file.name.casefold() == file_name:
                return file.resolve()

        return find_in_dir(current_dir.parent, last_dir=current_dir)

    return find_in_dir(start_dir, last_dir=None)


class DocCreationConfig(ConfigParser):

    def __init__(self, file_path: Union[str, os.PathLike]):
        super().__init__()
        self.path = Path(file_path).resolve()
        self.folder = self.path.parent
        self.read(self.path, encoding="utf-8")

    @cached_property
    def local_options(self) -> dict[str, Any]:
        return self.get_local_options()

    def get_local_options(self) -> dict[str, Any]:
        section_name = "local"
        _out = {"auto_open": self.getboolean(section_name, "auto_open", fallback=False),
                "browser_for_html": self.get(section_name, "browser_for_html", fallback="firefox"),
                "env_file_to_load": self.get_env_file_to_load()}
        return _out

    def get_source_dir(self, creator: "Creator") -> Path:
        section = f"building_{creator.builder_name.casefold()}" if creator.builder_name is not None else "building"
        key = "source_dir"

        try:
            source_dir = self.get(section, key)
        except (NoSectionError, NoOptionError):
            source_dir = None

        if source_dir in {None, ""}:
            source_dir = self.get("building", "source_dir")

        return self.folder / source_dir

    def get_output_dir(self, creator: "Creator") -> Path:
        section = f"building_{creator.builder_name.casefold()}" if creator.builder_name is not None else "building"
        key = "output_dir"
        try:
            output_dir = self.get(section, key)
        except (NoSectionError, NoOptionError):
            output_dir = None

        if output_dir in {None, ""}:
            output_dir = self.get("building", "output_dir")

        output_dir = output_dir.replace("<builder_name>", creator.builder_name.casefold())

        return self.folder / output_dir

    def get_release_output_dir(self) -> Path:
        output_dir = self.get("release", "output_dir")
        return self.folder / output_dir

    def get_release_source_dir(self) -> Path:
        source_dir = self.get("release", "source_dir")
        return self.folder / source_dir

    def get_release_builder_name(self) -> str:
        return self.get("release", "builder_name", fallback="html")

    def get_env_file_to_load(self) -> Path:
        rel_path = self.get("local", "env_file_to_load", fallback=".env")
        return self.path.joinpath(rel_path)

    def __repr__(self) -> str:

        return f'{self.__class__.__name__}(file_path={self.path.as_posix()!r})'


# region[Main_Exec]
if __name__ == '__main__':
    y = DocCreationConfig(find_config_file("generate_config.ini", r"D:\Dropbox\hobby\Modding\Programs\Github\My_Repos\A3-Antistasi-Docs\source\dev_guide"))
    print(y.get_release_output_dir())
# endregion[Main_Exec]
