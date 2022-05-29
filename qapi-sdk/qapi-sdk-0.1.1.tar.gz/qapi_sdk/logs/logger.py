import logging
import os


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    fh = logging.FileHandler(os.path.join(os.path.dirname(__file__), 'log.logs'))
    formatter = logging.Formatter('%(asctime)s - %(funcName)s(): %(name)s:%(levelname)s: %(message)s',
                                  datefmt='%m/%d/%Y %I:%M:%S %p %Z')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    logger.addHandler(ch)
    logger.addHandler(fh)
    return logger
