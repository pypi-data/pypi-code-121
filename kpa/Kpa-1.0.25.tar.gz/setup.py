#!/usr/bin/env python3
# to install locally: `pip install -e .`
# to install latest from pypi: `pip3 install --upgrade --upgrade-strategy eager --no-cache-dir kpa`
# to publish: `./setup.py publish`
# to update deps: `kpa pip-find-updates`

from setuptools import setup
import importlib
import sys


def load_module_by_path(module_name, filepath):
    module = importlib.util.module_from_spec(importlib.util.spec_from_file_location(module_name, filepath))
    module.__spec__.loader.exec_module(module)
    return module
version = load_module_by_path('kpa.version', 'kpa/version.py').version


if sys.argv[-1] in ['publish', 'pub']:
    pypi_utils = load_module_by_path('kpa.pypi_utils', 'kpa/pypi_utils.py')
    pypi_utils.upload_package(package_name='Kpa', current_version=version)
    sys.exit(0)


setup(
    name='Kpa',
    version=version,
    description="<forthcoming>",
    author="Peter VandeHaar",
    author_email="pjvandehaar@gmail.com",
    url="https://github.com/pjvandehaar/kpa",
    classifiers=[
        'Programming Language :: Python :: 3 :: Only',
        'Operating System :: Unix',
    ],

    package_data={'kpa': ['py.typed']},  # tells mypy this has types
    packages=['kpa'],
    entry_points={'console_scripts': [
        'kpa=kpa.command_line:main',
    ]},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.4",
    setup_requires=[
        'pytest-runner~=4.2',
    ],
    install_requires=[
        'boltons~=20.2',
    ],
    tests_require=[
        'pytest~=4.0',
    ],
)
