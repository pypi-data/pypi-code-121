"""" Basis of all template based generators """
from abc import ABC,abstractmethod
from pathlib import Path
from typing import Dict
from jinja2.environment import Template
from .package_generator import PackageGenerator


class TemplateBasedGenerator(ABC):
    """" Basis of all template based generators """

    @abstractmethod
    def generate(self,package_generator: PackageGenerator, template : Template, outputfile: Path, config: Dict):
        """Will be called once for each template registered to it"""
        raise NotImplementedError()

    @staticmethod
    def first_to_upper(string):
        """ Make sure the first letter is uppercase """
        return string[:1].upper() + string[1:]
