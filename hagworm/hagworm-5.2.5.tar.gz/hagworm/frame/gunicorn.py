# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

from uvicorn.workers import UvicornWorker

from .fastapi.base import DEFAULT_HEADERS


DEFAULT_LOG_CONFIG = {
    'root': {
        'level': 'INFO',
        'handlers': ['loguru'],
    },
    'loggers': {
        'gunicorn.error': {
            'level': 'INFO',
            'handlers': ['loguru'],
            'qualname': 'gunicorn.error',
        },
        'gunicorn.access': {
            'level': 'INFO',
            'handlers': ['loguru'],
            'qualname': 'gunicorn.access',
        },
    },
    'handlers': {
        'loguru': {
            'class': 'hagworm.extend.logging.LogInterceptor',
        },
    },
}

SIMPLE_LOG_CONFIG = {
    'root': {
        'level': 'INFO',
        'handlers': ['loguru'],
    },
    'loggers': {
        'gunicorn.error': {
            'level': 'INFO',
            'handlers': ['loguru'],
            'qualname': 'gunicorn.error',
        },
    },
    'handlers': {
        'loguru': {
            'class': 'hagworm.extend.logging.LogInterceptor',
        },
    },
}

DEFAULT_WORKER_STR = r'hagworm.frame.gunicorn.Worker'


class Worker(UvicornWorker):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.config.headers.extend(DEFAULT_HEADERS)
