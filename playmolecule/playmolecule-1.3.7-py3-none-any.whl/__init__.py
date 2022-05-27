from playmolecule.session import (
    Session,
    SessionError,
    UserNotFoundError,
    UserFailedRegistrationError,
    UserUpdateError,
)
from playmolecule.job import (
    Job,
    JobStatus,
    JobBucketNotFoundError,
    JobConfigNotLoadedError,
)
from playmolecule.datacenter import DataCenter, DataCenterError, Dataset
from playmolecule.jsonlogger import enable_json_logger
from playmolecule.config import loadConfig
import logging.config
import os


__init__dir = os.path.dirname(os.path.abspath(__file__))

try:
    logging.config.fileConfig(
        os.path.join(__init__dir, "logging.ini"), disable_existing_loggers=False
    )
except Exception as e:
    print(f"PlayMolecule: Logging setup failed with error {e}")

loadConfig()
