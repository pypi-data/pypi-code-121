#!/usr/bin/env python
# encoding: UTF-8

import ast
import os.path

from setuptools import setup


try:
    # For setup.py install
    from turberfield.dialogue import __version__ as version
except ImportError:
    # For pip installations
    version = str(ast.literal_eval(
        open(os.path.join(
            os.path.dirname(__file__),
            "turberfield", "dialogue", "__init__.py"), "r"
        ).read().split("=")[-1].strip()
    ))

__doc__ = open(os.path.join(os.path.dirname(__file__), "README.rst"),
               'r').read()

setup(
    name="turberfield-dialogue",
    version=version,
    description="Scripting dialogue and soundtrack for your Turberfield project.",
    author="D Haynes",
    author_email="tundish@gigeconomy.org.uk",
    url="https://github.com/tundish/turberfield-dialogue/issues",
    long_description=__doc__,
    classifiers=[
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.4",
        "License :: OSI Approved :: GNU General Public License v3"
        " or later (GPLv3+)"
    ],
    namespace_packages=["turberfield"],
    packages=[
        "turberfield.dialogue",
        "turberfield.dialogue.test",
        "turberfield.dialogue.sequences",
        "turberfield.dialogue.sequences.battle",
        "turberfield.dialogue.sequences.cloak",
    ],
    package_data={
        "turberfield.dialogue": [
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
        "turberfield.dialogue.sequences.battle": [
            "*.rst",
            "*.wav",
        ],
        "turberfield.dialogue.sequences.cloak": [
            "*.rst",
            "*.wav",
        ]
    },
    install_requires=[
        "docutils>=0.17.1",
        "turberfield-utils>=0.46.0",
    ],
    extras_require={
        "dev": [
            "flake8", "wheel"
        ],
        "docbuild": [
            "babel>=2.4.0",
            "sphinx>=1.6.1",
            "sphinx-argparse>=0.2.0",
            "sphinxcontrib-seqdiag>=0.8.5",
            "sphinx_rtd_theme>=1.0.0"
        ],
        "play": [
            "blessings>=1.6",
            "simpleaudio>=1.0.1",
        ],
    },
    tests_require=[],
    entry_points={
        "console_scripts": [
            "turberfield-dialogue = turberfield.dialogue.main:run",
            "turberfield-rehearse = turberfield.dialogue.viewer:run",
        ],
    },
    zip_safe=False
)
