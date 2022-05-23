"""
`gl_parser`
=======================================================================
Parser to pull job contexts from .gitlab-ci.yml files
* Author(s): Bailey Steinfadt
"""
import logging
import re
from embedops_cli.yaml_tools import open_yaml
from ..eo_types import LocalRunContext, BadYamlFileException

_logger = logging.getLogger(__name__)

_GITLAB_RESERVED_KEYWORDS = [
    "stages",
    "image",
    "workflow",
    "include",
    "services",
    "types",
    "before_script",
    "after_script",
    "variables",
    "cache",
    "default",
    "artifacts",
    "interruptable",
    "retry",
    "tags",
    "timeout",
]


def get_job_name_list(glyml_filename: str) -> list:
    """Get list of job names from the given YAML object"""

    try:
        glyml = open_yaml(glyml_filename)
    except BadYamlFileException as exc:
        raise BadYamlFileException() from exc

    job_name_list = []

    try:
        for item in glyml.items():
            # reserved GitLab yaml tags
            if item[0] not in _GITLAB_RESERVED_KEYWORDS:
                job_name_list.append(item[0])

        if not all(isinstance(job_name, str) for job_name in job_name_list):
            raise BadYamlFileException()

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
        default_image = ""
        default_var_dict = {}
        for tag, value in glyml.items():
            # default image can be at top level image:,
            # under image:name:, or default:image:
            if tag == "image":
                if "name" in value:
                    default_image = value["name"]
                else:
                    default_image = value
            if tag == "default":
                if "image" in value:
                    default_image = value["image"]
                # update default_var_dict (in case top level vars came first)
                if "variables" in value:
                    default_var_dict.update(value["variables"])

            # update default_var_dict (in case default:variables: came first)
            if tag == "variables":
                default_var_dict.update(value)

            # reserved GitLab yaml tags are the only things that aren't jobs
            if tag not in _GITLAB_RESERVED_KEYWORDS:

                job_ctx = _parse_job_context(
                    tag, value, default_image, default_var_dict
                )

                job_list.append(job_ctx)
        return job_list
    except (TypeError, KeyError, BadYamlFileException) as err:
        raise BadYamlFileException() from err


def _parse_job_context(yaml_tag, yaml_value, default_image, default_var_dict):
    # Image defined in job overrides any default image
    image = ""

    if "image" in yaml_value:
        if "name" in yaml_value["image"]:
            image = yaml_value["image"]["name"]
        else:

            image = yaml_value["image"]
    else:
        image = default_image

    # Does not need to have a script, can be empty
    # TODO: parse before and after scripts
    # TODO: parse the | token appropriately
    script_list = []
    if "script" in yaml_value:
        if isinstance(yaml_value["script"], list):
            for line in yaml_value["script"]:
                script_list.append(line)
        elif isinstance(yaml_value["script"], str):
            script_list = yaml_value["script"].split("\n")
            if script_list[-1] == "":
                # Remove the last empty command
                script_list.pop(-1)
        else:
            raise BadYamlFileException()

    # Does not necessarily have variables
    # if it does, add them (via update()) to the default_var_dict
    var_dict = {}
    var_dict.update(default_var_dict)
    if "variables" in yaml_value:
        dereferenced_job_vars = _dereference_vars(
            yaml_value["variables"], default_var_dict
        )
        var_dict.update(dereferenced_job_vars)
    return LocalRunContext(yaml_tag, image, script_list, var_dict)


def _dereference_vars(raw_vars: dict, global_vars: dict) -> dict:
    dereferenced_vars = {}
    for raw_key in raw_vars.keys():
        dereferenced_value = raw_vars[raw_key]
        for global_key in global_vars.keys():
            just_dollar = rf"\${global_key}"
            dollar_and_braces = rf"\${{{global_key}}}"
            if re.search(just_dollar, raw_vars[raw_key]) is not None:
                dereferenced_value = re.sub(
                    just_dollar, global_vars[global_key], raw_vars[raw_key]
                )
            if re.search(dollar_and_braces, raw_vars[raw_key]) is not None:
                dereferenced_value = re.sub(
                    dollar_and_braces, global_vars[global_key], raw_vars[raw_key]
                )

        dereferenced_vars[raw_key] = dereferenced_value
    return dereferenced_vars
