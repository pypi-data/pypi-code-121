import logging
import sys


def get_logger(logger_name: str, log_level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(logger_name)
    h = logging.StreamHandler(sys.stdout)
    log_format = '[%(levelname)s] %(asctime)s - %(name)s: %(message)s'
    h.setFormatter(logging.Formatter(log_format))
    logger.addHandler(h)
    logger.setLevel(log_level)
    logger.propagate = False

    return logger
