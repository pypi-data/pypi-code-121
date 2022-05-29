import os
import pathlib
import re
from typing import Set

import build
import pep517
from build import util


def _remove_extras_marker(requirement: str) -> str:
    """Return requirement without any extras markers
    >>> _remove_extras_marker("fire (>=0.4) ; extra == 'cli'")
    'fire (>=0.4)'
    """
    return re.sub(r"\s*;\s*extra\s*==\s*'[^']+'", "", requirement)


def run_requirements(project_dir: pathlib.Path) -> Set[str]:
    return set(
        _remove_extras_marker(requirement)
        for requirement in util.project_wheel_metadata(project_dir).get_all(
            "Requires-Dist"
        )
        or []
    )


def build_dependencies(project_dir: pathlib.Path) -> Set[str]:
    return build.ProjectBuilder(
        os.fspath(project_dir),
        runner=pep517.quiet_subprocess_runner,
    ).build_system_requires
