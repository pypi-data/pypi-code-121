import logging

LOG_FORMAT = '%(asctime)s [%(process)d] [%(levelname)s] %(message)s'
LOG_DATEFMT = '[%Y-%m-%d %H:%M:%S %z]'


def configure_logger(name: str, log_level: str):
    log_level = log_level.upper()
    logger = logging.getLogger(name)
    handler = logging.StreamHandler()
    handler.setLevel(log_level)
    formatter = logging.Formatter(LOG_FORMAT, LOG_DATEFMT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(log_level)
    logger.propagate = False
