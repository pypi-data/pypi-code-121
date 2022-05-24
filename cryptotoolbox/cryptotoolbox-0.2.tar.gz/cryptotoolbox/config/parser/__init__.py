__author__ = "hugo.inzirillo"

from .parsertemplate import NapoleonToolboxConfigParser
from npxlogger import log
import inspect

conf = NapoleonToolboxConfigParser().read().parse()



def config(Cls):
    class NewCls(object):
        def __init__(self, *args, **kwargs):
            self.__instance = Cls(*args, **kwargs)

        @property
        def instance(self):
            return self.__instance

        def __getattribute__(self, s):
            try:
                x = super(NewCls, self).__getattribute__(s)
            except AttributeError:
                pass
            else:
                return x
            x = self.__instance.__getattribute__(s)
            if isinstance(x, dict):
                return x
            else:
                pass

    return Cls


def target(_value: str):
    """

    Parameters
    ----------
    _value : parameter in the config.yml file to target

    Returns
    -------
    dict : value containing the param in the config
    """
    def inner_function(function):
        def wrapper(*args, **kwargs):
            log.info("target value in config :  {value}".format(value=_value))
            kwargs = __get(_value)
            function(*args, **kwargs)

        return wrapper

    return inner_function


def getter(value: str):
    """

    Parameters
    ----------
    value : parameter in the config.yml file to target

    Returns
    -------
    dict : value containing the param in the config
    """
    def inner_function(function):
        def wrapper(*args, **kwargs):
            log.info("target value in config :  {value}".format(value=value))
            return __get_for_getters(value)
        return wrapper

    return inner_function



def __get(_value: str):
    """

    Parameters
    ----------
    _value : target value in config

    Returns
    -------
    dict : value inside the config.yml file

    """
    _schema = _value.split(".")
    _attr = _schema[0]
    _filtered_config = getattr(conf, _attr)
    field = ""
    len_schema = len(_schema)

    if len_schema == 1:
        return {_attr: _filtered_config}
    else:

        for iter in range(1, len(_schema)):
            _field = _schema[iter]
            if _field in _filtered_config:
                _filtered_config = _filtered_config[_field]
                field = _field
            else:
                log.error("missing {field} in config".format(field=field))
                return None
        return {field: _filtered_config}


def __get_for_getters(_value: str):
    """

    Parameters
    ----------
    _value : target value in config

    Returns
    -------
    dict : value inside the config.yml file

    """
    _schema = _value.split(".")
    _attr = _schema[0]
    _filtered_config = getattr(conf, _attr)
    field = ""
    len_schema = len(_schema)

    if len_schema == 1:
        return {_attr: _filtered_config}
    else:

        for iter in range(1, len(_schema)):
            _field = _schema[iter]
            if _field in _filtered_config:
                _filtered_config = _filtered_config[_field]
                field = _field
            else:
                log.error("missing {field} in config".format(field=field))
                return None
        return  _filtered_config



