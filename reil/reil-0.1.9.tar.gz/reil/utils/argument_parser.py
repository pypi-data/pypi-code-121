import argparse
import collections
import dataclasses
import pathlib
from typing import Any, Dict, List, Optional, Type, Union

from ruamel.yaml import YAML

from reil.utils.yaml_tools import parse_yaml


@dataclasses.dataclass
class CommandlineArgument:
    name: str
    type: Type[Any]
    default: Any


class CommandlineParser:
    def __init__(
            self,
            cmd_args: List[CommandlineArgument],
            extra_args: Optional[Dict[str, Any]] = None) -> None:

        self.parsed_args = vars(self._parse_cmd_args(cmd_args, extra_args))

    @staticmethod
    def _parse_cmd_args(cmd_args: List[CommandlineArgument],
                        extra_args: Optional[Dict[str, str]] = None
                        ) -> argparse.Namespace:
        '''
        Parse command line arguments, and add `extra_args`.
        '''
        arg_parser = argparse.ArgumentParser()

        for arg in cmd_args:
            temp = {'type': arg.type, 'default': arg.default}
            if isinstance(arg.default, (list, tuple)):
                temp['nargs'] = '+'
            arg_parser.add_argument(f'--{arg.name}', **temp)

        parsed_args = arg_parser.parse_args()

        if extra_args is not None:
            parsed_args = arg_parser.parse_args(
                list(b
                     for a in extra_args.items()
                     for b in a),
                namespace=parsed_args)

        return parsed_args


class ConfigParser:
    def __init__(
            self,
            config_filenames: Dict[str, str],
            config_path: Optional[Union[pathlib.Path, str]] = None,
            vars_dict: Optional[Dict[str, str]] = None) -> None:

        self.config: Dict[str, Any]
        if config_filenames:
            self.config = {
                key: self._load_config_file(value, config_path, vars_dict)
                for key, value in config_filenames.items()
            }
        else:
            self.config = collections.defaultdict()

    @staticmethod
    def _load_config_file(
            filename: str,
            path: Optional[Union[pathlib.Path, str]] = None,
            vars_dict: Optional[Dict[str, str]] = None) -> Any:

        _path = pathlib.Path(path or '.')
        _filename = filename if filename.endswith((
            '.yaml', '.yml')) else f'{filename}.yaml'

        with open(_path / _filename, 'r') as f:
            temp = f.read()
            # temp = YAML().load(f)

        if vars_dict:
            for name, value in vars_dict.items():
                temp = temp.replace(f'${name}$', str(value))

        return YAML().load(temp)  # type: ignore

    def extract(
            self, root_name: str, branch_name: str, as_object: bool = False
    ) -> Any:
        conf = self.config[root_name][branch_name]
        if as_object:
            return parse_yaml(conf)

        return conf

    def contains(self, root_name: str, branch_name: str) -> bool:
        return branch_name in self.config[root_name]
