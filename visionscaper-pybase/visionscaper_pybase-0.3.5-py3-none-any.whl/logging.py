import logging

LOGGING_FORMAT = '%(levelname)s: %(name)s::%(funcName)s : %(message)s'

logging.basicConfig(format=LOGGING_FORMAT)


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    return logger
