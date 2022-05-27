from pathlib import Path
from typing import List

from nmk.model.resolver import NmkListConfigResolver


class FilesFinder(NmkListConfigResolver):
    def find_in_folders(self) -> List[str]:  # pragma: no cover
        pass

    def get_value(self, name: str) -> List[Path]:
        # Iterate on source paths, and find all python files
        return [src_file for src_path in map(Path, self.find_in_folders()) for src_file in filter(lambda f: f.is_file(), src_path.rglob("*.py"))]


class PythonFilesFinder(FilesFinder):
    def find_in_folders(self) -> List[str]:
        return self.model.config["pythonSrcFolders"].value


class PythonTestFilesFinder(FilesFinder):
    def find_in_folders(self) -> List[str]:
        return [self.model.config["pythonTestSources"].value]
