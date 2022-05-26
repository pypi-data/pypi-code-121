import logging


def configure_logger(verbose):
    logging_level = logging.INFO
    if verbose:
        logging_level = logging.DEBUG
    logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s %(message)s', level=logging_level,
                        datefmt='%Y-%m-%d %H:%M:%S')