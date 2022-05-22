logging_config={
    "version": 1,
    "formatters":{
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        "simple":{
            "format": '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        }
    },
    "handlers":{
        "console":{
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "verbose",
            "stream": "ext://sys.stdout"
        },
        "info_file_handler":{
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "verbose",
            "filename": "log/scheduler_info.log",
            "maxBytes": 10485760,
            "backupCount": 3,
            "encoding": "utf8"
        },
        "error_file_handler":{
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "verbose",
            "filename": "log/scheduler_error.log",
            "maxBytes": 10485760,
            "backupCount": 3,
            "encoding": "utf8"
        },
        'warning_file_handler':{
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            "formatter": "verbose",
            'filename': 'log/scheduler_Warning.log',
            "maxBytes": 10485760,
            "backupCount": 3,
            "encoding": "utf8"
        }
    },
    "loggers":{

    },
    "root":{
        "level": "DEBUG",
        "handlers": ["console", "info_file_handler", "error_file_handler", "warning_file_handler"]
    }
}