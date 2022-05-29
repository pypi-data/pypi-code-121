# logging.py

import logging, os


def mk_logger(timeStamp, *args, name, logDir=None, **kwargs):
    # logging config to put somewhere before calling functions
    # call like: logger.debug(f"logtext: {anyvar}")
    if logDir is None:
        return type("NoLogger", (), {"info": lambda self: "logging-not-active"})
    logger = logging.getLogger(os.sep.join(__name__))
    logger.setLevel(logging.INFO)
    logformat = "%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s"
    datefmt = "%m-%d %H:%M"
    logForm = logging.Formatter(fmt=logformat, datefmt=datefmt)
    # logging here refers to the logDir
    logPath = os.path.join(logDir, f"{name}_{timeStamp}.log")
    logHandler = logging.FileHandler(logPath, mode="a")
    logHandler.setFormatter(logForm)
    logger.addHandler(logHandler)
    return logger
