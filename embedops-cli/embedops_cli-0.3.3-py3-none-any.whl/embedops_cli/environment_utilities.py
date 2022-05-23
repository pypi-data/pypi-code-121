"""
`environment_utilities`
=======================================================================
Managing the environment variables for CLI context
* Author(s): Bailey Steinfadt
"""

import os
import re

ENV_FILE = ".env"
PROJECT_ENV_FILE = ".eo_env"
JOB_ENV_FILE = ".eo_job_env"


def _clean_env_file(env_file_contents: list):
    """clean env file for Docker"""
    clean_contents = []
    for line in env_file_contents:
        line = line.strip()
        if not line.startswith("#"):
            line = re.sub(r'=["\']', r"=", line)
            line = re.sub(r'["\']\s*$', r"", line)
            if len(line) > 0:
                clean_contents.append(f"{line}\n")
    return clean_contents


def _read_envvar_strings(filename):
    clean_env_contents = []

    if os.path.exists(filename):
        project_env_contents = ""
        with open(filename, "r", encoding="utf-8") as env_file:
            project_env_contents = env_file.readlines()

        clean_env_contents += _clean_env_file(project_env_contents)
    return clean_env_contents


# TODO: use a dynaconf loader.write to export the
#   config from dynaconf/internal settings to an env file that can be passed to docker
def create_job_env_file(yaml_vars: dict):
    """
    Collect environment variables from .eo_env and the run context
    and combine them into a file to be passed into the docker container.
    """
    delete_job_env_file()
    envvar_strings = []

    envvar_strings += _read_envvar_strings(ENV_FILE)
    envvar_strings += _read_envvar_strings(JOB_ENV_FILE)

    with open(JOB_ENV_FILE, "a", encoding="utf-8") as env_file:

        for line in envvar_strings:
            env_file.write(line)

        for key, value in yaml_vars.items():
            env_file.write(f"\n{key}={value}")


def delete_job_env_file():
    """Delete job env file"""
    if os.path.exists(JOB_ENV_FILE):
        os.remove(JOB_ENV_FILE)
