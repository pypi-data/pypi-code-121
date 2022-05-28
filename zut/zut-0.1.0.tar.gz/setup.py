#!/usr/bin/env python3
import os, shutil
from pathlib import Path
from glob import glob
from setuptools import setup, find_packages, Command

BASE_DIR = Path(__file__).resolve().parent

NAME = "zut"
VERSION = "0.1.0"

class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        globpaths = [
            "build",
            "dist",
            "**/__pycache__",
            "**/*.egg-info",
        ]
        for globpath in globpaths:
            for path in glob(globpath, recursive=True):
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.unlink(path)

class LsoCommand(Command):
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        os.system("git ls-files -o -x .venv")

with open("README.md", "r", encoding="utf-8") as file:
    LONG_DESCRIPTION = file.read()

def get_requirements(path):
    with open(path, "r", encoding="utf-8") as file:
        requirements = []
        for line in file.read().splitlines():
            pos = line.find("#")
            if pos >= 0:
                line = line[0:pos]
            line = line.strip()
            if not line:
                continue
            requirements.append(line)
        return requirements

INSTALL_REQUIREMENTS = get_requirements(BASE_DIR.joinpath("zut/requirements.txt"))

EXTRAS_REQUIREMENTS = {
    "django": get_requirements(BASE_DIR.joinpath("zut/django/requirements.txt")),
    "pgsql": get_requirements(BASE_DIR.joinpath("zut/pgsql/requirements.txt")),
}

if __name__ == "__main__":
    setup(
        name=NAME,
        version=VERSION,
        author="Ipamo",
        author_email="dev@ipamo.net",
        description="Reusable Python, Django and PostgreSql utilities",
        long_description=LONG_DESCRIPTION,
        long_description_content_type="text/markdown",
        url="https://gitlab.com/ipamo/zut",
        project_urls={
            "Bug Tracker": "https://gitlab.com/ipamo/zut/issues",
        },
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
        packages=["zut"] + [f"zut.{pkg}" for pkg in find_packages(where="./zut")],
        package_data={
            "zut.pgsql": ["*.sql"]
        },
        python_requires=">=3.9",
        setup_requires=[
            "setuptools"
        ],
        install_requires=INSTALL_REQUIREMENTS,
        extras_require=EXTRAS_REQUIREMENTS,
        cmdclass={
            'clean': CleanCommand,
            'lso': LsoCommand,
        }
    )
