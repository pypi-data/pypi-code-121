# ----------------------------------------------------------------------------
# Description    : The setup script
# Git repository : https://gitlab.com/qblox/packages/software/qblox_instruments.git
# Copyright (C) Qblox BV (2020)
# ----------------------------------------------------------------------------


import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(os.path.abspath(__file__))) + "/qblox_instruments")
from build import __version__ as version

from setuptools import setup, find_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("AUTHORS.rst") as authors_file:
    authors = authors_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: BSD License",
    "Natural Language :: English",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
]

requirements = [
    "numpy",
    "ifaddr",
    "qcodes>=0.20.0",
    "fastjsonschema",
    "spirack"
]

setup_requirements = [
    "setuptools"
]

docs_requirements = [
    "sphinx",
    "sphinx-togglebutton",
    "sphinx-jsonschema",
    "sphinx-rtd-theme",
    "nbsphinx",
    "jupyter_sphinx",
]

test_requirements = [
    "pylint",
    "pylint-exit",
    "anybadge",
    "pytest",
    "pytest-runner",
    "pytest-cov",
    "scipy",
    "twine",
] + docs_requirements  # Docs are also built as a test

packages = [
    "qblox_instruments",
    "qblox_instruments/assemblers",
    "qblox_instruments.cfg_man",
    "qblox_instruments.pnp",
    "qblox_instruments.ieee488_2",
    "qblox_instruments.scpi",
    "qblox_instruments.native",
    "qblox_instruments.native.spi_rack_modules",
    "qblox_instruments.qcodes_drivers",
    "qblox_instruments.qcodes_drivers.spi_rack_modules",
]

package_data = {
    "": [
        "LICENSE",
        "README.rst",
        "AUTHORS.rst",
        "HISTORY.rst"
    ],
    "qblox_instruments": [
        "assemblers/q1asm_linux",
        "assemblers/q1asm_macos",
        "assemblers/q1asm_windows.exe",
    ],
}

entry_points = {
    "console_scripts": [
        "qblox-cfg=qblox_instruments.cfg_man.main:_main",
        "qblox-pnp=qblox_instruments.pnp.main:_main",
    ],
}

setup(
    name="qblox_instruments",
    author="Qblox BV",
    author_email="support@qblox.com",
    license="BSD 4-Clause",
    version=version,
    url="https://gitlab.com/qblox/packages/software/qblox_instruments",
    download_url="https://gitlab.com/qblox/packages/software/qblox_instruments/-/archive/v{0}/qblox_instruments-v{0}.zip".format(version),
    description="Instrument drivers for Qblox devices.",
    long_description=readme + "\n\n" + authors + "\n\n" + history,
    long_description_content_type="text/x-rst",
    keywords=["Qblox", "QCoDeS", "instrument", "driver"],
    classifiers=classifiers,
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={"dev": test_requirements, "docs": docs_requirements},
    include_package_data=True,
    packages=find_packages(include=packages),
    package_data=package_data,
    entry_points=entry_points,
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    zip_safe=False,
)
