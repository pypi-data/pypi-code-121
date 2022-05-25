
LOG_DEFAULT_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'format': '{"datetime": "%(asctime)s", "host": ""'
                      '"source": "", "level": "%(levelname)s", '
                      '"source_id": "", "event": "", '
                      '"file_line": "%(pathname)s %(funcName)s: %(lineno)d", '
                      '"msg": "%(message)s"}'

        },
        'json': {
            'class': 'mf_python_tools.JSONLOGFormatter'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'formatter': 'simple',
            'class': 'logging.StreamHandler'
        },
        'consoleJson': {
            'level': 'DEBUG',
            'formatter': 'json',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'INFO',
            'formatter': 'json',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': 'access.log',
            'when': 'D',
            'backupCount': 31,
        },
        'fileError': {
            'level': 'WARNING',
            'formatter': 'json',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': 'error.log',
            'when': 'D',
            'backupCount': 31,
        },
    },
    'loggers': {
        '': {
            'handlers': ['consoleJson'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'tasks': {
            'handlers': ['consoleJson','file','fileError'],
            'level': 'INFO',
            'propagate': False,
        },
        'root': {
            'handlers': ['consoleJson',],
            'level': 'INFO',
            'propagate': False,
        },
        'print': {
            'handlers': ['consoleJson',],
            'level': 'INFO',
            'propagate': False,
        },
        'cement': {
            'handlers': ['consoleJson',],
            'level': 'DEBUG',
            'propagate': False,
        },
        'celery': {
            'handlers': ['consoleJson',],
            'level': 'DEBUG',
            'propagate': False,
        },
        'celery.work': {
            'handlers': ['consoleJson',],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
    "root": {
            'handlers': ['consoleJson',],
            'level': 'INFO',
            'propagate': False,
    }
}
