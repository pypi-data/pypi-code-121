"""
`gh_parser`
=======================================================================
Parser to pull job contexts from .github-ci.yml files
* Author(s): Zhi Xuen Lai
"""
import logging
import re
from embedops_cli.yaml_tools import open_yaml
from ..eo_types import (
    BadYamlFileException,
    LocalRunContext,
)

_logger = logging.getLogger(__name__)


def _check_job_name(string):
    """
    Check if the job name starts with a letter or _ and
    contains only alphanumeric characters, -, or _.
    """
    # Check if the job name starts with a letter or _
    is_first_char_valid = bool(re.match("^[a-zA-Z_]", string[:1]))
    # Check if the job name contains only alphanumeric characters, -, or _
    is_whole_job_name_valid = bool(re.match("^[a-zA-Z0-9_-]*$", string))
    return is_first_char_valid and is_whole_job_name_valid


def get_job_name_list(ghyml_filename: str) -> list:
    """Get list of job names from the given YAML object"""

    try:
        ghyml = open_yaml(ghyml_filename)
    except BadYamlFileException as exc:
        raise BadYamlFileException() from exc

    job_name_list = []

    try:
        for item in ghyml["jobs"]:
            if not _check_job_name(item):
                raise BadYamlFileException()
            job_name_list.append(item)

        return job_name_list
    except (KeyError) as err:
        raise BadYamlFileException() from err


def get_job_list(glyml_filename: str) -> list:
    """Return the list of LocalRunContexts found in the given yaml object"""

    try:
        glyml = open_yaml(glyml_filename)
    except BadYamlFileException as exc:
        raise BadYamlFileException() from exc

    job_list = []

    try:
        default_var_dict = {}
        for tag, value in glyml.items():
            # update default_var_dict
            if tag == "env":
                default_var_dict.update(value)

            if tag == "jobs":
                for job, context in value.items():
                    if not _check_job_name(job):
                        raise BadYamlFileException()
                    job_ctx = _parse_job_context(job, context, default_var_dict)

                    job_list.append(job_ctx)

        return job_list
    except (TypeError, KeyError) as err:
        raise BadYamlFileException() from err


def _parse_job_context(yaml_tag, yaml_value, default_var_dict):
    """Return a LocalRunContexts by parsing a job context"""
    image = ""

    if "container" in yaml_value:
        if "image" in yaml_value["container"]:
            image = yaml_value["container"]["image"]

    # Does not necessarily have variables
    # if it does, add them (via update()) to the default_var_dict
    var_dict = {}
    var_dict.update(default_var_dict)
    if "env" in yaml_value:
        var_dict.update(yaml_value["env"])

    # TODO: parse the | token appropriately
    #       (Note: it's able to parse simple multi-line command)
    # TODO: handle `uses` keyword
    #       (Note: only `run` and `env` keywords are handled at the moment)
    script_list = []
    if "steps" in yaml_value:
        for line in yaml_value["steps"]:
            if "run" in line:
                script_list.append(line["run"])
            if "env" in line:
                var_dict.update(line["env"])
    else:
        raise BadYamlFileException()

    return LocalRunContext(yaml_tag, image, script_list, var_dict)
