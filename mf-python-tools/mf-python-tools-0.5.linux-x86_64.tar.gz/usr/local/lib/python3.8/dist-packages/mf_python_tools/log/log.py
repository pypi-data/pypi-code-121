
import copy
import logging
import logging.config
from .logging_config import LOG_DEFAULT_CONFIG

log_config = copy.deepcopy(LOG_DEFAULT_CONFIG)

handlers_config = {
    'level': 'INFO',
    'formatter': 'json',
    'class': 'logging.StreamHandler',
}

loggers_config = {
    "handlers": ["consoleJson"],
    "level": "INFO",
    "propagate": False,
}

def log_init():
    logging.config.dictConfig(log_config)


def add_handlers(name, default=True,data=None):
    if name in log_config['handlers']:
        return False
    if data is None:
        if default:
            log_config['handlers'][name] = handlers_config
        else:
            return False
    else:
        if default :
            handlers_config_data = copy.deepcopy(handlers_config)
            handlers_config_data.update(data)
            log_config['handlers'][name] = handlers_config_data
        else:
            log_config['handlers'][name] = data
    return True

def add_loggers(name,default=True,data=None):
    if name in log_config['loggers']:
        return False
    if data is None:
        if default:
            log_config['loggers'][name] = loggers_config
        else:
            return False
    else:
        if default :
            loggers_config_data = copy.deepcopy(loggers_config)
            loggers_config_data.update(data)
            log_config['loggers'][name] = loggers_config_data
        else:
            log_config['loggers'][name] = data
    return True

def _update(filed, name, data):
    if filed not in ['handlers', 'loggers']:
        return False
    if name not in log_config[filed]:
        return False
    log_config[filed][name].update(data)
    return True

def update_handlers(name,data):
    return _update('handlers', name, data)

def update_loggers(name,data):
    return _update('loggers', name, data)

def get_log_config():
    return log_config