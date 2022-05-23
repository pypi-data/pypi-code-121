import abc
import json
from typing import Dict, Any, Type


class BaseConfigurableClass(abc.ABC):
    """Base class for all configurable classes."""
    identifier: str = 'BaseConfigurableClass'

    @abc.abstractmethod
    def _to_config(self) -> Dict[str, Any]:
        """
        Return the current configuration of the object in a dictionary that is JSON-serializable.

        This method returns a configuration dictionary that describes the current configuration of the object of the
        configurable class. The configuration dictionary's keys must be strings and the dictionary must be
        JSON-serializable with Python's internal json module. Furthermore, the configuration dictionary must contain
        the identifier of the configurable class.

        :return: JSON-serializable configuration dictionary
        """
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def _from_config(cls, config: Dict[str, Any]) -> "BaseConfigurableClass":
        """
        Create an object of the class that is configured with the given configuration.

        This method creates an object of the class that is configured with the given configuration.

        :param config: configuration of the object
        :return: configured object of the class
        """
        raise NotImplementedError()

    def to_config(self) -> Dict[str, Any]:
        """
        Return the current configuration of the object in a dictionary that is JSON-serializable.

        IMPORTANT: This method must not be overwritten. It calls the abstract method `_to_config()`, which should be
        implemented by the subclasses.

        This method returns a configuration dictionary that describes the current configuration of the object of the
        configurable class. The configuration dictionary's keys must be strings and the dictionary must be
        JSON-serializable with Python's internal json module. Furthermore, the configuration dictionary must contain
        the identifier of the configurable class.

        :return: JSON-serializable configuration dictionary
        """
        config: Dict[str, Any] = self._to_config()

        if not isinstance(config, dict):
            raise TypeError('The provided configuration is not a dictionary!')

        if 'identifier' not in config.keys():
            raise KeyError('The provided configuration does not contain an identifier for the configurable class!')

        # check that the identifier is a string and there exists a registered configurable class for it
        _ = get_configurable_class(config['identifier'])

        return config

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "BaseConfigurableClass":
        """
        Create an object of the class that is configured with the given configuration.

        IMPORTANT: This method must not be overwritten. It calls the abstract method `_from_config()`, which should be
        implemented by the subclasses.

        This method creates an object of the class that is configured with the given configuration. It raises a
        KeyError if the configuration dictionary does not contain the key 'identifier' or there is no registered
        configurable class with the given key and a TypeError if the given configuration is not a dictionary or the
        identifier is not a string.

        :param config: configuration of the object
        :return: configured object of the class
        """
        if not isinstance(config, dict):
            raise TypeError('The provided configuration is not a dictionary!')

        if 'identifier' not in config.keys():
            raise KeyError('The provided configuration does not contain an identifier for the configurable class!')

        return get_configurable_class(config['identifier'])._from_config(config)

    def to_config_json(self) -> str:
        """
        Return the current configuration of the object as a JSON string and validate it.

        This method obtains a JSON-serializable configuration dictionary using the `to_config()` method and serializes
        it using Python's internal json module. It raises errors in case the obtained configuration dictionary is
        invalid or the JSON serialization fails.

        :return: JSON string of the configuration
        """
        return json.dumps(self.to_config())

    @classmethod
    def from_config_json(cls, config_json_str: str) -> "BaseConfigurableClass":
        """
        Create an object of the class that is configured with the given configuration JSON string.

        This method creates an object of the class that is configured with the given configuration JSON string using the
        `from_config()` method. It raises errors in case the JSON deserialization fails or the deserialized
        configuration is invalid.

        :param config_json_str: JSON string of the configuration
        :return: configured object of the class
        """
        return cls.from_config(json.loads(config_json_str))


_configurable_classes: Dict[str, Type[BaseConfigurableClass]] = {}


def register_configurable_class(configurable_class: Type[BaseConfigurableClass]) -> Type[BaseConfigurableClass]:
    """
    Register and return the given configurable class.

    This method registers and returns the given configurable class. It throws a KeyError if a configurable class with
    the given key is already registered and a TypeError if the given class is not a subclass of BaseConfigurableClass or
    the identifier of the given class is not a string.

    :param configurable_class: configurable class to register
    :return: registered configurable class
    """
    global _configurable_classes

    if not issubclass(configurable_class, BaseConfigurableClass):
        raise TypeError('The given class is not a subclass of BaseConfigurableClass!')

    if not isinstance(configurable_class.identifier, str):
        raise TypeError('The identifier of the given class is not a string!')

    if configurable_class.identifier in _configurable_classes.keys():
        raise KeyError(f'There is already a configurable class with the identifier "{configurable_class.identifier}"!')

    _configurable_classes[configurable_class.identifier] = configurable_class

    return configurable_class


def get_configurable_class(identifier: str) -> Type[BaseConfigurableClass]:
    """
    Return the registered configurable class with the given identifier.

    This method returns the configurable class with the given identifier. It throws a KeyError if no configurable class
    with the given identifier is registered and a TypeError if the given identifier is not a string.

    :param identifier: identifier of the configurable class
    :return: configurable class
    """
    global _configurable_classes

    if not isinstance(identifier, str):
        raise TypeError('The given identifier is not a string!')

    if identifier not in _configurable_classes.keys():
        raise KeyError(f'There is no configurable class with the identifier "{identifier}"!')

    return _configurable_classes[identifier]
