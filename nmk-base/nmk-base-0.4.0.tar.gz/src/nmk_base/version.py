from abc import abstractmethod

from nmk.model.resolver import NmkStrConfigResolver

import nmk_base


class VersionResolver(NmkStrConfigResolver):
    @abstractmethod
    def get_version(self) -> str:  # pragma: no cover
        pass

    def get_value(self, name: str) -> str:
        return self.get_version()


class NmkBaseVersionResolver(VersionResolver):
    def get_version(self) -> str:
        return nmk_base.__version__
