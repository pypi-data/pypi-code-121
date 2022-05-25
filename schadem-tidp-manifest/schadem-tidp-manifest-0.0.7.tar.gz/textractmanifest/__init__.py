import logging
from logging import NullHandler
from .manifest import IDPManifest, Query, IDPManifestSchema, QuerySchema

logging.getLogger('tidpmanifest').addHandler(NullHandler())

__version__ = '0.0.7'
