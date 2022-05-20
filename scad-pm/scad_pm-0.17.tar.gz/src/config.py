import abc
import dataclasses
import logging
import typing

import scopeton.scope
from dataclasses_json import dataclass_json
import yaml

# @dataclasses.dataclass
# @dataclass_json
from scopeton.decorators import Inject


class ArgsConfig:
    lib_path: str
    upgrade: bool
    v: bool
    pm_file: str

    def __str__(self):
        return "{}:[{}]".format(self.__class__.__name__, self.__dict__)


class DEP_TYPES:
    git = "git"


@dataclass_json()
@dataclasses.dataclass
class Dependency(object):
    url: str
    path: typing.Optional[str] = None
    revision: typing.Optional[str] = None
    dependency_type: str = DEP_TYPES.git


@dataclass_json()
@dataclasses.dataclass
class FileConfig(object):
    dependencies: typing.List[Dependency]
    dep_path: typing.Union[str, None] = None


class ConfigParser:
    @abc.abstractmethod
    def parse(self, file: str):
        pass

    @abc.abstractmethod
    def is_type(self, file: str) -> bool:
        pass


class YamlConfigParser(ConfigParser):
    def is_type(self, file: str) -> bool:
        return file.split(".")[-1] == 'yaml'

    @Inject()
    def __init__(self, args_config: ArgsConfig):
        self.args_config = args_config

    def parse(self, file: str):
        with open(file, "r") as stream:
            data = yaml.safe_load(stream)
            logging.info("Parsing data: {}".format(data))
            return self.map_data(data)

    def map_data(self, data):
        conf = FileConfig.from_dict(data)  # type: FileConfig
        for dep in conf.dependencies:
            if dep.path is None:
                dep.path = dep.url.split("/")[-1].split(".")[0]
        return conf


class PmConfigParser(ConfigParser):
    def is_type(self, file: str) -> bool:
        return file.split(".")[-1] == 'pm'

    @Inject()
    def __init__(self, args_config: ArgsConfig):
        self.args_config = args_config

    def parse(self, file: str):
        with open(file, "r") as stream:
            data = stream.readlines()
            logging.info("Parsing data: {}".format(data))
            return self.map_data(data)

    def map_data(self, data):
        deps = [self._parse_dep(k) for k in data]
        deps = filter(lambda x: x is not None, deps)
        return FileConfig(list(deps))

    def _parse_dep(self, k):
        k = k.strip()
        if k.startswith("#"):
            return None
        path = k.split("/")[-1].split(".")[0]
        if "#" in k:
            branch = k.split("#")[1]
        else:
            branch = None
        path = path.split("#")[0]
        return Dependency(
            k,
            path=path,
            revision=branch
        )


class MainConfigParser:
    @Inject()
    def __init__(self, scope: scopeton.scope.Scope):
        self.scope = scope
        self.parsers = scope.getInstances(ConfigParser)
        logging.info("Config parsers: {}".format(self.parsers))

    def _get_parser(self, file: str) -> ConfigParser:
        for k in self.parsers:
            if k.is_type(file):
                return k
        raise Exception("Parser not found for file: {}".format(file))

    def parse(self, file: str) -> FileConfig:
        return self._get_parser(file).parse(file)
