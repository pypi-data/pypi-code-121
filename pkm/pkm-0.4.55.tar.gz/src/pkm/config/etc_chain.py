from pathlib import Path
from typing import List, Optional, Union


class EtcChain:
    """
    represents a recursive etc chain finder.
    the idea is that for some applications we want to have "contextual enrichment" for configuration
    e.g., say that we have some configurations file called: x stored in /etc/app-identifier/x
    and in that file there is a project relevant setting p, we want to enable the project to overwrite/merge/remove p,
    so we can add, under the project dir, the file: etc/app-identifier/x with our modifications.
    Now, if, the configuration loader, when reading x, use the etc chain from the root of the project, it will get
    all the "x" files that should affect the configuration.

    It works by finding all instances of the file inside the given context of its parent directories,
    and finally also include the main (/etc/app-identifier/x) configuration in case it wasn't already
    """

    def __init__(self, main: Path, identifier: str):
        self._main = main
        self._identifier = identifier

    def main_config(self, etc_subpath: Union[Path, str]) -> Optional[Path]:
        return self._main / etc_subpath

    def config_chain(
            self, context_path: Path, etc_subpath: Union[str, Path] = "", include_main: bool = True) -> List[Path]:
        # TODO: document order: context to root
        result = []

        search_list = [context_path, *context_path.parents]
        for s in search_list:
            if (sp := s / 'etc' / self._identifier / etc_subpath).exists():
                result.append(sp)

        if (main_subpath := self._main / etc_subpath).exists():
            if include_main and main_subpath not in result:
                result.append(main_subpath)
            elif not include_main and main_subpath in result:
                result.remove(main_subpath)

        return result
