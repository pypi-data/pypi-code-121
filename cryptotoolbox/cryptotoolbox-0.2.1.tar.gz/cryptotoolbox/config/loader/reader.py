__author__ = "hugo.inzirillo"

import os

import yaml

from napoleontoolbox import __path__
from napoleontoolbox.napoleon_config_tools.loader.abstractreader import AbstractYamlReader
from napoleontoolbox.napoleon_config_tools.object.config import Config
from npxlogger import log


class YamlReader(AbstractYamlReader):
    def __init__(self):
        pass

    def _read(self, _path: str) -> dict:
        """

        Parameters
        ----------
        _path : path of file to read .yml

        Returns
        -------

        """
        with open(_path, 'r') as stream:
            try:
                _config = yaml.safe_load(stream)
                log.info("reading current config : {conf}".format(conf=_config))
                return _config
            except yaml.YAMLError as exc:
                log.error(exc)


class NapoleonConfigReader(YamlReader):

    @property
    def __config_file_path(self):
        return os.path.join(__path__[0], Config.FILE)

    def _read(self, _path: str = None) -> dict:
        """

        Parameters
        ----------
        _path : path of file to read .yml

        Returns
        -------

        """

        if _path is not None:
            path = _path
        else:
            path = self.__config_file_path

        return super(NapoleonConfigReader, self)._read(path)

    def read(self, _path: str = None) -> dict:
        """
        This method read the config.yml file
        Returns
        -------

        """

        return self._read(_path)
