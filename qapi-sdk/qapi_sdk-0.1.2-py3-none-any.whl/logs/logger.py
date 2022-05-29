import logging
import os


def get_logger(name):
    # Add color to the logs
    logging.addLevelName(logging.INFO, "\033[1;32m%s\033[1;0m" % logging.getLevelName(logging.INFO))
    logging.addLevelName(logging.WARNING, "\033[1;33m%s\033[1;0m" % logging.getLevelName(logging.WARNING))
    logging.addLevelName(logging.ERROR, "\033[1;31m%s\033[1;0m" % logging.getLevelName(logging.ERROR))
    logging.addLevelName(logging.CRITICAL, "\033[1;31m%s\033[1;0m" % logging.getLevelName(logging.CRITICAL))
    # Create a logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    # fh = logging.FileHandler(os.path.join(os.path.dirname(__file__), 'log.logs'))
    # formatter = logging.Formatter('%(asctime)s - %(funcName)s(): %(name)s:%(levelname)s: %(message)s',
    #                               datefmt='%m/%d/%Y %I:%M:%S %p %Z')
    formatter = logging.Formatter('%(asctime)s - %(funcName)s(): %(levelname)s: %(message)s',
                                  datefmt='%m/%d/%Y %I:%M:%S %p %Z')
    ch.setFormatter(formatter)
    # fh.setFormatter(formatter)
    logger.addHandler(ch)
    # logger.addHandler(fh)
    return logger
