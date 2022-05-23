"""
`docker_run`
=======================================================================
Module will take a local run context and run a job locally in Docker
* Author(s): Bailey Steinfadt
"""

import os
import re
import subprocess
import logging

from embedops_cli.utilities import quote_str_for_platform
from embedops_cli import environment_utilities as envutil
from .eo_types import (
    NoDockerContainerException,
    InvalidDockerContainerException,
    DockerNotRunningException,
    DockerRegistryException,
    LocalRunContext,
)

MAX_CONTAINER_NAME_LENGTH = 30
_logger = logging.getLogger(__name__)


def _remove_special_char(string):
    """
    Remove special characters from the input string.
    """
    # Make an RE character set and pass it as an argument
    # into the compile function
    string_check = re.compile("[~`!@#$%^&*()+=}{\\[\\]|\\\\:;\"'<>?/,]")

    # Remove the special characters
    clean_string = string_check.sub("", string)

    return clean_string


def _clean_job_name(job_name):
    """
    Remove special characters, spaces from the input job name string,
    and truncate it if necessarily.
    """
    # Checkpoint 1: Check for disallowed characters and remove them.
    # Allowed characters: [a-zA-Z0-9][a-zA-Z0-9_.-]
    clean_job_name = _remove_special_char(job_name)

    # Remove spaces
    clean_job_name = clean_job_name.replace(" ", "")

    # Checkpoint 2: Check for the string length and truncate it if necessarily.
    # Container name can only be up to 30 characters long
    if len(clean_job_name) > MAX_CONTAINER_NAME_LENGTH:
        clean_job_name = clean_job_name[0:MAX_CONTAINER_NAME_LENGTH]

    return clean_job_name


# TODO: check that we have a script, docker_tag, and job_name
# TODO: add exceptions to eo_types and raise in here for different issues
def docker_run(run_context: LocalRunContext):
    """Takes a run context and launches Docker with the parameters"""

    if run_context.docker_tag == "":
        raise NoDockerContainerException()

    if "http://" in run_context.docker_tag:
        raise InvalidDockerContainerException()

    # We're assuming the tool is run from the same directory as the CI YAML
    _pwd = os.getcwd()
    container_name = _clean_job_name(run_context.job_name)

    _logger.debug(f"Current working directory: {_pwd}")
    _logger.debug(f"Clean container name: {container_name}")

    script = ";".join(run_context.script)

    _logger.debug(f"Script as string: {script}")

    envutil.create_job_env_file(run_context.variables)

    dockercmd = ["docker", "run", "--rm"]
    if os.path.exists(envutil.JOB_ENV_FILE):
        dockercmd.extend([f"--env-file={envutil.JOB_ENV_FILE}"])

    quoted_script = quote_str_for_platform(script)
    _docker_run_cmd_arg = (
        f"/bin/bash -c {quoted_script}"  #!!!: Do not split these, it will break the cmd
    )

    dockercmd.extend(
        [
            "--name",
            container_name,
            "-v",
            f"{_pwd}:/eo_workdir",
            "-w",
            "/eo_workdir",
            "-i",
            run_context.docker_tag,
            _docker_run_cmd_arg,
        ]
    )

    _logger.debug(" ".join(dockercmd))

    _rc = None

    try:
        with subprocess.Popen(
            " ".join(dockercmd), shell=True, stdout=subprocess.PIPE
        ) as process:
            while True:
                output = process.stdout.readline()
                # used to check for empty output in Python2, but seems
                # to work with just poll in 2.7.12 and 3.5.2
                # if output == '' and process.poll() is not None:
                if process.poll() is not None:
                    break
                if output:
                    print(output.strip().decode())
        _rc = process.poll()
    except subprocess.CalledProcessError as err:

        _logger.error(f"Subprocess returned an error: {err}")
        # TODO: figure out how to use click to return these to the user
        # and logger to return things to the devs.
        try:
            print(err.stdout.decode("utf-8"))
        except UnicodeDecodeError as decode_err:
            _logger.error(decode_err)
        _logger.error(err.returncode)

        if "Is the docker daemon running?" in str(err.stdout):
            raise DockerNotRunningException from err
        if "Unable to find image" in str(err.stdout):
            raise DockerRegistryException from err

        return err.returncode
    finally:
        envutil.delete_job_env_file()
    return _rc
