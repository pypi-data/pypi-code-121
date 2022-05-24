# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

from setuptools import setup, find_packages
from shapelets.__main__ import __version__

try:  # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError:  # for pip <= 9.0.3
    from pip.req import parse_requirements

with open("README.rst", "r") as handler:
    LONG_DESC = handler.read()

REQUIREMENTS = parse_requirements("requirements.txt", session=False)
try:
    REQUIREMENTS = [str(req.req) for req in REQUIREMENTS]
except:
    REQUIREMENTS = [str(req.requirement) for req in REQUIREMENTS]

setup(
    author="Shapelets.io",
    author_email="info@shapelets.io",
    name="shapelets-solo",
    version=__version__,
    long_description=LONG_DESC,
    description="Python client for Shapelets",
    license="Shapelets-License",
    url="http://shapelets.io",
    packages=find_packages(exclude=["tests", "examples"]),
    package_data={"shapelets": ["dsl/resources/function_impl_tpt.jinja", "shapelets.cfg"]},
    include_package_data=True,
    install_requires=REQUIREMENTS,
    keywords=["time-series platform",
              "time-series analytics",
              "GPU acceleration",
              "Compute Graphs",
              "interactive visualization",
              "Data-Apps"
              ],
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: Microsoft :: Windows",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Visualization"
    ],
)
