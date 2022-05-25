import logging

def init_logger():
    LOG = logging.getLogger("mylogger")
    format = logging.Formatter("<<<<< LOGGER >>>>> %(module)s >>> %(funcName)s line:%(lineno)d >>> %(message)s")
    handler = logging.StreamHandler()
    handler.setFormatter(format)
    LOG.addHandler(handler)
    LOG.setLevel(logging.WARNING)
