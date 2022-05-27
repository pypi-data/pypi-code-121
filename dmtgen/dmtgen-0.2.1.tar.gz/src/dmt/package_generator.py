"""" Basis of all package generators """
from abc import ABC
from typing import Dict

from dmt.common.package import Package


class PackageGenerator(ABC):
    """" Basis of all package generators """

    def generate_package(self, config: Dict):
        """Generate package"""
        raise NotImplementedError()

    def root_package(self) -> Package:
        """Returns the root package """
        raise NotImplementedError()
