__author__ = "hugo.inzirillo"

from abc import abstractmethod

from napoleontoolbox.napoleon_config_tools.loader.reader import NapoleonConfigReader, Config
from napoleontoolbox.napoleon_config_tools.object import Profile, Env
from napoleontoolbox.napoleon_config_tools.parser.abstractparser import AbstractParserTemplate
from npxlogger import log


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances.keys():
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ParserTemplate(AbstractParserTemplate):
    """
    This object is a template of method to implement to create an instance of parser
    """

    @abstractmethod
    def _load(self):
        """
        This method will look up the yaml file attached to your loader
        Returns
        -------

        """
        raise NotImplemented

    @abstractmethod
    def _existing(self):
        """
        This method will check the existence of a config file
        Returns
        -------

        """
        raise NotImplemented

    @abstractmethod
    def _read_file(self):
        """
        This method will read the config file yaml
        Returns
        -------

        """
        raise NotImplemented

    @property
    @abstractmethod
    def config(self) -> Config:
        """
        This property return the Config
        Returns
        -------

        """
        raise NotImplemented

    @property
    @abstractmethod
    def reader(self):
        """
        This property return the Feeder
        Returns
        -------

        """
        raise NotImplemented


class Parser(ParserTemplate):
    """
    This object is the core of config parser
    """

    def __init__(self):
        self.__config = Config()
        self.__reader = NapoleonConfigReader()
        self.__raw_config = dict()

    def _load(self):
        """
        This method will look up the yaml file attached to your loader
        Returns
        -------

        """
        pass

    def _existing(self):
        """
        This method will check the existence of a config file
        Returns
        -------

        """
        pass

    def _read_file(self):
        """
        This method will read the config file yaml
        Returns
        -------

        """
        pass

    @property
    def config(self) -> Config:
        """
        This property return the Config
        Returns
        -------

        """
        return self.__config

    @property
    def reader(self) -> NapoleonConfigReader:
        """
        This property return the Feeder
        Returns
        -------

        """
        return self.__reader

    @property
    def raw_config(self) -> dict:
        """
        This property return the Config
        Returns
        -------

        """
        return self.__raw_config

    @raw_config.setter
    def raw_config(self, _raw_config):
        """
        This property return the Config
        Returns
        -------

        """
        self.__raw_config = _raw_config


@Profile(Env.TEST.value)
class NapoleonToolboxConfigParser(Parser):
    """
    This object will parse the config.yml file to retrieve all the settings
    The object will be automatically triggered
    """
    __metaclass__ = Singleton

    _config = {}

    @property
    def config(self) -> Config:
        return self.__config

    @config.setter
    def config(self, _conf: Config):
        self.__config = _conf

    def parse(self) -> Config:
        """
        This method will parse the config and return a Config object
        Returns
        -------

        """
        self.config = Config()
        _ = {setattr(self.config, key, value) for key, value in self.raw_config.items()}
        log.info("current loader : {config}".format(config=self.config))
        NapoleonToolboxConfigParser._config[self.config.profile] = self.config
        return NapoleonToolboxConfigParser._config[self.config.profile]

    def _read_file(self):
        """
        This method will read the config file yaml
        Returns
        -------

        """

        self.raw_config = self.reader.read()
        return self

    def read(self):
        """
        This method will return the file reader
        Returns
        -------

        """
        return self._read_file()
