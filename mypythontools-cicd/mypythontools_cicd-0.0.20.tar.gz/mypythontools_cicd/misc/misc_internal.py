"""Module with functions for 'misc' subpackage."""

from __future__ import annotations
from typing import Sequence
from pathlib import Path
import os

from typing_extensions import Literal
from mypythontools.paths import validate_path, PathLike

from mypythontools_cicd.project_paths import PROJECT_PATHS


def get_requirements_files(requirements: Literal["infer"] | PathLike | Sequence[PathLike]) -> list[Path]:
    """Consolidate various input types into defined one.

    Args:
        requirements (Literal["infer"] | PathLike | Sequence[PathLike]): E.g. ["requirements.txt",
            "requirements_dev.txt"]. if 'infer', then every file where requirements is in the name is used.

    Returns:
        list[Path]: List of paths to requirements files.
    """

    if requirements == "infer":

        requirements_parsed = []

        for i in PROJECT_PATHS.root.glob("*"):
            if "requirements" in i.as_posix().lower() and i.suffix == ".txt":
                requirements_parsed.append(i)
    else:
        if isinstance(requirements, (Path, str, os.PathLike)):
            requirements = [requirements]

        requirements_parsed = [validate_path(req) for req in requirements]

    return requirements_parsed
