import sys
import collections.abc
import copy
import logging
import logging.config
import inspect


def get_logger(name):
    """
    Add caller module name as prefix to "name" parameter and
    return default logging.getLogger
    """
    module_name = inspect.stack()[1].frame.f_globals["__name__"]
    return logging.getLogger(f"{module_name}.{name}")


class LogProducer:
    """
    Retrieve the caller class name
    """
    @property
    def logger(self):
        spec = sys.modules[self.__class__.__module__].__spec__
        name = self.__class__.__qualname__
        if spec is not None:
            name = f"{spec.name}.{name}"

        return logging.getLogger(name)


_config = {
    "version": 1,
    "formatters": {
        "color_formatter": {
            "()": "colorlog.ColoredFormatter",
            "format": (
                "%(asctime)s %(log_color)s[%(levelname)s] "
                "%(reset)s\t%(name)s - %(funcName)s - %(message)s"
            ),
        },
        "default_formatter": {
            "format": (
                "%(asctime)s [%(levelname)s] %(name)s - %(funcName)s - %(message)s"
            )
        },
    },
    "handlers": {
        "console": {"class": "colorlog.StreamHandler", "formatter": "color_formatter"}
    },
}

_on_update_cb = set()


def get_config(config):
    """
    Returns the current logging configuration dictionary as previously set or
    updated by :py:func:`~olympe.log.set_config` or
    :py:func:`~olympe.log.update_config` respectively.

    See: `Logging config dictionary schema <https://docs.python.org/3/library/logging.config.html#logging-config-dictschema>`_
    """
    global _config
    return _config


def _update_dict_recursive(res, update):
    for k, v in update.items():
        if isinstance(v, collections.abc.Mapping):
            res[k] = _update_dict_recursive(res.get(k, {}), v)
        else:
            res[k] = v
    return res


def update_config(update, on_update=None):
    """
    Update (recursively) the current logging configuration dictionary.

    See: `Logging config dictionary schema <https://docs.python.org/3/library/logging.config.html#logging-config-dictschema>`_

    """
    global _config
    global _on_update_cb
    new_config = copy.deepcopy(_config)
    _update_dict_recursive(new_config, update)
    new_config["disable_existing_loggers"] = False
    logging.config.dictConfig(new_config)
    if on_update is not None:
        _on_update_cb.add(on_update)

    for cb in _on_update_cb:
        cb()
    _config = new_config
