"""Utils."""

import logging

from py_console import console, textColor


def get_level_color(levelno):
    return {
        logging.CRITICAL: textColor.MAGENTA,
        logging.ERROR: textColor.RED,
        logging.WARNING: textColor.YELLOW,
        logging.INFO: textColor.GREEN,
        logging.DEBUG: textColor.BLUE,
        logging.NOTSET: textColor.WHITE,
    }.get(levelno, textColor.WHITE)


class CustomLoggingFormatter(logging.Formatter):
    def format(self, record):
        color = get_level_color(record.levelno)
        return console.highlight(
            f'({record.name}-{record.levelname}): {record.msg}',
            color)


def get_logger(logger_name='custom'):
    formatter = CustomLoggingFormatter()
    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)
    sh.setFormatter(formatter)

    log = logging.getLogger(logger_name)
    log.propagate = False
    log.setLevel(logging.DEBUG)
    log.handlers = [sh]
    return log


if __name__ == '__main__':
    log = get_logger('testing')
    log.critical('This is CRITICAL')
    log.error('This is ERROR')
    log.warning('This is WARNING')
    log.info('This is INFO')
    log.debug('This is DEBUG')
    print('This is a regular print')
