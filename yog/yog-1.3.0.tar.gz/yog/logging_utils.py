import logging
import os
import sys
from getpass import getuser
from os.path import join, exists

log = logging.getLogger(__name__)


def setup(app: str):
    ret = logging.getLogger(f"yog")
    ret.setLevel(logging.DEBUG)

    if getuser() == "root":
        log_dir = join("/var", "log", app)
    else:
        log_dir = join(os.environ["HOME"], ".cache", app)

    if not exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    logfile = logging.FileHandler(join(log_dir, "log.txt"))
    logfile.setLevel(logging.DEBUG)
    logfile.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s]: %(message)s [%(pathname)s] [L%(lineno)d]"))
    ret.addHandler(logfile)

    stdout = logging.StreamHandler(sys.stdout)
    stdout.setLevel(logging.INFO)
    stdout.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s]: %(message)s"))
    ret.addHandler(stdout)

    ret.debug("Logging configured.")

    return ret

