#!/usr/bin/env python
# encoding: UTF-8

import ast
import os.path

from setuptools import setup


try:
    # Includes bzr revision number
    from turberfield.utils.about import version
except ImportError:
    try:
        # For setup.py install
        from turberfield.utils import __version__ as version
    except ImportError:
        # For pip installations
        version = str(ast.literal_eval(open(os.path.join(
            os.path.dirname(__file__), "turberfield", "utils", "__init__.py"
        ), 'r').read().split("=")[-1].strip()))

__doc__ = open(os.path.join(os.path.dirname(__file__), "README.rst"),
               'r').read()

setup(
    name="turberfield-utils",
    version=version,
    description="Reusable modules from the Turberfield project.",
    author="D Haynes",
    author_email="tundish@thuswise.org",
    url="https://www.assembla.com/spaces/turberfield/messages",
    long_description=__doc__,
    classifiers=[
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.4",
        "License :: OSI Approved :: GNU General Public License v3"
        " or later (GPLv3+)"
    ],
    namespace_packages=["turberfield"],
    packages=[
        "turberfield.utils",
        "turberfield.utils.test",
    ],
    package_data={
        "turberfield.utils": [
            "doc/*.rst",
            "doc/_templates/*.css",
            "doc/html/*.html",
            "doc/html/*.js",
            "doc/html/_sources/*",
            "doc/html/_static/css/*",
            "doc/html/_static/font/*",
            "doc/html/_static/js/*",
            "doc/html/_static/*.css",
            "doc/html/_static/*.gif",
            "doc/html/_static/*.js",
            "doc/html/_static/*.png",
        ],
    },
    install_requires=[],
    tests_require=[],
    entry_points={
        "console_scripts": [],
        "turberfield.utils.states": [
            "visibility = turberfield.utils.db:Visibility",
        ]
    },
    zip_safe=False
)
