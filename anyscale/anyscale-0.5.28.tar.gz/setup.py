from __future__ import absolute_import, division, print_function

import os
import re

from setuptools import Distribution, find_packages, setup


# mypy: ignore-errors


def find_version(path):
    with open(path) as f:
        match = re.search(
            r"^__version__ = ['\"]([^'\"]*)['\"]", f.read(), re.MULTILINE,
        )
        if match:
            return match.group(1)
        raise RuntimeError("Unable to find version string.")


def read_requirements(path):
    with open(path) as f:
        return [line.strip() for line in f.readlines()]


class BinaryDistribution(Distribution):
    def is_pure(self):
        return True

    def has_ext_modules(self):
        return True


# If adding new webterminal deps,
# Update backend/server/services/application_templates_service.py
# to prevent users from uninstalling them.
extras_require = {"backend": ["terminado==0.10.1", "tornado"]}


def package_files(directory):
    paths = []
    for (path, _, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join("..", path, filename))
    return paths


VERSION_PATH = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "anyscale", "version.py"
)
REQUIREMENTS_PATH = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "requirements.in"
)

setup(
    name="anyscale",
    version=find_version(VERSION_PATH),
    author="Anyscale Inc.",
    description=("Command Line Interface for Anyscale"),
    packages=[*find_packages(exclude="tests")],
    distclass=BinaryDistribution,
    setup_requires=["setuptools_scm"],
    package_data={
        "": [
            "requirements.in",
            "*.yaml",
            "*.json",
            *package_files("anyscale/client"),
            *package_files("anyscale/sdk"),
        ],
    },
    install_requires=read_requirements(REQUIREMENTS_PATH),
    extras_require=extras_require,
    entry_points={"console_scripts": ["anyscale=anyscale.scripts:main"]},
    include_package_data=True,
    zip_safe=False,
)
