"""
`bb_parser`
=======================================================================
Parser to pull job contexts from bitbucket-pipelines.yml files
* Author(s): Bailey Steinfadt
"""
import logging
from embedops_cli.yaml_tools import open_yaml
from ..eo_types import BadYamlFileException, LocalRunContext

_logger = logging.getLogger(__name__)


def get_job_name_list(bbyml_filename: str):
    """Get list of job names from the given YAML object"""

    try:
        bbyml = open_yaml(bbyml_filename)
    except BadYamlFileException as exc:
        raise BadYamlFileException() from exc

    job_name_list = []

    try:
        for job_def in bbyml["pipelines"]["default"]:
            if "step" in job_def:
                job_name_list.append(job_def["step"]["name"])

            elif "parallel" in job_def:
                for par_step in job_def["parallel"]:
                    job_name_list.append(par_step["step"]["name"])

        if not all(isinstance(job_name, str) for job_name in job_name_list):
            raise BadYamlFileException()

        return job_name_list
    except (KeyError) as err:
        raise BadYamlFileException() from err


def get_job_list(bbyml_filename: str) -> list:
    """Return the list of LocalRunContexts found in the given yaml object"""

    try:
        bbyml = open_yaml(bbyml_filename)
    except BadYamlFileException as exc:
        raise BadYamlFileException() from exc

    job_list = []

    try:
        default_image = "atlassian/default-image:latest"
        if "image" in bbyml:
            default_image = bbyml["image"]

        job_list = _parse_job_context(bbyml, default_image)

        return job_list
    except (KeyError, AttributeError, TypeError) as err:
        raise BadYamlFileException() from err


def _parse_job_context(bbyml, default_image):
    job_list = []

    # TODO: parse for other pipelines (branches, tags, pull-requests, custom)
    # TODO: parse for definitions and YAML anchors
    for job_def in bbyml["pipelines"]["default"]:
        if "step" in job_def:
            script_list = []

            if "script" in job_def["step"]:
                for line in job_def["step"]["script"]:
                    script_list.append(line)
            image = ""
            if "image" in job_def["step"]:
                image = job_def["step"]["image"]["name"]
            else:
                image = default_image
            job_list.append(
                LocalRunContext(job_def["step"]["name"], image, script_list)
            )

        elif "parallel" in job_def:
            for par_step in job_def["parallel"]:
                script_list = []

                if "script" in par_step["step"]:
                    for line in par_step["step"]["script"]:
                        script_list.append(line)
                image = ""
                if "image" in par_step["step"]:
                    image = par_step["step"]["image"]["name"]
                job_list.append(
                    LocalRunContext(par_step["step"]["name"], image, script_list)
                )

    return job_list
