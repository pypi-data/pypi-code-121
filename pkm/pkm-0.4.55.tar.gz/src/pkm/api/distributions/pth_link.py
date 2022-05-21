import os
from pathlib import Path
from typing import List, Optional

from pkm.utils.files import ensure_exists
from pkm.utils.strings import startswith_any


class PthLink:
    """
    taken mostly from the site module documentation:

    A path configuration file is a file whose name has the form name.pth and exists in site packages directories;
    its contents are additional items (one per line) to be added to sys.path.
    Non-existing items are never added to sys.path,
    and no check is made that the item refers to a directory rather than a file.
    No item is added to sys.path more than once.
    Blank lines and lines beginning with # are skipped.
    Lines starting with import (followed by space or tab) are executed.
    """

    def __init__(self, path: Path, links: List[Path], imports: Optional[List[str]] = None):
        """
        :param path: the path to the link itself
        :param links: collection of paths that this link should be responsible for appending to the `sys.path`
        :param imports: collection of imports that this link should be responsible for
                        loading when python sites is resolved
        """
        self.path = path
        self.imports = imports
        self.links = links

    def save(self):
        with self.path.open('w+') as out:
            if self.imports:
                for imp in self.imports:
                    out.write('import ')
                    out.write(imp)
                    out.write(os.linesep)

            for link in self.links:
                out.write(str(link.absolute()))
                out.write('\n')

    @classmethod
    def load(cls, path: Path) -> "PthLink":
        ensure_exists(path)

        imports: List[str] = []
        links: List[Path] = []

        with path.open('r') as pth_fd:
            while line := pth_fd.readline():
                if line := line.strip():
                    if line.startswith("#"):
                        continue
                    elif startswith_any(line, ('import ', 'import\t')):
                        imports.append(line[len("import"):].strip())
                    else:
                        links.append(Path(line))

        return PthLink(path, links, imports)
