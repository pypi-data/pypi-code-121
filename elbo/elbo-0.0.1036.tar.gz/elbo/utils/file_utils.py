import logging
import os
import tarfile
import tempfile

import coloredlogs
import yaml

from elbo.resources import ElboResources
from elbo.utils.misc_utils import generate_short_rand_string

logger = logging.getLogger("elbo.ai.client")
coloredlogs.install(level="DEBUG", logger=logger, fmt="%(name)s %(message)s")


def get_temp_file_path(prefix="elbo-archive", tgz=False):
    """
    Generate a name for temp file
    :return: A random temp file name
    """
    rand_string = f"{prefix}-{generate_short_rand_string()}"
    if tgz:
        rand_string = f"{rand_string}.tgz"

    path = os.path.join(tempfile.mkdtemp(), rand_string)
    return path


def create_tar_gz_archive(output_filename, source_dir):
    """
    Create a tar gzip file

    :param output_filename: The name of the output file
    :param source_dir: The directory to tar and gzip
    :return: None
    """
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))


def read_config(config_file):
    """
    Read the config file and verify that is valid and has all the requirements parameters
    :param config_file: The input config file
    :return: Python dictionary of YAML
    """
    with open(config_file) as fd:
        task_config = yaml.load(fd, Loader=yaml.FullLoader)

    keys = task_config.keys()

    valid_config = True
    if "task_dir" not in keys:
        logger.error(
            f"needs 'task_dir' to be specified in '{config_file}'. This is the directory "
            f"where your source code is present."
        )
        valid_config = False

    if "run" not in keys:
        logger.error(
            f"needs 'run' to be specified in '{config_file}'. This is the command that should be "
            f"run to start the task."
        )
        valid_config = False

    if "artifacts" not in keys:
        logger.error(
            f"needs 'artifacts to be specified in '{config_file}'. This directory would be tar-balled and saved "
            f"as output for your task."
        )
        valid_config = False

    if not valid_config:
        return None

    return task_config


def extract_file(local_file_name):
    os.makedirs(ElboResources.ELBO_CACHE_DIR, exist_ok=True)
    temp_dir = tempfile.mkdtemp()
    if local_file_name.endswith("tar.gz") or local_file_name.endswith(".tgz"):
        tar = tarfile.open(local_file_name, "r:gz")
        tar.extractall(temp_dir)
        tar.close()
    elif local_file_name.endswith("tar"):
        tar = tarfile.open(local_file_name, "r:")
        tar.extractall(temp_dir)
        tar.close()
    return temp_dir
