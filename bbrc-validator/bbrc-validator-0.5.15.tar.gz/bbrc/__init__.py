from .version import __version__
import os.path as op
import logging.config as logconf

logconf.fileConfig(op.join(op.dirname(__file__), 'data', 'logconf.ini'))
