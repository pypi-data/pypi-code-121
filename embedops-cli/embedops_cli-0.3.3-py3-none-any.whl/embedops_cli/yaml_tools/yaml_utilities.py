"""
`yaml_utilities`
=======================================================================
Shared YAML parsing utilities
* Author(s): Bailey Steinfadt and Bryan Siepert
"""

from logging import getLogger
from os import listdir, path
from embedops_cli.yaml_tools import bb_parser, gl_parser, gh_parser

from embedops_cli.eo_types import (
    BadYamlFileException,
    NoYamlFileException,
    UnsupportedYamlTypeException,
    MultipleYamlFilesException,
    LocalRunContext,
    SUPPORTED_CI_FILENAMES,
    GH_CI_CONFIG_FILE_PATH,
    GL_CI_CONFIG_FILENAME,
    BB_CI_CONFIG_FILENAME,
    EO_CI_CONFIG_FILENAME,
)

_logger = getLogger(__name__)


def get_job_context_for_name(
    parser, yml_filename: str, requested_name: str
) -> LocalRunContext:
    """Get job context for requested job name from specified yml object"""

    try:
        for job in parser.get_job_list(yml_filename):
            if job.job_name == requested_name:
                return job
    except BadYamlFileException as exc:
        raise BadYamlFileException() from exc

    # if job was not found, return None
    return None


def get_yaml_in_directory(directory="."):
    """Looks for supported YAML files in the indicated directory"""
    current_dir_files = listdir(directory)
    for dir_file in SUPPORTED_CI_FILENAMES:
        if dir_file in current_dir_files:
            filename = dir_file

            _logger.debug(f"Found YAML: {filename} in directory: {directory}")
            break
    # No CI configuration file is found in the root directory
    # Check for the GitHub CI configuration file in GH_CI_CONFIG_FILE_PATH
    else:
        if not path.isdir(GH_CI_CONFIG_FILE_PATH):
            raise NoYamlFileException()

        files = listdir(GH_CI_CONFIG_FILE_PATH)
        if len(files) != 1:
            raise MultipleYamlFilesException()

        if files[0].lower().endswith(".yaml") or files[0].endswith(".yml"):
            filename = path.join(GH_CI_CONFIG_FILE_PATH, files[0])
            _logger.debug(
                f"\nFound YAML: {files[0]} in directory: {GH_CI_CONFIG_FILE_PATH} \n"
            )
        else:
            raise NoYamlFileException()
    return filename


def get_job_list(filename: str) -> list:
    """Retrieve the job list from the given file using the required parser"""
    try:
        parser = get_correct_parser_type(filename)
    except UnsupportedYamlTypeException as exc:
        raise UnsupportedYamlTypeException() from exc

    try:
        job_list = parser.get_job_list(filename)
        return job_list
    except BadYamlFileException as exc:
        raise BadYamlFileException() from exc


def get_correct_parser_type(filename: str):
    """Get the parser for a given filename"""
    normalized_filename = filename.lower()
    if GL_CI_CONFIG_FILENAME in normalized_filename:
        return gl_parser
    if EO_CI_CONFIG_FILENAME in normalized_filename:
        return gl_parser
    if BB_CI_CONFIG_FILENAME in normalized_filename:
        return bb_parser
    # The name of the GitHub CI configuration file is not fixed
    # but the file must be in the GH_CI_CONFIG_FILE_PATH
    if GH_CI_CONFIG_FILE_PATH in normalized_filename:
        return gh_parser
    raise UnsupportedYamlTypeException()
