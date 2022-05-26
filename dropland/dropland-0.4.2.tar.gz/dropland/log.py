import logging.config
import os
import sys

import dropland.tr
from dropland.tr.static import StaticTranslator

DEBUG_MODE = os.environ.get('DEBUG', False)

LOGGING_CONFIG_DEFAULTS = dict(
    version=1,
    disable_existing_loggers=False,
    loggers={
        'dropland': {
            'level': 'INFO' if not DEBUG_MODE else 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'dropland.worker': {
            'level': 'INFO' if not DEBUG_MODE else 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'apscheduler.scheduler': {
            'level': 'INFO' if not DEBUG_MODE else 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
    },
    handlers={
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'stream': sys.stdout,
        },
        'error_console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'stream': sys.stderr,
        },
    },
    formatters={
        'generic': {
            'format': '%(asctime)s [%(process)d] [%(levelname)s] %(message)s',
            'datefmt': '[%Y-%m-%d %H:%M:%S %z]',
            'class': 'logging.Formatter',
        },
        'verbose': {
            'format': '%(asctime)s [%(process)d/%(threadName)s] [%(levelname)-5.8s] %(message)s (%(name)s:%(module)s:%(lineno)s)',
            'datefmt': '[%Y-%m-%d %H:%M:%S %z]',
            'class': 'logging.Formatter',
        },
        'simple': {
            'format': '%(asctime)s [%(levelname)-5.8s] %(message)s'
        },

    },
)


logging.config.dictConfig(LOGGING_CONFIG_DEFAULTS)
logger = logging.getLogger('dropland')
worker_logger = logging.getLogger('dropland.worker')

tr = StaticTranslator()
tr.load_package(dropland.tr, 'dropland.toml')
