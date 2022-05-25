# -*- coding: utf-8 -*-
from pkg_resources import DistributionNotFound, get_distribution
import logging

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = __name__
    __version__ = get_distribution(dist_name).version
except DistributionNotFound:
    __version__ = "unknown"
finally:
    del get_distribution, DistributionNotFound

# # Create a top-level logger
# logger = logging.getLogger("pycarta")
# logger.setLevel(logging.DEBUG)
# # TODO (@bkappes): Redirect the log to a standard location.
# # The log file should be stored in a standard location or a location
# # of the users choosing
# fh = logging.FileHandler("pycarta.log") # File handler
# fh.setLevel(logging.DEBUG)
# ch = logging.StreamHandler() # Console handler
# ch.setLevel(logging.ERROR)
# formatter = logging.Formatter(
#     "%(levelname)s: [%(asctime)s](%(name)s) %(message)s") # Message format.
# fh.setFormatter(formatter)
# ch.setFormatter(formatter)
# logger.addHandler(fh)
# logger.addHandler(ch)
