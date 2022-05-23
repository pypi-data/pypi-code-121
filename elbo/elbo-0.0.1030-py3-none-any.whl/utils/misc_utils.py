import logging
import subprocess
import sys
import uuid

import coloredlogs
import requests

logger = logging.getLogger("elbo.client")
coloredlogs.install(level="DEBUG", logger=logger, fmt="%(name)s %(message)s")


def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix) :]
    return text


def say_hello(user_first_name=None):
    """
    Say hello to the user
    :param user_first_name: The user's first name
    :return: None
    """
    # TODO: Add fortune? Random geetings?
    if user_first_name is None:
        logger.info(f"Hey there 👋")
    else:
        logger.info(f"Hey {user_first_name} 👋, welcome!")


def generate_short_rand_string():
    """
    Generate a short random string
    :return: The random string
    """
    return str(uuid.uuid4())[:8]


def get_task_id_from_file_name(file_name):
    """
    Get the task id from the file name
    :param file_name: The file name
    :return: The task id
    """
    try:
        task_id = file_name.split("-")[2].split(".")[0]
    except IndexError as _:
        task_id = None

    return task_id


def is_elbo_outdated():
    output = subprocess.check_output([sys.executable, "-m", "pip", "show", "elbo"])
    output = str(output, encoding="utf-8").split("\n")
    installed_version = 0
    for line in output:
        if "Version:" in line:
            installed_version = line.split(" ")[1]
    try:
        response = requests.get(f"https://pypi.org/pypi/elbo/json")
        latest_version = response.json()["info"]["version"]
    except requests.exceptions.ConnectionError as _:
        return False, installed_version
    return installed_version != latest_version, latest_version


def exit_handler():
    is_outdated, latest_version = is_elbo_outdated()
    if is_outdated:
        logger.warning(f"A new version of elbo is available, please install using:")
        logger.warning(f"pip3 install elbo=={latest_version}")


def log():
    _logger = logging.getLogger("elbo.client")
    coloredlogs.install(level="DEBUG", logger=_logger, fmt="%(name)s %(message)s")
    return _logger
