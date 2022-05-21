"""Functions for project utility like docs generation, reformatting etc.

This module contains functions that are usually called in pipeline with 'project_utils_pipeline'
from 'project_utils' which you can call with script from terminal and you can use sys args to configure it.

You can use functions separately of course.
"""

from mypythontools_cicd.project_utils.project_utils_functions.project_utils_functions_internal import (
    git_commit_all,
    generate_readme_from_init,
    get_version,
    git_push,
    reformat_with_black,
    set_version,
    docs_regenerate,
)

__all__ = [
    "git_commit_all",
    "generate_readme_from_init",
    "get_version",
    "git_push",
    "reformat_with_black",
    "set_version",
    "docs_regenerate",
]
