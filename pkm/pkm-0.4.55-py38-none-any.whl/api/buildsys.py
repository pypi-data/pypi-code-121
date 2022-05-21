"""
an implementation of pep517 & pep660 build system
"""

from pathlib import Path

from pkm.api.projects.project import Project

# import sys
# sys.stdout = open(Path("/Users/bennyl/pkm-build.log").resolve(), "w")
# sys.stderr = open(Path("/Users/bennyl/pkm-build-err.log").resolve(), "w")


# noinspection PyUnusedLocal
def build_wheel(wheel_directory: str, config_settings=None, metadata_directory=None):
    return Project.load(Path(".")).build_wheel(Path(wheel_directory)).name


# noinspection PyUnusedLocal
def build_sdist(sdist_directory: str, config_settings=None):
    return Project.load(Path(".")).build_sdist(Path(sdist_directory)).name


# noinspection PyUnusedLocal
def get_requires_for_build_wheel(config_settings=None):
    return []


# noinspection PyUnusedLocal
def prepare_metadata_for_build_wheel(metadata_directory: str, config_settings=None):
    return Project.load(Path(".")).build_wheel(Path(metadata_directory), only_meta=True).name


# noinspection PyUnusedLocal
def get_requires_for_build_sdist(config_settings=None):
    return []


# noinspection PyUnusedLocal
def build_editable(wheel_directory, config_settings=None, metadata_directory=None):
    return Project.load(Path(".")).build_wheel(Path(wheel_directory), editable=True).name


# noinspection PyUnusedLocal
def get_requires_for_build_editable(config_settings=None):
    return []


# noinspection PyUnusedLocal
def prepare_metadata_for_build_editable(metadata_directory, config_settings=None):
    return Project.load(Path(".")).build_wheel(Path(metadata_directory), only_meta=True, editable=True).name
