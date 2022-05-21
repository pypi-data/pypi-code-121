"""Module with functionality around Continuous Integration and Continuous Delivery.

.. image:: https://img.shields.io/pypi/pyversions/mypythontools_cicd.svg
    :target: https://pypi.python.org/pypi/mypythontools_cicd/
    :alt: Python versions

.. image:: https://badge.fury.io/py/mypythontools_cicd.svg
    :target: https://badge.fury.io/py/mypythontools_cicd
    :alt: PyPI version

.. image:: https://pepy.tech/badge/mypythontools_cicd
    :target: https://pepy.tech/project/mypythontools_cicd
    :alt: Downloads

.. image:: https://img.shields.io/lgtm/grade/python/github/Malachov/mypythontools_cicd.svg
    :target: https://lgtm.com/projects/g/Malachov/mypythontools_cicd/context:python
    :alt: Language grade: Python

.. image:: https://readthedocs.org/projects/mypythontools_cicd/badge/?version=latest
    :target: https://mypythontools_cicd.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
    :target: https://opensource.org/licenses/MIT
    :alt: License: MIT

.. image:: https://codecov.io/gh/Malachov/mypythontools_cicd/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/Malachov/mypythontools_cicd
    :alt: Codecov

Why to use this and not Travis or Circle CI? It's local and it's fast. You can setup it as a task in IDE and
if some phase fails, you know it soon and before pushing to repo.

You can also import mypythontools in your CI/CD and use it there of course.

If you are not sure whether the structure of your app will work with this code, check
`project-starter-cookiecutter` on https://github.com/Malachov/project-starter-cookiecutter

Links
-----

Official documentation - https://mypythontools_cicd.readthedocs.io

Official repo - https://github.com/Malachov/mypythontools_cicd


Installation
------------

Python >=3.6 (Python 2 is not supported).

Install with::

    pip install mypythontools_cicd

Subpackages
-----------
Package is divided into several subpackages

:py:mod:`mypythontools_cicd.build`
----------------------------------
Build your application to .exe with pyinstaller. It also builds javascript frontend with npm build if configured,
which is used mostly in PyVueEel applications.

:py:mod:`mypythontools_cicd.deploy`
-----------------------------------
Build package and push it to PyPi,

:py:mod:`mypythontools_cicd.misc`
---------------------------------
Miscellaneous functions that are too small to have own subpackage.

:py:mod:`mypythontools_cicd.project_utils`
------------------------------------------
Run cicd functions like formatting, testing or deploying.

:py:mod:`mypythontools_cicd.project_paths`
------------------------------------------
Subpackage where you can get paths used in your project (path to README,  __init__.py etc.).

:py:mod:`mypythontools_cicd.tests`
----------------------------------
Runs tests in more venvs with different python versions, also with wsl linux if configured and create coverage.

Mypythontools
==================

There is extra library in separate repository which is not about CICD, but normal python helpers.

https://github.com/Malachov/mypythontools

This can help you with a lot of stuff around CICD like getting project paths, generating docs, testing,
deploying to PyPi etc.

**subpackages**

- config
- misc
- paths
- plots
- property
- terminal
- type_hints
"""
from mypythontools_cicd import build
from mypythontools_cicd import deploy
from mypythontools_cicd import project_paths
from mypythontools_cicd import project_utils
from mypythontools_cicd import tests
from mypythontools_cicd import venvs

__all__ = ["build", "deploy", "project_paths", "project_utils", "tests", "venvs"]

__version__ = "0.0.20"

__author__ = "Daniel Malachov"
__license__ = "MIT"
__email__ = "malachovd@seznam.cz"
