from typing import List, Dict, Union, Optional


class Partitioning:
    def __init__(self, default: Optional[Union[str, List[str]]] = None):
        self.default: Optional[Union[str, List[str]]] = None
        if default is not None and isinstance(default, str):
            self.default = [default]
        elif default is not None:
            self.default = default

        self._partitions: Dict[str, List[str]] = {}

    @staticmethod
    def from_dict(
        partitions: Dict[str, List[str]],
        default: Optional[Union[str, List[str]]] = None,
    ) -> "Partitioning":
        partitioning = Partitioning(default)
        partitioning.update(partitions)
        return partitioning

    def update(self, value: Dict[str, List[str]]):
        self._partitions.update(value)

    def __getitem__(self, key: str):
        return self._partitions.get(key, self.default)

    def __setitem__(self, key: str, val: List[str]):
        self._partitions[key] = val
