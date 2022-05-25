#!/usr/bin/env python
from pathlib import Path

from setuptools import setup


def get_version():
    ini_path = Path(__file__).parent / "interlinked" / "__init__.py"
    for line in ini_path.open():
        if line.startswith("__version__"):
            return line.split("=")[1].strip("' \"\n")
    raise ValueError(f"__version__ line not found in {ini_path}")


description = (
    "Interlinked provide routing, dependency management and dependency "
    "injection for data-driven applications"
)
setup(
    name="interlinked",
    version=get_version(),
    description=description,
    long_description=description,
    author="Bertrand Chenal",
    url="https://github.com/bertrandchenal/interlinked",
    license="MIT",
    packages=["interlinked"],
    install_requires=[
    ],
)
