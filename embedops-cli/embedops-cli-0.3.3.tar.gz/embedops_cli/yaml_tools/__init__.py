"""A collection of tools for woriking with YAML CI config files"""
import yaml
from embedops_cli.eo_types import BadYamlFileException


def open_yaml(yaml_filename: str):
    """Open YAML file and load it for parsing"""
    with open(yaml_filename, "r", encoding="utf-8") as stream:
        try:
            glyml = yaml.safe_load(stream)
            return glyml
        except yaml.YAMLError as err:
            raise BadYamlFileException() from err
