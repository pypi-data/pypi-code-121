"""Subpackage where you can get paths used in your project (path to README,  __init__.py etc.) or configure
paths to be able other modules here in mypythontools_cicd with PROJECT_PATHS.
"""

from mypythontools_cicd.project_paths.project_paths_internal import (
    PROJECT_PATHS,
    ProjectPaths,
)

__all__ = ["PROJECT_PATHS", "ProjectPaths"]
