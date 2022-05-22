import sys
from os.path import exists
from collections import namedtuple
import importlib_metadata as imp_md
import yaml
from pkg_resources import safe_name


class DistInfo(object):
    """
    Class for distribution metadata information
    Attributes:
        environment: PathInfo object (name of environment, path to environment)
        entry_points: List of PathInfo object (name of entry points as installed, path to entry points (from Scripts folder)
        libraries: List of PathInfo object (name of library folders, path to libraries)
        requirements: List of PathInfo object (internal name of requirements, path to files)
    """

    PathInfo = namedtuple("PathInfo", ["name", "path"])

    def __init__(self, configs):
        self._configs = configs

    @classmethod
    def from_yaml(cls, path):
        '''
        Extracts metadata information for a given distribution from a given yaml file
        :param distribution: name of the distribution/repo (not the package)
        :return: DistInfo object with environment, entry points, libraries & requirements information
        '''
        with open(path) as file:
            try:
                configs = yaml.safe_load(file)
            except yaml.YAMLError as exc:
                print(exc)
        return DistInfo(configs)

    @classmethod
    def from_env(cls, distribution:str):
        '''
        Extracts metadata information for a given distribution from the running environment
        :param distribution: name of the distribution/repo (not the package)
        :return: DistInfo object with environment, entry points, libraries & requirements information
        '''
        dist = imp_md.distribution(distribution)
        eps_console = dist.entry_points.select(group="console_scripts")
        entry_points = [{'name': ep.name, 'path': r'{0}\Scripts\{1}'.format(sys.prefix, ep.name)} for ep in eps_console]
        pkgs = [pkg for pkg, dists in imp_md.packages_distributions().items() if
                safe_name(distribution) in dists]  # packages names
        libraries = [{'name': pkg, 'path': str(dist.locate_file(pkg))} for pkg in pkgs]
        requirements = [{'name': 'req-{0}'.format(lib['name']), 'path': r'{0}\requirements.txt'.format(lib['path'])} for
                        lib in libraries if exists(r'{0}\requirements.txt'.format(lib['path']))]
        return DistInfo({
            "environment": {'name': sys.prefix.split("\\")[-1], 'path': sys.prefix},
            "entry_points": entry_points,
            "libraries": libraries,
            "requirements": requirements
        })

    def to_yaml(self, path):
        '''Dumps DistInfo attributes into a given path to a yaml file'''
        with open(path, 'w') as f:
            yaml.dump(self._configs, f)

    @property
    def entry_points(self):
        return [self.__class__.PathInfo(name=ep['name'], path=ep['path']) for ep in self._configs['entry_points']]

    @property
    def environment(self):
        return self.__class__.PathInfo(name=self._configs['environment']['name'], path=self._configs['environment']['path'])

    @property
    def libraries(self):
        return [self.__class__.PathInfo(name=lib['name'], path=lib['path']) for lib in self._configs['libraries']]

    @property
    def requirements(self):
        return [self.__class__.PathInfo(name=lib['name'], path=lib['path']) for lib in self._configs['requirements']]



