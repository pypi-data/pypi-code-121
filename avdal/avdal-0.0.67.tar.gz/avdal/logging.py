import os
import time
import logging
from logging import handlers


def get_logger(appname, filename=None, stdout=True, level=logging.DEBUG):
    logger = logging.getLogger(appname)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s')

    if filename:
        base, name_ext = os.path.split(filename)
        name, ext = os.path.splitext(name_ext)
        date = time.strftime('%Y-%m-%d')
        filename = os.path.join(base, f"{name}_{date}{ext}")

        file = handlers.TimedRotatingFileHandler(filename, when='D')
        file.setFormatter(formatter)
        logger.addHandler(file)

    if stdout:
        stdout = logging.StreamHandler()
        stdout.setFormatter(formatter)
        logger.addHandler(stdout)

    logger.setLevel(level)

    return logger
