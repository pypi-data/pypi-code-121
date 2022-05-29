
import yaml
from .utils import is_param
from .parameter import Parameters
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

__all__ = ["Template"]

class Template():
    
    def __init__(self, yaml_dict):
        self.yaml_dict = yaml_dict

        for key, sub_template in self.yaml_dict.items():
            if is_param(sub_template):
                setattr(self, key, Parameters(key, sub_template))
            else:
                setattr(self, key, Template(sub_template))
        pass

    
    @staticmethod
    def from_yaml(template_file : str):
        with open(template_file, "r") as stream:
            yaml_template = yaml.load(stream, Loader=Loader)
        return Template(yaml_template)