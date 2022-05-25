from typing import Generator, Tuple, List

from pydmt.api.builder import Builder, SourceFile, TargetFile, Node
from pydmt.utils.digest import sha1_file


class OneSourceOneTarget(Builder):
    """
    This is a builder which has one source file and one target file
    """

    def __init__(self, source: str, target: str):
        super().__init__()
        self.source = source
        self.target = target
        self.sources = [SourceFile(filename=source)]
        self.targets = [TargetFile(filename=target)]

    def get_sources(self) -> List[Node]:
        return self.sources

    def get_targets(self) -> List[Node]:
        return self.targets

    def yield_results(self) -> Generator[Tuple[str, str], None, None]:
        yield sha1_file(self.target), self.target
