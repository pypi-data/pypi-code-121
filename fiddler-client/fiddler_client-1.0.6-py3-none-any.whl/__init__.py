"""
Fiddler Client Module
=====================

A Python client for Fiddler service.

TODO: Add Licence.
"""
import logging
from logging.handlers import RotatingFileHandler

from . import utils
from ._version import __version__
from .client import Fiddler, PredictionEventBundle
from .core_objects import (
    BatchPublishType,
    Column,
    DatasetInfo,
    DataType,
    ExplanationMethod,
    FiddlerPublishSchema,
    FiddlerTimestamp,
    MLFlowParams,
    ModelDeploymentParams,
    ModelInfo,
    ModelInputType,
    ModelTask,
)
from .fiddler_api import FiddlerApi
from .file_processor.src.constants import (
    CSV_EXTENSION,
    PARQUET_COMPRESSION,
    PARQUET_ENGINE,
    PARQUET_EXTENSION,
    PARQUET_ROW_GROUP_SIZE,
)
from .packtools import gem
from .utils import ColorLogger
from .validator import PackageValidator, ValidationChainSettings, ValidationModule

__all__ = [
    '__version__',
    'BatchPublishType',
    'Column',
    'ColorLogger',
    'DatasetInfo',
    'DataType',
    'Fiddler',
    'FiddlerApi',
    'FiddlerTimestamp',
    'FiddlerPublishSchema',
    'gem',
    'MLFlowParams',
    'ModelDeploymentParams',
    'ModelInfo',
    'ModelInputType',
    'ModelTask',
    'ExplanationMethod',
    'PredictionEventBundle',
    'PackageValidator',
    'ValidationChainSettings',
    'ValidationModule',
    'utils',
    # Exposing constants
    'CSV_EXTENSION',
    'PARQUET_EXTENSION',
    'PARQUET_ROW_GROUP_SIZE',
    'PARQUET_ENGINE',
    'PARQUET_COMPRESSION',
]

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# console logger
c_handler = logging.StreamHandler()
c_format = logging.Formatter('%(name)s %(levelname)s %(message)s')
c_handler.setFormatter(c_format)


# file handlers
f_handler = RotatingFileHandler(
    'fiddler_client.log', mode='a', maxBytes=5 * 1024 * 1024
)
f_format = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
f_handler.setFormatter(f_format)

logger.addHandler(c_handler)
logger.addHandler(f_handler)
